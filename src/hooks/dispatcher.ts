/**
 * Universal Agentic Hooks Framework (UAHF) — Dispatcher (TypeScript / Bun)
 * =========================================================================
 * Central TypeScript coordinator for receiving, routing, evaluating, and auditing hook events.
 */

import fs from 'node:fs';
import path from 'node:path';
import type { HookEvent, HookResult } from './types.js';
import { UniversalPolicyEngine } from './policy-engine.js';
import { ClaudeHookAdapter } from './adapters/claude-adapter.js';
import { GeminiHookAdapter } from './adapters/gemini-adapter.js';
import { CursorHookAdapter } from './adapters/cursor-adapter.js';
import { CodexHookAdapter } from './adapters/codex-adapter.js';
import { ShellHookAdapter } from './adapters/shell-adapter.js';
import { HomebrewHookAdapter } from './adapters/homebrew-adapter.js';
import { McpHookProxy } from './adapters/mcp-proxy.js';
import { CliAgentAdapter } from './adapters/cli-agent-adapter.js';

export class HookDispatcher {
  public policyEngine: UniversalPolicyEngine;
  public claudeAdapter: ClaudeHookAdapter;
  public geminiAdapter: GeminiHookAdapter;
  public cursorAdapter: CursorHookAdapter;
  public codexAdapter: CodexHookAdapter;
  public shellAdapter: ShellHookAdapter;
  public homebrewAdapter: HomebrewHookAdapter;
  public mcpProxy: McpHookProxy;
  public cliAdapter: CliAgentAdapter;
  private ledgerFile: string;

  constructor(public projectDir: string = process.cwd()) {
    this.policyEngine = new UniversalPolicyEngine(this.projectDir);
    this.claudeAdapter = new ClaudeHookAdapter(this.policyEngine);
    this.geminiAdapter = new GeminiHookAdapter(this.policyEngine);
    this.cursorAdapter = new CursorHookAdapter(this.policyEngine);
    this.codexAdapter = new CodexHookAdapter(this.policyEngine);
    this.shellAdapter = new ShellHookAdapter(this.policyEngine);
    this.homebrewAdapter = new HomebrewHookAdapter(this.policyEngine);
    this.mcpProxy = new McpHookProxy(this.policyEngine);
    this.cliAdapter = new CliAgentAdapter(this.policyEngine);

    const traceDir = path.join(this.projectDir, '.traces');
    if (!fs.existsSync(traceDir)) {
      fs.mkdirSync(traceDir, { recursive: true });
    }
    this.ledgerFile = path.join(traceDir, 'hook_events.jsonl');
  }

  logEventLedger(event: HookEvent, result: HookResult) {
    const entry = {
      timestamp: Date.now() / 1000,
      event_id: event.event_id,
      source: event.source,
      hook_type: event.hook_type,
      tool: event.tool_name,
      command: event.command && event.command.length > 120 ? `${event.command.slice(0, 120)}...` : event.command,
      file: event.file_path,
      verdict: result.verdict,
      rule_id: result.rule_id,
      message: result.message,
    };
    try {
      fs.appendFileSync(this.ledgerFile, JSON.stringify(entry) + '\n');
    } catch {
      // Non-blocking audit failure isolation
    }
  }

  dispatch(event: HookEvent): HookResult {
    const result = this.policyEngine.evaluate(event);
    this.logEventLedger(event, result);
    return result;
  }

  getStatus() {
    let totalEvents = 0;
    let blockedEvents = 0;

    if (fs.existsSync(this.ledgerFile)) {
      const lines = fs.readFileSync(this.ledgerFile, 'utf-8').trim().split('\n');
      for (const line of lines) {
        if (!line.trim()) continue;
        totalEvents++;
        if (line.includes('"verdict":"block"') || line.includes('"verdict": "block"')) {
          blockedEvents++;
        }
      }
    }

    return {
      framework: 'Universal Agentic Hooks Framework (UAHF)',
      version: '1.0.0',
      runtime: 'TypeScript / Bun',
      active_policies: this.policyEngine.rules.map((r) => r.rule_id),
      supported_adapters: [
        'claude (native JSON)',
        'cursor (MDC + MCP)',
        'antigravity (MCP + shell)',
        'codex (wrapper + shell)',
        'kimi (wrapper + shell)',
        'bash / zsh / terminal (preexec/trap)',
        'homebrew (package gatekeeper)',
        'mcp (JSON-RPC stdio proxy)',
      ],
      ledger_path: this.ledgerFile,
      telemetry: {
        total_events_intercepted: totalEvents,
        blocked_events: blockedEvents,
      },
    };
  }
}
