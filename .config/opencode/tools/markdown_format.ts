import { tool } from "@opencode-ai/plugin"
import os from "os"
import path from "path"

const SCRIPT = path.join(os.homedir(), ".agents", "tools", "markdown-format.py")

export default tool({
  description:
    "Format Markdown files deterministically. Use format after authoring or editing Markdown; use check only for " +
    "explicit human or CI validation.",
  args: {
    mode: tool.schema
      .enum(["check", "format"])
      .default("format")
      .describe("Use 'format' during normal agent work or 'check' for explicit human or CI validation"),
    paths: tool.schema
      .array(tool.schema.string())
      .min(1)
      .describe("One or more Markdown files or directories, preferably absolute paths"),
  },
  async execute(args, context) {
    try {
      const paths = args.paths.map((filePath) => path.isAbsolute(filePath) ? filePath : path.resolve(context.directory, filePath))
      const result = await Bun.$`${SCRIPT} ${args.mode} ${paths}`.text()
      return result.trim()
    } catch (error: any) {
      const stderr = error?.stderr?.toString?.() ?? String(error)
      return `Markdown ${args.mode} failed: ${stderr.trim()}`
    }
  },
})
