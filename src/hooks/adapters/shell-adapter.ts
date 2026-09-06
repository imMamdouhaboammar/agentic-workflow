/**
 * Shell & Terminal Hook Adapter (TypeScript / Bun)
 * ===============================================
 * Intercepts commands in Bash, Zsh, and Terminal environments.
 */

import type { HookEvent, HookResult, HookSource, HookType } from '../types.js';
import { UniversalPolicyEngine } from '../policy-engine.js';

export class ShellHookAdapter {
  constructor(private engine: UniversalPolicyEngine = new UniversalPolicyEngine()) {}

  createEvent(
    command: string,
    hookType: HookType = 'pre_command',
    source: HookSource = 'bash',
    cwd: string = process.cwd()
  ): HookEvent {
    return {
      event_id: `shell_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      source,
      hook_type: hookType,
      timestamp: Date.now(),
      command: command.trim(),
      tool_name: 'bash',
      cwd,
      env: { ...process.env } as Record<string, string>,
    };
  }

  evaluateCommand(
    command: string,
    hookType: HookType = 'pre_command',
    source: HookSource = 'bash'
  ): HookResult {
    if (!command || !command.trim()) {
      return { event_id: 'empty_cmd', verdict: 'allow', message: 'Empty command', exit_code: 0 };
    }
    const event = this.createEvent(command, hookType, source);
    return this.engine.evaluate(event);
  }
}
