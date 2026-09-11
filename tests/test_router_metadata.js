import assert from "node:assert/strict"
import test from "node:test"

import { routingTags, stripPrivateRoutingOptions } from "../.config/opencode/plugins/router-metadata.js"

test("routingTags emits profile, capability, and tier tags", () => {
  process.env.OPENCODE_ROUTING_PROFILE = "profile:personal"
  delete process.env.OPENCODE_ROUTING_TIER
  assert.deepEqual(routingTags("engineer-executor"), [
    "&profile:personal",
    "&capability:coding",
    "&tier:light"
  ])
})

test("routingTags uses a validated explicit standard tier", () => {
  process.env.OPENCODE_ROUTING_PROFILE = "profile:work"
  process.env.OPENCODE_ROUTING_TIER = "standard"
  assert.deepEqual(routingTags("unknown-agent"), [
    "&profile:work",
    "&capability:analysis",
    "&tier:standard"
  ])
  delete process.env.OPENCODE_ROUTING_TIER
})

test("routingTags defaults unknown agents to light and rejects invalid tiers", () => {
  process.env.OPENCODE_ROUTING_PROFILE = "profile:personal"
  delete process.env.OPENCODE_ROUTING_TIER
  assert.deepEqual(routingTags("unknown-agent"), [
    "&profile:personal",
    "&capability:analysis",
    "&tier:light"
  ])
  process.env.OPENCODE_ROUTING_TIER = "invalid"
  assert.throws(() => routingTags("unknown-agent"), /light, standard, or premium/)
  delete process.env.OPENCODE_ROUTING_TIER
})

test("routingTags keeps premium behind explicit approval", () => {
  process.env.OPENCODE_ROUTING_PROFILE = "profile:personal"
  process.env.OPENCODE_ROUTING_TIER = "premium"
  delete process.env.OPENCODE_PREMIUM_APPROVED
  assert.throws(() => routingTags("engineer-executor"), /explicit CLI authorization or automated approval/)
  process.env.OPENCODE_PREMIUM_APPROVED = "1"
  assert.deepEqual(routingTags("engineer-executor"), [
    "&profile:personal",
    "&capability:coding",
    "&tier:premium"
  ])
  delete process.env.OPENCODE_ROUTING_TIER
  delete process.env.OPENCODE_PREMIUM_APPROVED
})

test("routingTags accepts explicit CLI premium authorization", () => {
  process.env.OPENCODE_ROUTING_PROFILE = "profile:personal"
  process.env.OPENCODE_ROUTING_TIER = "premium"
  process.env.OPENCODE_CLI_PREMIUM_AUTHORIZED = "1"
  delete process.env.OPENCODE_PREMIUM_APPROVED
  assert.deepEqual(routingTags("engineer-executor"), [
    "&profile:personal",
    "&capability:coding",
    "&tier:premium"
  ])
  delete process.env.OPENCODE_ROUTING_TIER
  delete process.env.OPENCODE_CLI_PREMIUM_AUTHORIZED
})

test("routingTags rejects invalid configured route metadata", () => {
  process.env.OPENCODE_ROUTING_PROFILE = "profile:personal"
  delete process.env.OPENCODE_ROUTING_TIER
  assert.throws(
    () => routingTags("custom", { custom: { options: { routing: { capability: "analysis", tier: "opus" } } } }),
    /Unsupported routing tier: opus/
  )
})

test("routingTags rejects invalid configured capability metadata", () => {
  process.env.OPENCODE_ROUTING_PROFILE = "profile:personal"
  delete process.env.OPENCODE_ROUTING_TIER
  assert.throws(
    () => routingTags("custom", { custom: { options: { routing: { capability: "writing", tier: "light" } } } }),
    /Unsupported routing capability: writing/
  )
})

test("routingTags rejects an unset or invalid profile", () => {
  process.env.OPENCODE_ROUTING_PROFILE = "profile:invalid"
  assert.throws(() => routingTags("principal"), /profile:personal or profile:work/)
})

test("stripPrivateRoutingOptions removes private routing parameters", () => {
  const options = { routingTier: "premium", temperature: 0.2, profile: "work" }
  assert.deepEqual(stripPrivateRoutingOptions(options), { temperature: 0.2 })
})
