import { tool } from "@opencode-ai/plugin"
import path from "path"
import os from "os"

const SCRIPT = path.join(os.homedir(), ".config", "opencode", "tools", "clipboard_image.py")

export default tool({
  description:
    "Capture or grab a screenshot and save it to a fixed path so the model can read it. " +
    "Use mode='capture' to open an interactive region selector (the user draws a box on screen). " +
    "Use mode='clipboard' (default) to grab whatever image is already on the clipboard. " +
    "After this tool returns successfully, use the Read tool on the returned path to view the image.",
  args: {
    mode: tool.schema
      .enum(["clipboard", "capture"])
      .default("clipboard")
      .describe("'clipboard' grabs the current clipboard image; 'capture' opens an interactive region selector"),
  },
  async execute(args, _context) {
    try {
      const result = await Bun.$`uv run ${SCRIPT} ${args.mode}`.text()
      const outPath = result.trim()
      if (!outPath) {
        return `Failed: script produced no output.`
      }
      return outPath
    } catch (err: any) {
      const stderr = err?.stderr?.toString?.() ?? String(err)
      return `Failed to capture screenshot: ${stderr}`
    }
  },
})
