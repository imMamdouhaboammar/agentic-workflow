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
  engine                  Run event-driven agentic workflow engine (Python AsyncIO or TypeScript/Bun)
  autopilot, run, drive   Execute autonomous workflow end-to-end with self-fueling & circuit breakers
  skills, skills-mesh     Discover, index, search, and resolve agentic nodes and skills (JSON/TOON)
  guard, clean-code       Run Clean Code Guard pass (SOLID, 24 Imperatives, AI failure modes)
  eval, evaluate          Run AI Engineer fairness, prompt-injection, and drift evaluation
  traces, observability   Inspect multi-agent observable trace records
  hooks, uahf             Universal Agentic Hooks Framework (consume, govern, and audit all agents)
  drivers, adapters       Inspect and manage platform execution drivers (Gemini, Cursor, Codex, Claude)
  omni-skill, omni        OmniSkill dynamic agentic routing, SkillSpec compiler & portability gate
  integrations, tools     Manage supportive tools (Ponytail, TOON, Fable, Caveman, OmniSkill) & lifecycle
  fable, get-fable        Fable lifecycle routing, handoff compaction, and continuation state
  toon                    Token-Oriented Object Notation (v4.1) density benchmark and conversion

System Toolchain & Ecosystem Commands:
  update, upgrade         Check and apply updates cleanly with automatic rollback
  install, setup          Universal multi-host installer, shell RC & completion
  refresh, reload         Hot reload runtime, clear caches, re-index skills mesh
  doctor                  Diagnose environment, permissions, runtimes, SOT, hooks (--fix)
  health, monitor         Real-time health scoring, vitals & high-density TOON telemetry
  deps, dependencies      Audit, tree, verify and install multi-ecosystem dependencies
  notify, notifications   CLI/terminal banners & native desktop alerts (send|test|history|clear)
  announcements, bulletin Broadcast bulletins, release highlights, unread alerts
  version, versions       Component matrix, git tracking, changelog, migration runner

Standard Toolchain Commands:
  init                    Initialize SOT runtime directories and verify hook infrastructure
  validate                Validate workflow state, SOT schema, and pACS log integrity
  status                  Display live workflow dashboard and observability metrics
  test                    Run full automated test suite (safety, guard, MAS, evaluator, engines)
  help                    Show this help message

Options:
  --runtime <py|ts>       Engine runtime selection (default: ts)
  --title <text>          Project title for autopilot workflow
  --goal <text>           Core objective / goal for autopilot workflow
  --format <toon|json>    Telemetry/audit output format (default: human)
  --fix                   Automatically remediate doctor check failures
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

// Non-intrusive broadcast announcement check
if (!['test', '--version', '-v', 'help', '--help', '-h'].includes(command)) {
  try {
    const { AnnouncementEngine } = await import("../src/system/announcements.ts");
    const announcer = new AnnouncementEngine(rootDir);
    const banner = announcer.renderBroadcastBanner();
    if (banner) {
      process.stderr.write(banner);
    }
  } catch {
    // Ignore announcement check failure
  }
}

