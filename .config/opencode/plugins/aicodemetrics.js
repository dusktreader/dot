// aicodemetrics opencode plugin — do not edit (managed by aicodemetricsd)
import { spawn } from "node:child_process";
import { homedir } from "node:os";
import { isAbsolute, resolve } from "node:path";

const BINARY_PATH = "/usr/local/bin/aicodemetricsd";

// Tools that only read or search a file, or track session state. Their calls are
// not reported; every other tool's calls are.
const IGNORED_TOOLS = new Set([
  "read",
  "list",
  "glob",
  "grep",
  "lsp",
  "webfetch",
  "websearch",
  "skill",
  "todowrite",
  "todoread",
  "task",
  "question",
  "plan_exit",
  "invalid",
]);

function isReportedTool(tool) {
  return typeof tool === "string" && !IGNORED_TOOLS.has(tool.toLowerCase());
}

// On Windows, OpenCode uses FSUtil.normalizePath(path.resolve(root,
// FSUtil.windowsPath(text))) and routes /-prefixed workdirs through cygpath for
// POSIX shells. Plain path.resolve here can report a different shell cwd.
function toolDirectory(tool, args, directory) {
  if (tool?.toLowerCase() !== "bash" && tool?.toLowerCase() !== "shell")
    return directory;
  const workdir = args?.workdir;
  if (typeof workdir !== "string" || !workdir) return directory;
  const home = homeWorkdir(workdir);
  if (home) return home;
  if (isAbsolute(workdir)) return resolve(workdir);
  return directory ? resolve(directory, workdir) : directory;
}

// OpenCode 2.x expands ~, ~/ and, on Windows, ~\ in a shell workdir
// (core/src/file-access.ts). 1.x does not, and its spawn then fails, so the
// command changes nothing either way.
function homeWorkdir(workdir) {
  if (workdir === "~") return homedir();
  if (workdir.startsWith("~/") || (process.platform === "win32" && workdir.startsWith("~\\")))
    return resolve(homedir(), workdir.slice(2));
  return "";
}

// Cap on cached sessions, so a long-running server does not accumulate entries.
const MAX_TRACKED_SESSIONS = 256;

// Session metadata filled in from the event stream so a tool call usually does
// not have to look up its session. The known flags distinguish a resolved empty
// value from a value not yet observed; the lifecycle flags prevent duplicate V2
// reports when both current and compatibility events describe one transition.
const sessionCache = new Map();

// In-flight lookups and lifecycle reports, plus per-session event ordering.
const pendingV1Lookups = new Map();
const pendingV2Lookups = new Map();
const pendingV2Starts = new Map();
const pendingV2Ends = new Map();
const pendingV2Events = new Map();

// Merges the supplied fields into a session's entry. Empty values never
// overwrite a value already recorded.
function cacheSessionData(sessionID, fields) {
  if (!sessionID) return;
  const entry = sessionCache.get(sessionID) ?? {
    version: "",
    model: "",
    versionKnown: false,
    modelKnown: false,
    startReported: false,
    terminalEndReported: false,
    executionEventsSeen: false,
    messages: [],
  };
  if (fields.version) entry.version = fields.version;
  if (fields.model) entry.model = fields.model;
  if (fields.versionKnown) entry.versionKnown = true;
  if (fields.modelKnown) entry.modelKnown = true;
  if (typeof fields.startReported === "boolean")
    entry.startReported = fields.startReported;
  if (typeof fields.terminalEndReported === "boolean")
    entry.terminalEndReported = fields.terminalEndReported;
  if (fields.executionEventsSeen) entry.executionEventsSeen = true;
  if (Array.isArray(fields.messages))
    entry.messages = mergeV2Messages(entry.messages, fields.messages);
  // Re-insert so the eviction below drops the least recently updated session.
  sessionCache.delete(sessionID);
  sessionCache.set(sessionID, entry);
  while (sessionCache.size > MAX_TRACKED_SESSIONS) {
    const coldest = sessionCache.keys().next();
    if (coldest.done) break;
    sessionCache.delete(coldest.value);
  }
}

