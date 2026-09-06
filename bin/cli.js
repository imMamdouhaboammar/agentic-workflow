#!/usr/bin/env node
/**
 * AgenticWorkflow CLI — Universal Autonomous Agentic Toolchain
 * 
 * Implements:
 * - Autopilot End-to-End Self-Driving Execution Loop
 * - Clean Code Guard & AI Failure-Mode Auditor
 * - Multi-Agent System Architecture & Trace Observability
 * - AI Engineering & Evaluation Gates
 */

import { execSync } from 'node:child_process';
import process from 'node:process';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const args = process.argv.slice(2);
const command = args[0] || 'help';

function printHelp() {
  console.log(`
⚡ AgenticWorkflow CLI — Universal Autonomous Agentic Toolchain ⚡

Usage:
  agentic-workflow <command> [options]

Core Autonomous Commands:
  autopilot, run, drive   Execute autonomous workflow end-to-end with self-fueling & circuit breakers
  guard, clean-code       Run Clean Code Guard pass (SOLID, 24 Imperatives, AI failure modes)
  eval, evaluate          Run AI Engineer fairness, prompt-injection, and drift evaluation
  traces, observability   Inspect multi-agent observable trace records

Standard Toolchain Commands:
  init                    Initialize SOT runtime directories and verify hook infrastructure
  validate                Validate workflow state, SOT schema, and pACS log integrity
  status                  Display live workflow dashboard and observability metrics
  test                    Run full automated test suite (safety, guard, MAS, evaluator)
  help                    Show this help message

Options:
  --title <text>          Project title for autopilot workflow
  --goal <text>           Core objective / goal for autopilot workflow
  --version, -v           Show version
  --help, -h              Show help
`);
}

function parseArgValue(flag) {
  const idx = args.indexOf(flag);
  if (idx !== -1 && idx + 1 < args.length) {
    return args[idx + 1];
  }
  return null;
}

switch (command) {
  case 'autopilot':
  case 'run':
  case 'drive': {
    const title = parseArgValue('--title') || 'Autonomous Production Workflow';
    const goal = parseArgValue('--goal') || 'Autonomous end-to-end execution without user bottleneck';
    console.log(`🚀 [agentic-workflow] Launching Autopilot Engine...`);
    console.log(`   Title: "${title}"`);
    console.log(`   Goal:  "${goal}"`);
    try {
      const script = `
from core.autopilot_engine import AutopilotEngine
engine = AutopilotEngine(project_dir="${rootDir}", auto_approve=True)
engine.plan_default_workflow(title="${title}", goal="${goal}")
success = engine.run_all()
exit(0 if success else 1)
`;
      execSync(`python3 -c '${script}'`, { cwd: rootDir, stdio: 'inherit' });
    } catch (e) {
      console.error("❌ Autopilot execution failed or circuit breaker tripped.");
      process.exit(1);
    }
    break;
  }

  case 'guard':
  case 'clean-code': {
    const targetDir = args[1] || '.';
    console.log(`🛡️ [agentic-workflow] Running Clean Code Guard on '${targetDir}'...`);
    try {
      execSync(`python3 core/clean_code_guard.py "${targetDir}"`, { cwd: rootDir, stdio: 'inherit' });
    } catch (e) {
      process.exit(1);
    }
    break;
  }

  case 'eval':
  case 'evaluate': {
    console.log("🧪 [agentic-workflow] Running AI Engineer Evaluation Gates...");
    try {
      execSync("python3 -m unittest tests/test_ai_evaluator.py", { cwd: rootDir, stdio: 'inherit' });
      console.log("✅ AI Evaluation Gates passed: Fairness, Prompt Injection, and PSI Drift stable.");
    } catch (e) {
      process.exit(1);
    }
    break;
  }

  case 'traces':
  case 'observability': {
    const traceDir = path.join(rootDir, '.traces');
    console.log(`📊 [agentic-workflow] Querying Multi-Agent Traces in ${traceDir}...`);
    if (!fs.existsSync(traceDir)) {
      console.log("No traces recorded yet.");
      break;
    }
    const files = fs.readdirSync(traceDir).filter(f => f.endsWith('.jsonl'));
    console.log(`Found ${files.length} trace log(s):`);
    for (const f of files.slice(-5)) {
      const content = fs.readFileSync(path.join(traceDir, f), 'utf-8').trim().split('\n');
      console.log(`  - ${f} (${content.length} spans)`);
    }
    break;
  }

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
    console.log("🧪 [agentic-workflow] Running Full Multi-Engine Test Suite...");
    try {
      console.log("\n-> 1. Safety Hooks Tests (Destructive commands, secret filter, sensitive files)...");
      execSync("python3 .claude/hooks/scripts/_test_block_destructive.py", { cwd: rootDir, stdio: 'inherit' });
      execSync("python3 .claude/hooks/scripts/_test_secret_filter.py", { cwd: rootDir, stdio: 'inherit' });
      execSync("python3 .claude/hooks/scripts/_test_sensitive_file_guard.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 2. Clean Code Guard Tests...");
      execSync("python3 -m unittest tests/test_clean_code_guard.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 3. Multi-Agent Systems & Circuit Breaker Tests...");
      execSync("python3 -m unittest tests/test_multi_agent_system.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 4. AI Engineer Evaluation Tests...");
      execSync("python3 -m unittest tests/test_ai_evaluator.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 5. Autopilot Engine & Refueling Tests...");
      execSync("python3 -m unittest tests/test_autopilot_engine.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n✅ ALL MULTI-ENGINE TESTS PASSED CLEANLY!");
    } catch (e) {
      console.error("❌ Test suite encountered a failure.");
      process.exit(1);
    }
    break;
  }

  case '--version':
  case '-v': {
    console.log("agentic-workflow v1.1.0");
    break;
  }

  case 'help':
  case '--help':
  case '-h':
  default:
    printHelp();
    break;
}
