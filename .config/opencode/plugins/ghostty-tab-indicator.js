export const GhosttyTabIndicator = async ({ directory }) => {
  const label = directory.split("/").filter(Boolean).pop() ?? directory

  const setTitle = (indicator) => {
    process.stdout.write(`\x1b]0;${indicator} ${label}\x07`)
  }

  return {
    "session.idle": async () => {
      setTitle("✓")
    },
    "session.status": async ({ status }) => {
      if (status !== "idle") {
        setTitle("⏱")
      }
    },
  }
}
