import { tool } from "@opencode-ai/plugin"
async function ensurePypdfCommand(): Promise<boolean> {
  if (Bun.which("pypdf")) {
    return true
  }

  const install = Bun.spawn(["uv", "tool", "install", "pypdf"], {
    stderr: "pipe",
    stdout: "pipe",
  })
  await install.exited

  // pypdf currently has no console-script entry point, so uv tool install
  // reports failure even though the Python package itself is valid.
  return Boolean(Bun.which("pypdf"))
}

export const extract = tool({
  description:
    "Extract readable text from a PDF. Installs the pypdf command with uv on first use when it is unavailable.",
  args: {
    file_path: tool.schema.string().describe("Absolute path to the PDF file"),
  },
  async execute(args, _context) {
    try {
      const commandAvailable = await ensurePypdfCommand()
      const extract = Bun.spawn(
        commandAvailable
          ? ["pypdf", "extract-text", args.file_path, "-"]
          : [
              "uv",
              "run",
              "--with",
              "pypdf",
              "python",
              "-c",
              "from pypdf import PdfReader; import sys; print('\\n'.join(page.extract_text() or '' for page in PdfReader(sys.argv[1]).pages))",
              args.file_path,
            ],
        {
        stderr: "pipe",
        stdout: "pipe",
        },
      )
      const exitCode = await extract.exited

      if (exitCode !== 0) {
        const stderr = await new Response(extract.stderr).text()
        return `PDF extraction failed: ${stderr.trim()}`
      }

      return await new Response(extract.stdout).text()
    } catch (error) {
      return `PDF extraction failed: ${error instanceof Error ? error.message : String(error)}`
    }
  },
})
