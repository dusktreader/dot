import path from "path"
import os from "os"

const SCRIPT = path.join(os.homedir(), ".config", "opencode", "tools", "gmail_cleanup.py")

export const analyze = {
  description:
    "Scan the Gmail inbox and classify emails as junk, personal, or uncertain. " +
    "Saves results to a local analysis file for review. Run this first before executing any cleanup.",
  args: {
    max_results: {
      type: "number",
      default: 1000,
      description: "Maximum number of inbox emails to analyze",
    },
  },
  async execute(args, _context) {
    try {
      const maxResults = args.max_results ?? 1000
      const result = await Bun.$`python3 ${SCRIPT} analyze --max ${maxResults}`.text()
      return result.trim()
    } catch (err: any) {
      const stderr = err?.stderr?.toString?.() ?? String(err)
      return `Gmail analyze failed: ${stderr}`
    }
  },
}

export const report = {
  description:
    "Print a summary report of the last Gmail inbox analysis, grouped by sender. " +
    "Shows junk senders and uncertain emails that need judgment. Run analyze first.",
  args: {},
  async execute(_args, _context) {
    try {
      const result = await Bun.$`python3 ${SCRIPT} report`.text()
      return result.trim()
    } catch (err: any) {
      const stderr = err?.stderr?.toString?.() ?? String(err)
      return `Gmail report failed: ${stderr}`
    }
  },
}

export const execute = {
  description:
    "Unsubscribe and trash emails from approved senders based on the last analysis. " +
    "Use approve_all_junk to process all detected junk, or pass specific sender domains. " +
    "Personal emails are never touched. Always run analyze + report before this.",
  args: {
    approve_all_junk: {
      type: "boolean",
      default: false,
      description: "If true, trash and unsubscribe all senders classified as junk",
    },
    approve_senders: {
      type: "string",
      default: "",
      description: "Comma-separated list of specific junk sender domains to approve (e.g. 'mailchimp.com,sendgrid.net')",
    },
    approve_uncertain: {
      type: "string",
      default: "",
      description: "Comma-separated list of uncertain sender domains to treat as junk and trash",
    },
  },
  async execute(args, _context) {
    try {
      const cmdArgs = ["python3", SCRIPT, "execute"]

      if (args.approve_all_junk) {
        cmdArgs.push("--approve-all-junk")
      }
      if (args.approve_senders) {
        cmdArgs.push("--approve", args.approve_senders)
      }
      if (args.approve_uncertain) {
        cmdArgs.push("--approve-uncertain", args.approve_uncertain)
      }

      const result = await Bun.$`${cmdArgs}`.text()
      return result.trim()
    } catch (err: any) {
      const stderr = err?.stderr?.toString?.() ?? String(err)
      return `Gmail execute failed: ${stderr}`
    }
  },
}
