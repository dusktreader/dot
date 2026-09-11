const DEFAULT_ROUTES = {
  principal: { capability: "tools", tier: "light" },
  "architect-planner": { capability: "analysis", tier: "light" },
  "architect-reviewer": { capability: "analysis", tier: "light" },
  "engineer-planner": { capability: "analysis", tier: "light" },
  "engineer-task-planner": { capability: "analysis", tier: "light" },
  "engineer-investigator": { capability: "analysis", tier: "light" },
  "engineer-executor": { capability: "coding", tier: "light" },
  "engineer-reviewer": { capability: "analysis", tier: "light" },
  build: { capability: "coding", tier: "light" },
  plan: { capability: "analysis", tier: "light" },
  general: { capability: "analysis", tier: "light" },
  explore: { capability: "analysis", tier: "light" },
  title: { capability: "analysis", tier: "light" },
  summary: { capability: "analysis", tier: "light" },
  compaction: { capability: "analysis", tier: "light" }
}

const CAPABILITIES = new Set(["coding", "analysis", "tools", "large-context"])
const TIERS = new Set(["light", "standard", "premium"])

const PRIVATE_ROUTING_OPTIONS = new Set([
  "routing",
  "routingProfile",
  "routingCapability",
  "routingTier",
  "profile",
  "capability",
  "tier",
  "litellmTags"
])

function routeForAgent(agent, configuredAgents = {}) {
  const route = configuredAgents[agent]?.options?.routing
  const capability = route?.capability ?? DEFAULT_ROUTES[agent]?.capability ?? "analysis"
  const configuredTier = route?.tier ?? DEFAULT_ROUTES[agent]?.tier ?? "light"
  if (!CAPABILITIES.has(capability)) {
    throw new Error(`Unsupported routing capability: ${capability}`)
  }
  if (!TIERS.has(configuredTier)) {
    throw new Error(`Unsupported routing tier: ${configuredTier}`)
  }
  return {
    capability,
    tier: selectedTier(configuredTier)
  }
}

function selectedTier(defaultTier) {
  const tier = process.env.OPENCODE_ROUTING_TIER || defaultTier
  if (!TIERS.has(tier)) {
    throw new Error("OPENCODE_ROUTING_TIER must be light, standard, or premium")
  }
  const premiumApproved = process.env.OPENCODE_PREMIUM_APPROVED === "1" ||
    process.env.OPENCODE_CLI_PREMIUM_AUTHORIZED === "1"
  if (tier === "premium" && !premiumApproved) {
    throw new Error("premium routing requires explicit CLI authorization or automated approval")
  }
  return tier
}

function profileTag() {
  const profile = process.env.OPENCODE_ROUTING_PROFILE
  if (profile !== "profile:personal" && profile !== "profile:work") {
    throw new Error("OPENCODE_ROUTING_PROFILE must be profile:personal or profile:work")
  }
  return profile
}

export function routingTags(agent, configuredAgents = {}) {
  const route = routeForAgent(agent || "principal", configuredAgents)
  return [`&${profileTag()}`, `&capability:${route.capability}`, `&tier:${route.tier}`]
}

export function stripPrivateRoutingOptions(options) {
  for (const key of PRIVATE_ROUTING_OPTIONS) delete options[key]
  return options
}

export default async function RouterMetadataPlugin() {
  let configuredAgents = {}
  return {
    config(config) {
      configuredAgents = config.agent ?? {}
    },
    "chat.headers": async (input, output) => {
      output.headers["x-litellm-tags"] = routingTags(input.agent, configuredAgents).join(",")
    },
    "chat.params": async (_input, output) => {
      stripPrivateRoutingOptions(output.options)
    }
  }
}
