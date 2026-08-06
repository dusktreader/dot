import { spawnSync } from "node:child_process"

/**
 * Bridge OpenCode tool events to the dependency-free dt staleness-guard commands.
 * The state lives in dt rather than in this plugin because OpenCode loads plugins
 * in a dependency installation path that is not reliable for user-owned config.
 */
export const StalenessGuard = async () => {
  function run(command, paths) {
    const result = spawnSync("dt", ["opencode", "staleness-guard", command, ...paths], {
      encoding: "utf8",
    })
    if (result.error) throw result.error
    if (result.status !== 0) {
      throw new Error((result.stderr || result.stdout || `dt exited with ${result.status}`).trim())
    }
  }

  function extractPaths(tool, args = {}) {
    if (tool === "apply_patch" && typeof args.patchText === "string") {
      const paths = []
      const pattern = /^\*\*\* (?:Update|Add|Move to|Delete) File: (.+)$/gm
      let match
      while ((match = pattern.exec(args.patchText)) !== null) paths.push(match[1])
      return paths
    }
    return typeof args.filePath === "string" ? [args.filePath] : []
  }

  return {
    "tool.execute.after": async (input) => {
      if (input.tool === "read" && input.args?.filePath) run("read", [input.args.filePath])
    },

    "tool.execute.before": async (input, output) => {
      if (!["edit", "write", "apply_patch"].includes(input.tool)) return
      const paths = extractPaths(input.tool, output.args)
      if (paths.length > 0) run("check", paths)
    },
  }
}
