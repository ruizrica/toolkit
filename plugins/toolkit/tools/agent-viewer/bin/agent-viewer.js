#!/usr/bin/env node

const { parseCliArgs, printTopLevelHelp, printVersion, fail } = require("../lib/cli-args.js");
const { runPlanViewer } = require("../lib/run-plan-viewer.js");
const { runSpecViewer } = require("../lib/run-spec-viewer.js");
const { runCompletionViewer } = require("../lib/run-completion-viewer.js");

async function main() {
  const parsed = parseCliArgs(process.argv.slice(2));

  if (parsed.version) {
    printVersion();
    return;
  }

  if (!parsed.command) {
    printTopLevelHelp();
    return;
  }

  if (parsed.help || parsed.commandHelp) {
    printTopLevelHelp(parsed.command);
    return;
  }

  switch (parsed.command) {
    case "plan":
      await runPlanViewer(parsed);
      return;
    case "spec":
      await runSpecViewer(parsed);
      return;
    case "completion":
      await runCompletionViewer(parsed);
      return;
    default:
      fail(`Unknown command: ${parsed.command}`);
  }
}

main().catch((error) => {
  fail(error && error.message ? error.message : String(error));
});