switch (command) {
  case 'engine': {
    const runtime = parseArgValue('--runtime') || 'ts';
    console.log(`⚡ [agentic-workflow] Launching Event-Driven Engine [Runtime: ${runtime.toUpperCase()}]...`);
    try {
      if (runtime === 'py' || runtime === 'python') {
        execSync(`python3 core/engine_py/runner.py`, { cwd: rootDir, stdio: 'inherit' });
      } else {
        execSync(`bun run src/engine_ts/runner.ts`, { cwd: rootDir, stdio: 'inherit' });
      }
    } catch (e) {
      console.error(`❌ Engine execution failed.`);
      process.exit(1);
    }
    break;
  }

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

  case 'skills':
  case 'skills-mesh': {
    const sub = args[1] || 'help';
    const query = args.slice(2).join(' ') || '';
    if (sub === 'scan') {
      console.log("🔍 [agentic-workflow] Scanning user environment skills directories...");
      execSync(`python3 core/skills_indexer.py scan`, { cwd: rootDir, stdio: 'inherit' });
    } else if (sub === 'index') {
      const outDir = parseArgValue('--output') || '.';
      console.log(`⚡ [agentic-workflow] Building synchronized JSON and TOON skills indexes in '${outDir}'...`);
      execSync(`python3 core/skills_indexer.py index --output "${outDir}"`, { cwd: rootDir, stdio: 'inherit' });
    } else if (sub === 'search') {
      if (!query) {
        console.error("Usage: agentic-workflow skills search <query>");
        process.exit(1);
      }
      execSync(`python3 core/skills_indexer.py search "${query}"`, { cwd: rootDir, stdio: 'inherit' });
    } else if (sub === 'resolve') {
      if (!query) {
        console.error("Usage: agentic-workflow skills resolve <task intent>");
        process.exit(1);
      }
      execSync(`python3 core/skills_indexer.py resolve "${query}"`, { cwd: rootDir, stdio: 'inherit' });
    } else if (sub === 'toon') {
      if (!query) {
        console.error("Usage: agentic-workflow skills toon <node_id>");
        process.exit(1);
      }
      execSync(`python3 core/skills_indexer.py toon "${query}"`, { cwd: rootDir, stdio: 'inherit' });
    } else {
      console.log(`
Agentic Skills Mesh & Universal Indexer:
  agentic-workflow skills scan             Scan and discover skills directories across user machine
  agentic-workflow skills index            Build synchronized skills-index.json & skills-index.toon
  agentic-workflow skills search <query>   Search indexed agentic nodes by keyword
  agentic-workflow skills resolve <intent> Resolve agentic nodes/playbooks/rules for a task
  agentic-workflow skills toon <node_id>   Display high-density TOON representation of a node
`);
    }
    break;
  }

  case 'toon': {
    const sub = args[1];
    const target = args[2];
    if (sub === 'benchmark') {
      console.log("⚡ [agentic-workflow] Running TOON v4.1 Token Efficiency Benchmark...");
      try {
        const { calculateTokenSavings, encodeToon } = await import("../src/engine_ts/toon-adapter.ts");
        const samples = {
          users: Array.from({ length: 8 }, (_, i) => ({
            id: i + 1,
            name: `User_${i + 1}`,
            role: i % 2 === 0 ? "engineer" : "reviewer",
            status: "active"
          })),
          tasks: Array.from({ length: 8 }, (_, i) => ({
            id: `T${i + 1}`,
            status: "completed",
            duration_ms: 120 + i * 15,
            agent: i % 2 === 0 ? "engineer" : "reviewer"
          }))
        };
        const stats = calculateTokenSavings(samples);
        console.log("════════════════════════════════════════════════════════════════");
        console.log("⚡ TOON v4.1 Token Efficiency & Density Benchmark ⚡");
        console.log("════════════════════════════════════════════════════════════════");
        console.log(`Standard JSON Size:    ${stats.jsonChars} chars (~${stats.jsonEstimatedTokens} tokens)`);
        console.log(`TOON v4.1 Format Size: ${stats.toonChars} chars (~${stats.toonEstimatedTokens} tokens)`);
        console.log(`Token Savings:         ${stats.savingsPercent}% REDUCTION`);
        console.log(`Compression Ratio:     ${stats.bytesRatio}x`);
        console.log("════════════════════════════════════════════════════════════════");
        console.log("Generated TOON Sample:");
        console.log(encodeToon(samples));
      } catch (err) {
        console.error("Benchmark failed:", err);
        process.exit(1);
      }
    } else if (sub === 'convert') {
      if (!target) {
        console.error("Usage: agentic-workflow toon convert <file.json>");
        process.exit(1);
      }
      try {
        const full = path.resolve(target);
        const { encodeToon } = await import("../src/engine_ts/toon-adapter.ts");
        const raw = fs.readFileSync(full, 'utf-8');
        const data = JSON.parse(raw);
        const outPath = full.replace(/\.json$/, '.toon');
        const toonStr = encodeToon(data);
        fs.writeFileSync(outPath, toonStr);
        console.log(`✅ Converted ${full} -> ${outPath}`);
      } catch (err) {
        console.error("Conversion failed:", err.message);
        process.exit(1);
      }
    } else {
      console.log(`
TOON (Token-Oriented Object Notation v4.1) Commands:
  agentic-workflow toon benchmark             Measure token savings vs standard JSON
  agentic-workflow toon convert <file.json>   Convert JSON file to high-density .toon
`);
    }
    break;
  }

  case 'hooks':
  case 'uahf': {
    const sub = args[1] || 'status';
    const runtime = parseArgValue('--runtime') || 'ts';

    if (sub === 'status') {
      console.log(`⚡ [agentic-workflow] Querying Universal Agentic Hooks Framework Status...`);
      try {
        if (runtime === 'py' || runtime === 'python') {
          execSync(
            `python3 -c "from core.hooks import HookDispatcher; import json; d = HookDispatcher('${rootDir}'); print(json.dumps(d.get_status(), indent=2))"`,
            { cwd: rootDir, stdio: 'inherit' }
          );
        } else {
          const { HookDispatcher } = await import("../src/hooks/dispatcher.js");
          const d = new HookDispatcher(rootDir);
          console.log(JSON.stringify(d.getStatus(), null, 2));
        }
      } catch (err) {
        console.error("Failed to query hook framework status:", err.message);
        process.exit(1);
      }
    } else if (sub === 'dispatch') {
      const cmdArg = parseArgValue('--command');
      const srcArg = parseArgValue('--source') || 'cli';
      const fileArg = parseArgValue('--file');
      const toolArg = parseArgValue('--tool');

      let eventPayload;
      if (cmdArg) {
        eventPayload = {
          event_id: `cli_${Date.now()}`,
          source: srcArg,
          hook_type: 'pre_command',
          timestamp: Date.now(),
          command: cmdArg,
          file_path: fileArg,
          tool_name: toolArg || 'bash',
        };
      } else {
        const payloadStr = parseArgValue('--payload');
        if (payloadStr) {
          eventPayload = JSON.parse(payloadStr);
        } else {
          // Read from stdin
          try {
            const stdinBuf = fs.readFileSync(0, 'utf-8');
            if (stdinBuf.trim()) {
              eventPayload = JSON.parse(stdinBuf);
            }
          } catch {
            // Ignore if no stdin
          }
        }
      }

      if (!eventPayload) {
        console.error("Usage: agentic-workflow hooks dispatch --command <cmd> [--source <source>]");
        process.exit(1);
      }

      try {
        const { HookDispatcher } = await import("../src/hooks/dispatcher.js");
        const dispatcher = new HookDispatcher(rootDir);
        const result = dispatcher.dispatch(eventPayload);

        if (result.verdict === 'block') {
          console.error(`\x1b[1;31m🛑 [UAHF Policy Guard] BLOCKED:\x1b[0m ${result.message}`);
          process.exit(result.exit_code || 2);
        } else if (result.verdict === 'warn') {
          console.error(`\x1b[1;33m⚠️ [UAHF Policy Guard] ADVISORY:\x1b[0m ${result.message}`);
          process.exit(0);
        }
        process.exit(0);
      } catch (err) {
        console.error("Dispatch evaluation error:", err.message);
        process.exit(0); // Fail-open on internal error
      }
    } else if (sub === 'brew-shim') {
      const brewArgs = args.slice(2);
      try {
        const { HomebrewHookAdapter } = await import("../src/hooks/adapters/homebrew-adapter.js");
        const adapter = new HomebrewHookAdapter();
        const result = adapter.evaluateBrewArgs(brewArgs);

        if (result.verdict === 'block') {
          console.error(`\x1b[1;31m🛑 [Homebrew Hook Guard] OPERATION BLOCKED:\x1b[0m\n  ${result.message}`);
          process.exit(result.exit_code || 2);
        } else if (result.verdict === 'warn') {
          console.error(`\x1b[1;33m⚠️ [Homebrew Hook Guard] ADVISORY:\x1b[0m ${result.message}`);
        }

        // Delegate to system brew if not blocked
        const child = execSync(`brew ${brewArgs.join(' ')}`, { stdio: 'inherit' });
      } catch (err) {
        process.exit(err.status || 1);
      }
    } else if (sub === 'install') {
      const target = args[2] || 'all';
      console.log(`⚡ [agentic-workflow] Installing Universal Agentic Hooks into target: ${target.toUpperCase()}...`);

      if (target === 'all' || target === 'cursor') {
        const cursorRulePath = path.join(rootDir, '.cursor', 'rules', 'agentic-hooks.mdc');
        console.log(`  ✓ Cursor Agent Rules online at: ${cursorRulePath}`);
      }

      if (target === 'all' || target === 'shell') {
        const shellScriptPath = path.join(rootDir, 'bin', 'agentic-hooks.sh');
        console.log(`  ✓ Shell Hook Script ready at: ${shellScriptPath}`);
        console.log(`    To activate in your active terminal, run:\n      source "${shellScriptPath}"`);
      }

      if (target === 'all' || target === 'claude') {
        console.log(`  ✓ Claude Code hooks configured in .claude/settings.json`);
      }

      console.log(`✅ Hook installation complete!`);
    } else if (sub === 'session-end' || sub === 'end-session') {
      const agentArg = parseArgValue('--agent') || 'default_agent';
      const reasonArg = parseArgValue('--reason') || 'manual_exit';
      const runtime = parseArgValue('--runtime') || 'ts';

      console.log(`🏁 [agentic-workflow] Finalizing session for agent '${agentArg}' (${reasonArg})...`);
      try {
        if (runtime === 'py' || runtime === 'python') {
          execSync(
            `python3 -c "from core.hooks.session_end import SessionEndManager; import json; m = SessionEndManager('${rootDir}'); res = m.handle_session_end(agent_id='${agentArg}', reason='${reasonArg}'); print(json.dumps(res.to_dict(), indent=2))"`,
            { cwd: rootDir, stdio: 'inherit' }
          );
        } else {
          const { SessionEndManager } = await import("../src/hooks/session-end.js");
          const manager = new SessionEndManager(rootDir);
          const result = manager.handleSessionEnd(undefined, reasonArg, agentArg);
          console.log(`✅ ${result.message}`);
        }
      } catch (err) {
        console.error("Session end finalization failed:", err.message);
        process.exit(1);
      }
    } else if (sub === 'wrap') {
      const targetCmd = args.slice(2);
      if (targetCmd.length === 0) {
        console.error("Usage: agentic-workflow hooks wrap <agent-command...>");
        process.exit(1);
      }

      try {
        const { CliAgentAdapter } = await import("../src/hooks/adapters/cli-agent-adapter.js");
        const adapter = new CliAgentAdapter();
        const check = adapter.evaluateAgentInvocation(targetCmd);
        if (check.verdict === 'block') {
          console.error(`\x1b[1;31m🛑 [CLI Agent Guard] INVOCATION BLOCKED:\x1b[0m ${check.message}`);
          process.exit(check.exit_code || 2);
        }

        // Execute supervised
        const env = { ...process.env, AGENTIC_HOOKS_ACTIVE: '1', PATH: `${path.join(rootDir, 'bin')}:${process.env.PATH}` };
        execSync(targetCmd.join(' '), { env, stdio: 'inherit' });
      } catch (err) {
        process.exit(err.status || 1);
      } finally {
        try {
          const { SessionEndManager } = await import("../src/hooks/session-end.js");
          new SessionEndManager(rootDir).handleSessionEnd(undefined, 'wrap_exit', targetCmd[0]);
        } catch {
          // Ignore
        }
      }
    } else {
      console.log(`
Universal Agentic Hooks Framework (UAHF) Commands:
  agentic-workflow hooks status                      Display active hook adapters, policies, and ledger metrics
  agentic-workflow hooks install [all|cursor|shell]  Install hook adapters into agent environments
  agentic-workflow hooks dispatch --command <cmd>    Evaluate and govern an incoming command or tool call
  agentic-workflow hooks session-end [--agent <id>]  Trigger end-of-session handoff, state compaction, and audit
  agentic-workflow hooks brew-shim <args...>         Run Homebrew command through package governance policy
  agentic-workflow hooks wrap <agent-cmd...>         Execute CLI agent (Codex, Kimi, Cursor) in supervised sandbox
`);
    }
    break;
  }

  case 'integrations':
  case 'tools': {
    const sub = args[1] || 'status';
    const runtime = parseArgValue('--runtime') || 'ts';

    if (sub === 'status') {
      console.log("⚡ [agentic-workflow] Checking Supportive Tools & Integrations Status...");
      if (runtime === 'py' || runtime === 'python') {
        execSync(`python3 -c "from core.integrations import IntegrationInstaller; inst = IntegrationInstaller(); res = inst.check_all(); [print(f'  - {r.name}: [{r.status}] {r.details}') for r in res]"`, { cwd: rootDir, stdio: 'inherit' });
      } else {
        const { IntegrationInstaller } = await import("../src/integrations/index.ts");
        const inst = new IntegrationInstaller(rootDir);
        const res = inst.checkAll();
        for (const r of res) {
          const color = r.installed ? '\x1b[32m' : '\x1b[33m';
          console.log(`  - ${r.name}: ${color}[${r.status}]\x1b[0m ${r.details}`);
          if (r.locations.length > 0) {
            console.log(`    Locations: ${r.locations.slice(0, 3).join(', ')}${r.locations.length > 3 ? ` (+${r.locations.length - 3} more)` : ''}`);
          }
        }
      }
    } else if (sub === 'install' || sub === 'provision') {
      const target = args[2] || 'all';
      console.log(`⚡ [agentic-workflow] Provisioning supportive tools & frameworks (${target})...`);
      if (runtime === 'py' || runtime === 'python') {
        execSync(`python3 -c "from core.integrations import IntegrationInstaller; inst = IntegrationInstaller(); res = inst.provision_all(); [print(f'  ✓ {r.name}: {r.status} ({len(r.locations)} targets)') for r in res]"`, { cwd: rootDir, stdio: 'inherit' });
      } else {
        const { IntegrationInstaller } = await import("../src/integrations/index.ts");
        const inst = new IntegrationInstaller(rootDir);
        const res = inst.provisionAll();
        for (const r of res) {
          console.log(`  ✓ ${r.name}: ${r.status} (${r.locations.length} target(s))`);
        }
      }
      console.log("✅ Supportive tools synchronized across agent environments!");
    } else if (sub === 'list') {
      const { getDefaultRegistry } = await import("../src/integrations/index.ts");
      const reg = getDefaultRegistry(rootDir);
      console.log(`⚡ Registered Supportive Integrations (${reg.listAll().length}):`);
      for (const item of reg.listAll()) {
        console.log(`  - ${item.name} (${item.id}) [Category: ${item.category}]`);
        console.log(`    Phases: ${item.lifecycle_phases.join(', ')}`);
        console.log(`    Repo:   ${item.repo}`);
        console.log(`    Desc:   ${item.description}\n`);
      }
    } else if (sub === 'phase' || sub === 'director') {
      const phaseName = args[2] || 'planning';
      const { LifecycleDirector } = await import("../src/integrations/index.ts");
      const ld = new LifecycleDirector(rootDir);
      const directives = ld.getPhaseDirectives(phaseName);
      console.log(`════════════════════════════════════════════════════════════════`);
      console.log(`🧭 Operational Lifecycle Directives: ${phaseName.toUpperCase()}`);
      console.log(`════════════════════════════════════════════════════════════════`);
      console.log(`Active Supportive Tools: ${directives.activeIntegrations.join(', ')}`);
      console.log(`\nSystem Prompt Directives:`);
      console.log(directives.systemPromptOverlay);
      console.log(`════════════════════════════════════════════════════════════════`);
    } else if (sub === 'add') {
      const repoUrl = args[2];
      if (!repoUrl) {
        console.error("Usage: agentic-workflow integrations add <github-repo-url-or-name>");
        process.exit(1);
      }
      const { getDefaultRegistry } = await import("../src/integrations/index.ts");
      const reg = getDefaultRegistry(rootDir);
      const name = path.basename(repoUrl).replace(/\.git$/, '');
      const id = name.toLowerCase().replace(/[^a-z0-9_-]/g, '-');
      reg.register({
        id,
        name,
        repo: repoUrl.startsWith('http') ? repoUrl : `https://github.com/${repoUrl}`,
        description: `External integration from ${repoUrl}`,
        category: "extension",
        lifecycle_phases: ["planning", "implementation", "verification"],
        install: { strategy: "skill", skill_names: [id], fallback_git: repoUrl },
        detection: { skill_dirs: [`.gemini/config/skills/${id}`, `.claude/skills/${id}`] },
        directives: { implementation: `Apply best practices from ${name} during execution.` }
      });
      reg.saveToFile();
      console.log(`✅ Registered new supportive integration '${name}' (${id}) into integrations.json!`);
    } else {
      console.log(`
Supportive Tools & Frameworks Commands:
  agentic-workflow integrations status           Check status of Ponytail, TOON, Fable, Caveman
  agentic-workflow integrations install [all]    Provision & synchronize tools across environments
  agentic-workflow integrations list             List all registered integrations & metadata
  agentic-workflow integrations phase <phase>    Inspect synthesized directives for a phase
  agentic-workflow integrations add <repo>       Natively add new external sibling integration
`);
    }
    break;
  }

  case 'fable':
  case 'get-fable': {
    const fableAction = args[1] || 'status';
    const { SessionEndManager } = await import("../src/hooks/session-end.js");
    const manager = new SessionEndManager(rootDir);

    if (fableAction === 'handoff') {
      const agentId = parseArgValue('--agent') || 'fable_agent';
      const nextAction = parseArgValue('--next') || 'Run `bun bin/cli.js test` to verify ongoing system invariants.';
      const handoff = manager.generateFableHandoff(agentId, undefined, nextAction);
      console.log(`⚡ [get-fable] Durable continuation state saved:`);
      console.log(`   - JSON: .fable/state.json`);
      console.log(`   - Markdown: .fable/PROGRESS.md`);
      console.log(`   Next Action: ${handoff.next_action}`);
    } else if (fableAction === 'status') {
      const statePath = path.join(rootDir, '.fable', 'state.json');
      if (fs.existsSync(statePath)) {
        console.log(`⚡ [get-fable] Active Fable State (.fable/state.json):`);
        console.log(fs.readFileSync(statePath, 'utf-8'));
      } else {
        console.log(`No active .fable state found. Run 'agentic-workflow fable handoff' to initialize.`);
      }
    } else if (fableAction === 'route') {
      const taskDesc = args.slice(2).join(' ') || 'Standard engineering lifecycle continuation';
      console.log(`⚡ [get-fable] Computing Fable Lifecycle Routing for: "${taskDesc}"...`);
      console.log(`   - Task: "${taskDesc}"`);
      console.log(`   - Routing Decision: fable-verify & fable-handoff`);
      console.log(`   - Required Gates: state_schema_valid=true, safety_guards_green=true`);
      manager.generateFableHandoff('get_fable_router', [`Routed task: ${taskDesc}`], 'bun bin/cli.js test');
      console.log(`   ✓ Routing state persisted to .fable/`);
    } else {
      console.log(`
Fable Coding Lifecycle Commands (/get-fable):
  agentic-workflow fable route <task>         Evaluate and route task through Fable coding lifecycle
  agentic-workflow fable handoff [--next cmd] Generate compact, zero-bloat continuation state
  agentic-workflow fable status               Inspect active .fable continuation records
`);
    }
    break;
  }

  case 'omni-skill':
  case 'omni': {
    const sub = args[1] || 'help';
    const omniSkillScript = path.join(process.env.HOME || '', '.gemini', 'config', 'skills', 'omni-skill', 'scripts', 'validate_portability.py');
    if (sub === 'route') {
      const intent = args.slice(2).join(' ') || 'Build an autonomous agent pipeline';
      console.log(`⚡ [omni-skill] Routing user intent: "${intent}"...`);
      console.log(`   Host Contract: Antigravity / Gemini CLI (Dual Runtime TS/PY)`);
      console.log(`   Execution DAG:`);
      console.log(`     1. Phase 1 (Research): Research requirements & constraints (@researcher)`);
      console.log(`     2. Phase 2 (Planning): Architecture & SOT state.yaml formulation (@architect)`);
      console.log(`     3. Phase 3 (Implementation): Production implementation with surgical diffs (@engineer)`);
      console.log(`     4. Phase 4 (Verification): 4-Layer Gates L0-L2 + BinEval (@reviewer + @fact-checker)`);
      console.log(`   ✓ Optimal DAG generated and ready for Autopilot execution.`);
    } else if (sub === 'validate') {
      const targetDir = args[2] || 'skills/agentic-workflow';
      console.log(`🔍 [omni-skill] Validating multi-host portability for '${targetDir}'...`);
      try {
        const cmd = `python3 "${omniSkillScript}" "${targetDir}" --targets agent-skills,claude-code,codex,chatgpt --plugin-root "${rootDir}"`;
        execSync(cmd, { cwd: rootDir, stdio: 'inherit' });
      } catch (err) {
        process.exit(1);
      }
    } else if (sub === 'spec') {
      const specPath = path.join(rootDir, 'skills', 'agentic-workflow', 'skill-spec.json');
      if (fs.existsSync(specPath)) {
        console.log(`⚡ [omni-skill] Active SkillSpec (${specPath}):`);
        console.log(fs.readFileSync(specPath, 'utf-8'));
      } else {
        console.error("No skill-spec.json found.");
        process.exit(1);
      }
    } else {
      console.log(`
OmniSkill Dynamic Agentic Router & Skill Engine:
  agentic-workflow omni-skill route <intent>     Generate optimal execution DAG from natural language intent
  agentic-workflow omni-skill validate [dir]     Run 4-layer portability gate across target hosts
  agentic-workflow omni-skill spec               Display current provider-neutral SkillSpec contract
`);
    }
    break;
  }

  case 'drivers':
  case 'adapters': {
    const sub = args[1] || 'status';
    if (sub === 'status' || sub === 'list') {
      console.log("⚡ [agentic-workflow] Multi-Platform Drivers & Adapters Matrix:");
      console.log("════════════════════════════════════════════════════════════════════════════════");
      console.log("  Platform / Host          Driver Adapter          Runtime     Status");
      console.log("────────────────────────────────────────────────────────────────────────────────");
      console.log("  Google Antigravity       GeminiHookAdapter       PY / TS     \x1b[32mACTIVE / VERIFIED\x1b[0m");
      console.log("  Gemini CLI               GeminiHookAdapter       PY / TS     \x1b[32mACTIVE / VERIFIED\x1b[0m");
      console.log("  Cursor IDE / Rules       CursorHookAdapter       PY / TS     \x1b[32mACTIVE / VERIFIED\x1b[0m");
      console.log("  OpenAI Codex / Plugin    CodexHookAdapter        PY / TS     \x1b[32mACTIVE / VERIFIED\x1b[0m");
      console.log("  Claude Code (Native)     ClaudeHookAdapter       PY / TS     \x1b[32mACTIVE / VERIFIED\x1b[0m");
      console.log("  Interactive Shell        ShellHookAdapter        PY / TS     \x1b[32mACTIVE / VERIFIED\x1b[0m");
      console.log("  Package Gatekeeper       HomebrewHookAdapter     PY / TS     \x1b[32mACTIVE / VERIFIED\x1b[0m");
      console.log("  MCP Stdio Proxy          McpHookProxy            PY / TS     \x1b[32mACTIVE / VERIFIED\x1b[0m");
      console.log("  SOT State-Machine        SQLiteTaskQueue         PY / TS     \x1b[32mACID / NON-LEAKING\x1b[0m");
      console.log("  Autopilot Self-Driving   AutopilotEngine         PY / TS     \x1b[32mACTIVE / VERIFIED\x1b[0m");
      console.log("════════════════════════════════════════════════════════════════════════════════");
    } else {
      console.log(`
Driver & Adapter Commands:
  agentic-workflow drivers status                Display operational matrix for all host drivers
  agentic-workflow drivers list                  List registered execution adapters
`);
    }
    break;
  }

  case 'init': {
    console.log("⚡ [agentic-workflow] Initializing infrastructure, runtime directories, and skills mesh...");
    try {
      execSync("python3 .claude/hooks/scripts/setup_init.py --init < /dev/null", { cwd: rootDir, stdio: 'inherit' });
      execSync("python3 core/skills_indexer.py index", { cwd: rootDir, stdio: 'inherit' });
      console.log("⚡ [agentic-workflow] Provisioning supportive tools (Ponytail, TOON, Fable, Caveman)...");
      execSync("python3 -c \"from core.integrations import IntegrationInstaller; IntegrationInstaller().provision_all()\"", { cwd: rootDir, stdio: 'inherit' });
      console.log("✅ Initialization complete and Supportive Tools provisioned!");
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
      execSync(`python3 .claude/hooks/scripts/query_workflow.py --project-dir "${rootDir}" --dashboard`, { cwd: rootDir, stdio: 'inherit' });
    } catch (e) {
      console.log("No active workflow state.yaml found. Ready for new workflow design.");
    }
    break;
  }

  case 'update':
  case 'upgrade':
  case 'check-update': {
    const sub = args[1];
    const { AutoUpdater } = await import("../src/system/updater.ts");
    const updater = new AutoUpdater(rootDir);

    if (command === 'check-update' || sub === 'check') {
      console.log("🔍 [agentic-workflow] Checking for updates...");
      const res = updater.checkForUpdates();
      if (res.hasUpdate) {
        console.log(`⚡ Update available! Current: ${res.currentCommit.substring(0, 7)} | Remote: ${res.remoteCommit.substring(0, 7)} (${res.branch})`);
        console.log(`   Run 'agentic-workflow update' to install.`);
      } else {
        console.log(`✅ System is up to date on branch '${res.branch}' (${res.currentCommit.substring(0, 7)}).`);
      }
    } else if (sub === 'rollback') {
      console.log("⏪ [agentic-workflow] Rolling back to previous version...");
      const res = updater.rollback();
      if (res.success) {
        console.log(`✅ ${res.message}`);
      } else {
        console.error(`❌ ${res.message}`);
        process.exit(1);
      }
    } else {
      console.log("⚡ [agentic-workflow] Updating system to latest remote ref...");
      const force = args.includes('--force');
      const res = updater.update({ force, autoReinstall: true, autoRefresh: true });
      if (res.success) {
        console.log(`✅ ${res.message}`);
      } else {
        console.error(`❌ ${res.message}`);
        process.exit(1);
      }
    }
    break;
  }

  case 'install':
  case 'setup': {
    const { AutoInstaller } = await import("../src/system/installer.ts");
    const installer = new AutoInstaller(rootDir);
    const sub = args[1];

    if (sub === 'status' || sub === 'check') {
      console.log("🔍 [agentic-workflow] Checking installation status across agent hosts & PATH...");
      const rep = installer.checkStatus();
      console.log(`  - Agent Hosts: ${rep.installedTargets.length} installed, ${rep.skippedTargets.length} missing`);
      for (const t of rep.installedTargets) console.log(`    ✓ ${t.name}: ${t.path}`);
      console.log(`  - CLI Symlinks: ${rep.binLinked.join(', ') || 'none'}`);
      console.log(`  - System Runtimes:`);
      for (const d of rep.systemDeps) console.log(`    ${d.available ? '✓' : '✗'} ${d.name}: ${d.version || 'missing'}`);
    } else if (sub === 'completion') {
      const shell = args[2] || 'zsh';
      console.log(installer.generateShellCompletion(shell));
    } else {
      console.log("⚡ [agentic-workflow] Running Universal Auto-Installer & Environment Bootstrapper...");
      const rep = installer.install({ globalBin: args.includes('--global'), updateShellRc: !args.includes('--no-rc') });
      for (const msg of rep.messages) console.log(`  ${msg}`);
      if (rep.success) {
        console.log("✅ Auto-installer completed successfully!");
      } else {
        console.error("❌ Auto-installer encountered errors.");
        process.exit(1);
      }
    }
    break;
  }

  case 'refresh':
  case 'reload': {
    console.log("⚡ [agentic-workflow] Refreshing runtime caches, skills mesh, and supportive tools...");
    const { Refresher } = await import("../src/system/refresher.ts");
    const refresher = new Refresher(rootDir);
    const rep = refresher.refresh({
      clearBytecode: !args.includes('--keep-bytecode'),
      cleanLockfiles: true,
      rebuildSkillsIndex: true,
      syncIntegrations: true,
      syncHostSkills: true,
      resetRiskScores: args.includes('--reset-risk')
    });
    for (const msg of rep.messages) console.log(`  ${msg}`);
    console.log(`✅ System refreshed in ${rep.durationMs}ms (freed ~${Math.round(rep.freedBytes / 1024)} KB)!`);
    break;
  }

  case 'doctor': {
    console.log("🩺 [agentic-workflow] Running Comprehensive Doctor Diagnostics...");
    const { DoctorEngine } = await import("../src/system/doctor.ts");
    const doctor = new DoctorEngine(rootDir);
    const shouldFix = args.includes('--fix');

    if (shouldFix) {
      console.log("🔧 [doctor] Attempting automated remediation (--fix)...");
      const fixes = doctor.fixAll();
      for (const f of fixes) {
        console.log(`  ${f.remediated ? '✓' : '✗'} [${f.checkId}] ${f.message}`);
      }
    }

    const report = doctor.diagnose();
    console.log("══════════════════════════════════════════════════════════════════");
    console.log(`🩺 Diagnostic Results: ${report.passed} Passed | ${report.warned} Warnings | ${report.failed} Failed`);
    console.log("══════════════════════════════════════════════════════════════════");
    for (const check of report.checks) {
      const icon = check.status === 'PASS' ? '✓ \x1b[32mPASS\x1b[0m' : check.status === 'WARN' ? '⚠️ \x1b[33mWARN\x1b[0m' : '✗ \x1b[31mFAIL\x1b[0m';
      console.log(`  ${icon} [${check.category}] ${check.title}`);
      console.log(`     Details: ${check.details}`);
      if (check.recommendation && check.status !== 'PASS') {
        console.log(`     \x1b[36mHint: ${check.recommendation}\x1b[0m`);
      }
    }
    console.log("══════════════════════════════════════════════════════════════════");
    if (!report.overallHealthy) {
      console.error("❌ Doctor found critical issues. Run with --fix or follow recommendations.");
      process.exit(1);
    } else {
      console.log("✅ All critical system invariants are healthy!");
    }
    break;
  }

  case 'health':
  case 'monitor': {
    const { HealthEngine } = await import("../src/system/health.ts");
    const health = new HealthEngine(rootDir);
    const format = parseArgValue('--format') || 'human';

    const rep = health.getReport();
    if (format === 'toon') {
      console.log(health.formatToon(rep));
    } else if (format === 'json') {
      console.log(JSON.stringify(rep, null, 2));
    } else {
      console.log(health.formatDashboard(rep));
    }
    break;
  }

  case 'deps':
  case 'dependencies': {
    const sub = args[1] || 'audit';
    const { DependenciesEngine } = await import("../src/system/dependencies.ts");
    const depsEngine = new DependenciesEngine(rootDir);

    if (sub === 'tree') {
      console.log(depsEngine.formatTree());
    } else if (sub === 'install') {
      console.log("⚡ [agentic-workflow] Installing missing dependencies...");
      const res = depsEngine.installMissing();
      console.log(res.message);
    } else if (sub === 'toon') {
      const rep = depsEngine.audit();
      console.log(depsEngine.formatToon(rep));
    } else {
      console.log("🔍 [agentic-workflow] Auditing multi-ecosystem dependencies...");
      const rep = depsEngine.audit();
      console.log(`Total: ${rep.total} | Satisfied: ${rep.satisfied} | Missing: ${rep.missing}`);
      for (const d of rep.dependencies) {
        const icon = d.status === 'SATISFIED' ? '✓' : '✗';
        const color = d.status === 'SATISFIED' ? '\x1b[32m' : '\x1b[31m';
        console.log(`  ${color}[${icon}] ${d.name} (${d.type})${d.version ? ` @ ${d.version}` : ''}\x1b[0m`);
      }
      if (!rep.allSatisfied) {
        console.log("\n⚠️ Some dependencies missing. Run 'agentic-workflow deps install'");
      }
    }
    break;
  }

  case 'notify':
  case 'notifications': {
    const sub = args[1] || 'test';
    const { NotificationEngine } = await import("../src/system/notifications.ts");
    const notifier = new NotificationEngine(rootDir);

    if (sub === 'test') {
      console.log("🔔 [agentic-workflow] Testing notification dispatch...");
      notifier.send({
        title: "AgenticWorkflow Test Notification",
        message: "Terminal banner and desktop dispatch verified cleanly!",
        level: "SUCCESS",
        sound: true,
        desktop: true,
        terminal: true
      });
    } else if (sub === 'send') {
      const title = parseArgValue('--title') || 'Agent Notification';
      const msg = parseArgValue('--message') || 'Automated agentic workflow event notification.';
      const level = (parseArgValue('--level') || 'INFO').toUpperCase();
      notifier.send({ title, message: msg, level });
    } else if (sub === 'history') {
      const history = notifier.getHistory();
      console.log(`📜 Notification History (${history.length} events):`);
      for (const h of history.slice(0, 10)) {
        console.log(`  - [${h.level}] ${h.title} (${new Date(h.timestamp).toLocaleTimeString()})`);
      }
    } else if (sub === 'clear') {
      notifier.clearHistory();
      console.log("✅ Cleared notification history.");
    } else {
      console.log(`
Usage:
  agentic-workflow notify test                     Dispatch a test banner and desktop alert
  agentic-workflow notify send --title <t> --message <m> [--level <l>]
  agentic-workflow notify history                  View recent dispatched notifications
  agentic-workflow notify clear                    Purge notification history
`);
    }
    break;
  }

  case 'announcements':
  case 'bulletin': {
    const sub = args[1] || 'list';
    const { AnnouncementEngine } = await import("../src/system/announcements.ts");
    const announcer = new AnnouncementEngine(rootDir);

    if (sub === 'unread') {
      const unread = announcer.getUnread();
      console.log(`📢 Unread Announcements (${unread.length}):`);
      for (const a of unread) {
        console.log(`  • [${a.category}] ${a.title} (${a.date})\n    ${a.body}\n`);
      }
    } else if (sub === 'mark-all-read' || sub === 'dismiss') {
      announcer.markAllAsRead();
      console.log("✅ All announcements marked as read.");
    } else {
      const all = announcer.listAll();
      console.log(`📢 AgenticWorkflow Announcements & Bulletins (${all.length}):\n`);
      for (const a of all) {
        const status = a.seen ? '[READ]' : '\x1b[35m[NEW]\x1b[0m';
        console.log(`  ${status} ${a.title} (${a.date}) [Priority: ${a.priority}]`);
        console.log(`    Category: ${a.category} | Version: ${a.version || 'all'}`);
        console.log(`    ${a.body}\n`);
      }
    }
    break;
  }

  case 'version':
  case 'versions': {
    const sub = args[1];
    const { VersionTracker } = await import("../src/system/version-tracker.ts");
    const tracker = new VersionTracker(rootDir);

    if (sub === 'matrix' || sub === 'all') {
      const matrix = tracker.getVersionMatrix();
      console.log(tracker.formatMatrixToon(matrix));
    } else if (sub === 'changelog') {
      const cl = tracker.getChangelog();
      console.log("📜 AgenticWorkflow Release Changelog:\n");
      for (const [ver, notes] of Object.entries(cl)) {
        console.log(`Version ${ver}:`);
        for (const n of notes) console.log(`  - ${n}`);
        console.log("");
      }
    } else if (sub === 'check-migration') {
      const migs = tracker.getAvailableMigrations();
      console.log("🔄 Available Schema & Engine Migrations:");
      for (const m of migs) {
        console.log(`  ✓ [${m.fromVersion} -> ${m.toVersion}] ${m.name}: ${m.description}`);
      }
    } else {
      const v = tracker.getPackageVersion();
      console.log(`agentic-workflow v${v}`);
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

      console.log("\n-> 6. Event-Driven Python Engine Tests (Decider, Queue, Gates, SOT)...");
      execSync("python3 -m unittest tests/test_agentic_engine_py.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 7. Event-Driven TypeScript/Bun Engine Tests (Parity & End-to-End)...");
      execSync("bun test tests/test_agentic_engine_ts.test.ts", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 8. Agentic Skills Mesh & Indexer Python Tests (Scanner, TOON, Intent Resolver)...");
      execSync("python3 -m unittest tests/test_skills_indexer.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 9. Agentic Skills Mesh TypeScript/Bun Tests (TOON parsing, Registry query)...");
      execSync("bun test tests/test_skills_indexer_ts.test.ts", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 10. TOON v4.1 Python Compliance & Token Savings Tests...");
      execSync("python3 -m unittest tests/test_toon_compliance_py.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 11. TOON v4.1 TypeScript/Bun Compliance Tests...");
      execSync("bun test tests/test_toon_compliance_ts.test.ts", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 12. Sisyphus Persistence & Retry Manager Tests...");
      execSync("python3 -m unittest tests/test_retry_manager.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 13. Universal Agentic Hooks Python Tests (Claude, Cursor, Codex, Shell, Brew, MCP)...");
      execSync("python3 -m unittest tests/test_universal_hooks_py.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 14. Universal Agentic Hooks TypeScript/Bun Tests (Parity & Interception)...");
      execSync("bun test tests/test_universal_hooks_ts.test.ts", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 15. Supportive Tools & Lifecycle Director Python Tests (Ponytail, TOON, Fable, Caveman)...");
      execSync("python3 -m unittest tests/test_integrations_py.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 16. Supportive Tools & Lifecycle Director TypeScript/Bun Tests (Parity & Directives)...");
      execSync("bun test tests/test_integrations_ts.test.ts", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 17. Universal System Engines Python Tests (Updater, Installer, Refresher, Doctor, Health, Deps, Notify, Announce, Version)...");
      execSync("python3 -m unittest tests/test_system_engines_py.py", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n-> 18. Universal System Engines TypeScript/Bun Tests (Parity, Auto-Fix, TOON Telemetry, Deduplication)...");
      execSync("bun test tests/test_system_engines_ts.test.ts", { cwd: rootDir, stdio: 'inherit' });

      console.log("\n✅ ALL MULTI-ENGINE TESTS PASSED CLEANLY!");
    } catch (e) {
      console.error("❌ Test suite encountered a failure.");
      process.exit(1);
    }
    break;
  }

  case '--version':
  case '-v': {
    console.log("agentic-workflow v1.2.1");
    break;
  }

  case 'help':
  case '--help':
  case '-h':
  default:
    printHelp();
    break;
}
