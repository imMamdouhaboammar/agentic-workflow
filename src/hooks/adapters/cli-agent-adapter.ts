/**
 * CLI Agent Wrapper & Interceptor Adapter (TypeScript / Bun)
 * ==========================================================
 * Supervises external CLI agents (OpenAI Codex, Moonshot Kimi, Cursor, Aider).
 */

import path from 'node:path';
import type { HookEvent, HookResult, HookSource } from '../types.js';
import { UniversalPolicyEngine } from '../policy-engine.js';

export class CliAgentAdapter {
  constructor(private engine: UniversalPolicyEngine = new UniversalPolicyEngine()) {}

  identifyAgentSource(binaryName: string): HookSource {
    const name = path.basename(binaryName).toLowerCase();
    if (name.includes('codex')) return 'codex';
    if (name.includes('kimi')) return 'kimi';
    if (name.includes('cursor')) return 'cursor';
    if (name.includes('antigravity')) return 'antigravity';
    if (name.includes('claude')) return 'claude';
    return 'cli';
  }

  evaluateAgentInvocation(commandArgs: string[]): HookResult {
    if (!commandArgs || commandArgs.length === 0) {
      return { event_id: 'empty_args', verdict: 'block', message: 'No command provided', exit_code: 1 };
    }

    const binary = commandArgs[0];
    const source = this.identifyAgentSource(binary);
    const fullCommand = commandArgs.join(' ');

    const event: HookEvent = {
      event_id: `cli_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      source,
      hook_type: 'session_start',
      timestamp: Date.now(),
      command: fullCommand,
      tool_name: binary,
      args: { raw_args: commandArgs.slice(1) },
      agent_id: `agent_${source}`,
    };

    return this.engine.evaluate(event);
  }
}
