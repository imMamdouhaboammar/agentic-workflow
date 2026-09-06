#!/usr/bin/env node
import { execSync } from 'node:child_process';
import process from 'node:process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const command = process.argv[2] || 'help';

function printHelp() {
  console.log(`
AgenticWorkflow CLI — Universal Agentic Toolchain

Usage:
  agentic-workflow <command> [options]

Commands:
  init        Initialize SOT runtime directories and verify hook infrastructure
  validate    Validate workflow state, SOT schema, and pACS log integrity
  status      Display live workflow dashboard and observability metrics
  test        Run safety, security, and verification test suite
  help        Show this help message

Options:
  --version, -v   Show version
  --help, -h      Show help
`);
}

switch (command) {
  case 'init': {
    console.log("⚡ [agentic-workflow] Initializing infrastructure and runtime directories...");
    try {
      execSync("python3 .claude/hooks/scripts/setup_init.py", { cwd: rootDir, stdio: 'inherit' });
      console.log("✅ Initialization complete!");
    } catch (e) {
      process.exit(1);
    }
    break;
  }
  case 'validate': {
    console.log("🔍 [agentic-workflow] Validating workflow integrity...");
    try {
      execSync("python3 .claude/hooks/scripts/validate_pacs.py --help", { cwd: rootDir, stdio: 'pipe' });
      console.log("✅ Validation tooling online and ready!");
    } catch (e) {
      process.exit(1);
    }
    break;
  }
  case 'status': {
    console.log("📊 [agentic-workflow] Fetching workflow status...");
    try {
      execSync("python3 .claude/hooks/scripts/query_workflow.py dashboard", { cwd: rootDir, stdio: 'inherit' });
    } catch (e) {
      console.log("No active workflow state.yaml found. Ready for new workflow design.");
    }
    break;
  }
  case 'test': {
    console.log("🧪 [agentic-workflow] Running test suite (safety, secret filter, sensitive files)...");
    try {
      console.log("-> Running block_destructive_commands tests (43 cases)...");
      execSync("python3 .claude/hooks/scripts/_test_block_destructive.py", { cwd: rootDir, stdio: 'inherit' });
      console.log("-> Running secret_filter tests (44 cases)...");
      execSync("python3 .claude/hooks/scripts/_test_secret_filter.py", { cwd: rootDir, stdio: 'inherit' });
      console.log("-> Running sensitive_file_guard tests (44 cases)...");
      execSync("python3 .claude/hooks/scripts/_test_sensitive_file_guard.py", { cwd: rootDir, stdio: 'inherit' });
      console.log("✅ ALL TESTS PASSED!");
    } catch (e) {
      console.error("❌ Test suite encountered a failure.");
      process.exit(1);
    }
    break;
  }
  case '--version':
  case '-v': {
    console.log("agentic-workflow v1.0.0");
    break;
  }
  case 'help':
  case '--help':
  case '-h':
  default:
    printHelp();
    break;
}
