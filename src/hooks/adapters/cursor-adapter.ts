/**
 * Cursor IDE & Windsurf Hook Driver Adapter (TypeScript / Bun)
 * ==============================================================
 * Consumes tool execution and terminal command events from Cursor IDE rules (.cursor/rules)
 * and Windsurf cascades. Normalizes events to HookEvent(source='cursor') and applies
 * governance policies.
 */

import type { HookEvent, HookResult, HookType } from '../types.js';
import { UniversalPolicyEngine } from '../policy-engine.js';

export class CursorHookAdapter {
  constructor(private engine: UniversalPolicyEngine = new UniversalPolicyEngine()) {}

  parsePayload(rawInput: string | Record<string, any>, hookType: HookType = 'pre_tool'): HookEvent | null {
    try {
      const data = typeof rawInput === 'string' ? JSON.parse(rawInput) : rawInput;
      if (!data || typeof data !== 'object') return null;

      const toolName = data.tool || data.tool_name || data.action;
      let command: string | undefined = data.command || data.cmd;
      let filePath: string | undefined = data.file_path || data.path || data.target_file;
      const toolArgs = data.args || data.parameters || {};
      const output = data.output || data.result;

      if (typeof toolArgs === 'object') {
        if (!command) command = toolArgs.command || toolArgs.cmd;
        if (!filePath) filePath = toolArgs.file_path || toolArgs.path || toolArgs.target_file;
      }

      return {
        event_id: `cursor_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        source: 'cursor',
        hook_type: hookType,
        timestamp: Date.now(),
        tool_name: toolName || (command ? 'terminal' : 'file_op'),
        command,
        file_path: filePath,
        args: typeof toolArgs === 'object' ? toolArgs : { raw: toolArgs },
        output,
        metadata: { raw_cursor_payload: data },
      };
    } catch {
      return null;
    }
  }

  handle(rawInput: string | Record<string, any>, hookType: HookType = 'pre_tool'): HookResult {
    const event = this.parsePayload(rawInput, hookType);
    if (!event) {
      return { event_id: 'cursor_empty', verdict: 'allow', message: 'Empty payload', exit_code: 0 };
    }
    return this.engine.evaluate(event);
  }

  evaluateCommand(commandLine: string, isPre: boolean = true, output?: string): HookResult {
    const hookType: HookType = isPre ? 'pre_command' : 'post_command';
    return this.handle({ command: commandLine, output }, hookType);
  }
}