// Cap on how long a hook send waits for delivery.
const HOOK_TIMEOUT_MS = 3000;
// Total time execute.before waits for lookup, session start, and pre report.
const BEFORE_DELIVERY_BUDGET_MS = 3000;
// Bound SDK calls too: the hook timeout only starts after a payload is ready.
const V2_LOOKUP_TIMEOUT_MS = 3000;
// A queued start and end can take up to 21s across bounded lookups and sends.
const V2_DRAIN_TIMEOUT_MS = 30000;
// The iterator may ignore abort even after all queued reports have settled.
const V2_ITERATOR_TIMEOUT_MS = 1000;

async function v2Lookup(call) {
  let timer;
  try {
    return await Promise.race([
      Promise.resolve().then(call),
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error("V2 lookup timed out")), V2_LOOKUP_TIMEOUT_MS);
        timer.unref?.();
      }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}

async function waitForV2Cleanup(promise, timeoutMs) {
  let timer;
  try {
    await Promise.race([
      promise,
      new Promise((resolve) => { timer = setTimeout(resolve, timeoutMs); }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}

// Sends a payload and resolves once delivery finishes, times out, or cannot be
// started. Never rejects, so an ignored result cannot raise an unhandled
// rejection. Callers that need delivery to finish before the work they precede
// await the result; the rest let it run on its own.
function sendToHook(payload) {
  return new Promise((resolve) => {
    let child;
    try {
      child = spawn(
        BINARY_PATH,
        ["hook", "opencode", "--hook-input", "stdin"],
        {
          stdio: ["pipe", "ignore", "ignore"],
        },
      );
    } catch {
      // Ignore errors so telemetry never disrupts the user's session.
      resolve();
      return;
    }
    // The first of exit / error / timeout resolves; the rest are no-ops.
    const timer = setTimeout(() => resolve(), HOOK_TIMEOUT_MS);
    timer.unref?.(); // do not hold the event loop open
    const finish = () => {
      clearTimeout(timer);
      resolve();
    };
    child.on("exit", finish);
    child.on("error", finish);
    child.stdin.on("error", () => {});
    child.stdin.end(payload);
  });
}

// Returns the tool version and model recorded for a session. A resolved version
// comes from the cache; otherwise one lookup supplies it and is cached even
// when it fails, so a session costs at most one request. The model stays empty
// until the session's first assistant message arrives.
async function getV1SessionData(client, sessionID) {
  if (!sessionID) return { version: "", model: "" };

  const cached = sessionCache.get(sessionID);
  if (cached?.versionKnown) {
    return { version: cached.version, model: cached.model };
  }

  let lookup = pendingV1Lookups.get(sessionID);
  if (!lookup) {
    lookup = client.session
      .get({ path: { id: sessionID } })
      .then((resp) => resp?.data?.version ?? "")
      .catch(() => "")
      .finally(() => pendingV1Lookups.delete(sessionID));
    pendingV1Lookups.set(sessionID, lookup);
  }

  const version = await lookup;
  cacheSessionData(sessionID, { version, versionKnown: true });
  const entry = sessionCache.get(sessionID);
  return { version: entry?.version ?? version, model: entry?.model ?? "" };
}

function v2ModelID(model) {
  if (typeof model === "string") return model;
  return typeof model?.id === "string" ? model.id : "";
}

function v2Version(ctx) {
  return typeof ctx?.app?.version === "string" ? ctx.app.version : "";
}

async function getV2SessionData(ctx, sessionID) {
  if (!sessionID) return { version: v2Version(ctx), model: "" };

  const cached = sessionCache.get(sessionID);
  if (cached?.versionKnown && cached?.modelKnown) {
    return { version: cached.version, model: cached.model };
  }

  let lookup = pendingV2Lookups.get(sessionID);
  if (!lookup) {
    lookup = v2Lookup(() => ctx.session.get({ sessionID }))
      .then((session) => ({
        version: v2Version(ctx),
        model: v2ModelID(session?.model),
      }))
      .catch(() => ({ version: v2Version(ctx), model: "" }))
      .finally(() => pendingV2Lookups.delete(sessionID));
    pendingV2Lookups.set(sessionID, lookup);
  }

  const data = await lookup;
  cacheSessionData(sessionID, {
    ...data,
    versionKnown: true,
    modelKnown: Boolean(data.model),
  });
  const entry = sessionCache.get(sessionID);
  return {
    version: entry?.version ?? data.version,
    model: entry?.model ?? data.model,
  };
}

function v2Directory(ctx, session) {
  return session?.location?.directory ?? ctx?.location?.directory ?? "";
}

function normalizeV2Session(ctx, session) {
  return {
    id: session?.id,
    parentID: session?.parentID,
    title: session?.title,
    version: v2Version(ctx),
    directory: v2Directory(ctx, session),
    time: session?.time,
  };
}

function normalizeV2Messages(messages) {
  if (!Array.isArray(messages)) return [];

  const normalized = [];
  for (const message of messages) {
    if (message?.type === "user") {
      normalized.push({
        info: {
          id: message.id,
          role: "user",
          time: message.time,
        },
        parts: [{ type: "text", text: message.text ?? "" }],
      });
      continue;
    }

    if (message?.type !== "assistant") continue;
    normalized.push({
      info: {
        id: message.id,
        role: "assistant",
        time: message.time,
        modelID: v2ModelID(message.model),
        providerID: message.model?.providerID ?? "",
        tokens: message.tokens,
      },
      parts: Array.isArray(message.content)
        ? message.content
            .filter((part) => part?.type === "text")
            .map((part) => ({ type: "text", text: part.text ?? "" }))
        : [],
    });
  }
  return normalized;
}

function mergeV2Messages(cached, current) {
  const merged = Array.isArray(cached) ? [...cached] : [];
  const positions = new Map();
  for (let index = 0; index < merged.length; index++) {
    const id = merged[index]?.info?.id;
    if (id) positions.set(id, index);
  }
  for (const message of current) {
    const id = message?.info?.id;
    const index = id ? positions.get(id) : undefined;
    if (index === undefined) {
      if (id) positions.set(id, merged.length);
      merged.push(message);
    } else {
      merged[index] = message;
    }
  }
  return merged;
}

async function getV2Transcript(ctx, sessionID) {
  cacheSessionData(sessionID, {});
  const entry = sessionCache.get(sessionID);
  let timedOut = false;
  try {
    await v2Lookup(() => Promise.resolve(ctx.session.context({ sessionID })).then((messages) => {
      // Retain snapshots even if the queue stopped waiting before they arrived.
      // Deletion or eviction invalidates this entry, including after ID reuse.
      if (sessionCache.get(sessionID) !== entry) return;
      const current = normalizeV2Messages(messages);
      if (timedOut) {
        // A late pre-compaction window precedes the cached window. Prefer the
        // newer cached version of any message present in both snapshots.
        entry.messages = mergeV2Messages(current, entry.messages);
        cacheSessionData(sessionID, {});
      } else {
        cacheSessionData(sessionID, { messages: current });
      }
    }));
    return { messages: entry.messages, fresh: true };
  } catch {
    timedOut = true;
    return { messages: entry.messages, fresh: false };
  }
}

async function reportV2Session(ctx, sessionID, lifecycle) {
  if (!sessionID) return false;
  try {
    let session;
    try {
      session = await v2Lookup(() => ctx.session.get({ sessionID }));
    } catch (error) {
      if (lifecycle !== "end") throw error;
      // Retry the terminal event in its queue, before a newer turn can start.
      session = await v2Lookup(() => ctx.session.get({ sessionID }));
    }
    if (!session) return false;

    const model = v2ModelID(session.model);
    cacheSessionData(sessionID, {
      version: v2Version(ctx),
      versionKnown: true,
      model,
      modelKnown: Boolean(model),
    });
    if (session.parentID) return false;

    const normalizedSession = normalizeV2Session(ctx, session);
    const payload = {
      event_type: "session",
      lifecycle,
      session: normalizedSession,
      directory: normalizedSession.directory,
    };
    let fresh = true;
    if (lifecycle !== "start") {
      let transcript = await getV2Transcript(ctx, sessionID);
      if (!transcript.fresh) {
        // A transient context failure can be the final event of the session.
        transcript = await getV2Transcript(ctx, sessionID);
      }
      payload.messages = transcript.messages;
      fresh = transcript.fresh;
      // The parser ignores empty transcripts. Leave the end retryable instead
      // of marking it delivered when there is nothing it can record.
      if (!payload.messages?.length) return false;
    }
    await sendToHook(JSON.stringify(payload));
    return fresh;
  } catch {
    // Ignore errors so telemetry never disrupts the user's session.
    return false;
  }
}

// A start attempt waits at most V2_LOOKUP_TIMEOUT_MS plus HOOK_TIMEOUT_MS;
// dependent reports then proceed. execute.before has a separate total wait
// budget for lookup, start, and pre; its delivery chain continues in order
// after that budget expires.
async function ensureV2SessionStart(ctx, sessionID) {
  if (!sessionID || sessionCache.get(sessionID)?.startReported) return;
  let pending = pendingV2Starts.get(sessionID);
  if (!pending) {
    pending = reportV2Session(ctx, sessionID, "start")
      .then((reported) => {
        // A sent start counts even after a hook timeout. A failed session
        // lookup remains retryable by later events.
        if (reported && pendingV2Starts.get(sessionID) === pending) {
          cacheSessionData(sessionID, { startReported: true });
        }
      })
      .finally(() => {
        if (pendingV2Starts.get(sessionID) === pending) {
          pendingV2Starts.delete(sessionID);
        }
      });
    pendingV2Starts.set(sessionID, pending);
  }
  await pending;
}

async function reportV2SessionEnd(ctx, sessionID) {
  if (!sessionID || sessionCache.get(sessionID)?.terminalEndReported) return;
  let pending = pendingV2Ends.get(sessionID);
  if (!pending) {
    pending = (async () => {
      await ensureV2SessionStart(ctx, sessionID);
      if (
        (await reportV2Session(ctx, sessionID, "end")) &&
        pendingV2Ends.get(sessionID) === pending
      ) {
        cacheSessionData(sessionID, { terminalEndReported: true });
      }
    })().finally(() => {
      if (pendingV2Ends.get(sessionID) === pending) {
        pendingV2Ends.delete(sessionID);
      }
    });
    pendingV2Ends.set(sessionID, pending);
  }
  await pending;
}

async function handleV2Event(ctx, event) {
  const data = event?.data;

  if (event?.type === "session.deleted") {
    if (data?.sessionID) {
      sessionCache.delete(data.sessionID);
      pendingV2Lookups.delete(data.sessionID);
      pendingV2Starts.delete(data.sessionID);
      pendingV2Ends.delete(data.sessionID);
    }
    return;
  }

  if (event?.type === "session.model.selected") {
    cacheSessionData(data?.sessionID, {
      model: v2ModelID(data?.model),
      modelKnown: true,
    });
    return;
  }

  if (event?.type === "session.step.started") {
    const model = v2ModelID(data?.model);
    cacheSessionData(data?.sessionID, {
      model,
      modelKnown: Boolean(model),
    });
    return;
  }

  if (event?.type === "session.created") {
    const model = v2ModelID(data?.model);
    cacheSessionData(data?.sessionID, {
      version: v2Version(ctx),
      versionKnown: true,
      model,
      modelKnown: Boolean(model),
    });
    await ensureV2SessionStart(ctx, data?.sessionID);
    return;
  }

  if (event?.type === "session.execution.started") {
    cacheSessionData(data?.sessionID, { terminalEndReported: false, executionEventsSeen: true });
    pendingV2Ends.delete(data?.sessionID);
    await ensureV2SessionStart(ctx, data?.sessionID);
    return;
  }

  if (
    event?.type === "session.execution.succeeded" ||
    event?.type === "session.execution.failed" ||
    event?.type === "session.execution.interrupted"
  ) {
    cacheSessionData(data?.sessionID, { executionEventsSeen: true });
    await reportV2SessionEnd(ctx, data?.sessionID);
    return;
  }

  if (event?.type === "session.idle") {
    // The compatibility idle carries no execution identity. Once execution
    // events appear, only their terminal events can end a turn; a late idle
    // could otherwise consume the next turn's end. On idle-only runtimes,
    // each idle is a separate turn end.
    if (sessionCache.get(data?.sessionID)?.executionEventsSeen) return;
    cacheSessionData(data?.sessionID, { terminalEndReported: false });
    await reportV2SessionEnd(ctx, data?.sessionID);
    return;
  }

  if (event?.type === "session.compaction.started") {
    // Once compaction completes, ctx.session.context() starts at the new
    // boundary. Preserve the current window before that boundary advances.
    await getV2Transcript(ctx, data?.sessionID);
    return;
  }

  if (event?.type === "session.compaction.ended") {
    await ensureV2SessionStart(ctx, data?.sessionID);
    await reportV2Session(ctx, data?.sessionID, "compact");
  }
}

async function consumeV2Events(ctx, signal, tasks) {
  try {
    for await (const event of ctx.event.subscribe({ signal })) {
      if (signal.aborted) break;
      const sessionID = event?.data?.sessionID;
      const previous = pendingV2Events.get(sessionID) ?? Promise.resolve();
      const task = previous
        .then(() => handleV2Event(ctx, event))
        .catch(() => {
          // Malformed telemetry must not stop this or another session.
        })
        .finally(() => {
          tasks.delete(task);
          if (pendingV2Events.get(sessionID) === task) pendingV2Events.delete(sessionID);
        });
      tasks.add(task);
      if (sessionID) pendingV2Events.set(sessionID, task);
    }
  } catch {
    // Subscription errors must not disrupt the OpenCode server.
  }
}

function createV1Hooks({ client, directory }) {
  return {
    event: async ({ event }) => {
      // An assistant message carries the model that runs the turn's tool calls.
      if (event.type === "message.updated") {
        const info = event.properties?.info;
        if (info?.role === "assistant") {
          cacheSessionData(info.sessionID, {
            model: info.modelID,
            modelKnown: true,
          });
        }
        return;
      }

      if (event.type === "session.deleted") {
        const deletedID =
          event.properties?.info?.id ?? event.properties?.sessionID;
        if (deletedID) sessionCache.delete(deletedID);
        return;
      }

      if (event.type === "session.created") {
        // The event usually carries the whole session; fetch it if not.
        let session = event.properties?.info;
        const sessionID = session?.id ?? event.properties?.sessionID;
        if (!sessionID) return;
        try {
          if (!session) {
            const sessionResp = await client.session.get({
              path: { id: sessionID },
            });
            session = sessionResp?.data;
          }
          if (!session) return;
          // Cache before the parent check: child sessions run tools too.
          cacheSessionData(sessionID, {
            version: session.version,
            versionKnown: true,
          });
          if (session.parentID) return;
          sendToHook(
            JSON.stringify({
              event_type: "session",
              lifecycle: "start",
              session,
              directory,
            }),
          );
        } catch {
          // Ignore errors so telemetry never disrupts the user's session.
        }
        return;
      }

      if (event.type !== "session.idle" && event.type !== "session.compacted")
        return;
      const sessionID = event.properties?.sessionID;
      if (!sessionID) return;

      try {
        const sessionResp = await client.session.get({
          path: { id: sessionID },
        });
        const session = sessionResp?.data;
        if (!session) return;
        cacheSessionData(sessionID, {
          version: session.version,
          versionKnown: true,
        });
        if (session.parentID) return;

        const messagesResp = await client.session.messages({
          path: { id: sessionID },
        });
        const messages = messagesResp?.data ?? [];

        const lifecycle =
          event.type === "session.compacted" ? "compact" : "end";

        sendToHook(
          JSON.stringify({
            event_type: "session",
            lifecycle,
            session,
            messages,
            directory,
          }),
        );
      } catch {
        // Ignore errors so telemetry never disrupts the user's session.
      }
    },

    // Reports the state a tool is about to change, so delivery has to finish
    // before the tool runs.
    "tool.execute.before": async (input, output) => {
      if (!isReportedTool(input?.tool)) return;
      const sessionID = input?.sessionID;
      const data = await getV1SessionData(client, sessionID);
      await sendToHook(
        JSON.stringify({
          event_type: "tool",
          phase: "pre",
          tool: input?.tool,
          session_id: sessionID,
          call_id: input?.callID,
          tool_version: data.version,
          model: data.model,
          args: output?.args,
          directory: toolDirectory(input?.tool, output?.args, directory),
        }),
      );
    },

    // Reports the state a tool has already produced, so nothing waits on it.
    "tool.execute.after": async (input) => {
      if (!isReportedTool(input?.tool)) return;
      const sessionID = input?.sessionID;
      const data = await getV1SessionData(client, sessionID);
      sendToHook(
        JSON.stringify({
          event_type: "tool",
          phase: "post",
          tool: input?.tool,
          session_id: sessionID,
          call_id: input?.callID,
          tool_version: data.version,
          model: data.model,
          args: input?.args,
          directory: toolDirectory(input?.tool, input?.args, directory),
        }),
      );
    },
  };
}

async function setupV2(ctx) {
  const beforeRegistration = await ctx.tool.hook(
    "execute.before",
    async (event) => {
      if (!isReportedTool(event?.tool)) return;
      let timer;
      const timeout = new Promise((resolve) => {
        timer = setTimeout(resolve, BEFORE_DELIVERY_BUDGET_MS);
        timer.unref?.();
      });
      const delivery = (async () => {
        try {
          const data = await getV2SessionData(ctx, event?.sessionID);
          await ensureV2SessionStart(ctx, event?.sessionID);
          await sendToHook(
            JSON.stringify({
              event_type: "tool",
              phase: "pre",
              tool: event?.tool,
              session_id: event?.sessionID,
              call_id: event?.id,
              tool_version: data.version,
              model: data.model,
              args: event?.input,
              directory: toolDirectory(event?.tool, event?.input, ctx.location?.directory ?? ""),
            }),
          );
        } catch {
          // Telemetry must not interrupt the tool call.
        }
      })();
      try {
        await Promise.race([delivery, timeout]);
      } finally {
        clearTimeout(timer);
      }
    },
  );

  const afterRegistration = await ctx.tool.hook(
    "execute.after",
    async (event) => {
      if (!isReportedTool(event?.tool)) return;
      try {
        const data = await getV2SessionData(ctx, event?.sessionID);
        const payload = JSON.stringify({
          event_type: "tool",
          phase: "post",
          tool: event?.tool,
          session_id: event?.sessionID,
          call_id: event?.id,
          tool_version: data.version,
          model: data.model,
          args: event?.input,
          directory: toolDirectory(event?.tool, event?.input, ctx.location?.directory ?? ""),
        });
        ensureV2SessionStart(ctx, event?.sessionID)
          .then(() => sendToHook(payload))
          .catch(() => {});
      } catch {
        // Telemetry must not interrupt the tool call.
      }
    },
  );

  const eventController = new AbortController();
  const eventTasks = new Set();
  const eventTask = consumeV2Events(ctx, eventController.signal, eventTasks);

  return async () => {
    eventController.abort();
    const disposals = Promise.allSettled([
      Promise.resolve().then(() => beforeRegistration.dispose()),
      Promise.resolve().then(() => afterRegistration.dispose()),
    ]);
    const queued = Promise.allSettled([...eventTasks]);
    const stopped = eventTask.catch(() => {});
    await waitForV2Cleanup(Promise.all([disposals, queued]), V2_DRAIN_TIMEOUT_MS);
    await waitForV2Cleanup(stopped, V2_ITERATOR_TIMEOUT_MS);
  };
}

export default {
  id: "aicodemetrics",
  setup: setupV2,
  async server(input) {
    return createV1Hooks(input);
  },
};
