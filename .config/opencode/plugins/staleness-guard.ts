import type { Plugin } from "@opencode-ai/plugin"
import { statSync } from "fs"

/**
 * Prevents the agent from editing a file that has changed on disk since it was
 * last read.  Tracks mtime on every `read`, and checks it before every `edit`,
 * `write`, or `apply_patch`.  Throws if the file is stale, forcing a re-read.
 */
export const StalenessGuard: Plugin = async () => {
  // Map of absolute file path -> mtime (epoch ms) at last read
  const readTimestamps = new Map<string, number>()

  function getMtime(filePath: string): number | undefined {
    try {
      return statSync(filePath).mtimeMs
    } catch {
      return undefined
    }
  }

  function extractPaths(tool: string, args: Record<string, any>): string[] {
    if (tool === "apply_patch" && typeof args.patchText === "string") {
      const paths: string[] = []
      const re = /^\*\*\* (?:Update|Add|Move to|Delete) File: (.+)$/gm
      let match
      while ((match = re.exec(args.patchText)) !== null) {
        paths.push(match[1])
      }
      return paths
    }
    if (args.filePath) return [args.filePath]
    return []
  }

  return {
    "tool.execute.after": async (input, _output) => {
      if (input.tool === "read" && input.args.filePath) {
        const mtime = getMtime(input.args.filePath)
        if (mtime !== undefined) {
          readTimestamps.set(input.args.filePath, mtime)
        }
      }
    },

    "tool.execute.before": async (input, output) => {
      const editTools = ["edit", "write", "apply_patch"]
      if (!editTools.includes(input.tool)) return

      const paths = extractPaths(input.tool, input.args)
      for (const filePath of paths) {
        const readTime = readTimestamps.get(filePath)
        if (readTime === undefined) {
          // Built-in already enforces "must read before edit", so this is
          // just a safety net.
          continue
        }

        const currentMtime = getMtime(filePath)
        if (currentMtime === undefined) {
          // File was deleted since read -- let the built-in tool handle it.
          continue
        }

        if (currentMtime > readTime) {
          // Clear the stale timestamp so the agent must re-read.
          readTimestamps.delete(filePath)
          throw new Error(
            `File has been modified since it was last read: ${filePath}\n` +
            `Read at: ${new Date(readTime).toISOString()}\n` +
            `Modified at: ${new Date(currentMtime).toISOString()}\n` +
            `Re-read the file before editing.`
          )
        }
      }
    },
  }
}
