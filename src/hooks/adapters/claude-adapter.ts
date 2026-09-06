/**
 * Claude Code Hook Adapter (TypeScript / Bun)
 * ============================================
 * Consumes native Claude Code PreToolUse, PostToolUse, and Session hooks.
 */

import type { HookEvent, HookResult, HookType } from '../types.js';
import { UniversalPolicyEngine } from '../policy-engine.js';

export class ClaudeHookAdapter {
  constructor(private engine: UniversalPolicyEngine = new UniversalPolicyEngine()) {}

  parsePayload(rawInput: string | Record<string, any>, hookType: HookType = 'pre_tool'): HookEvent | null {
    try {
      const data = typeof rawInput === 'string' ? JSON.parse(rawInput) : rawInput;
      if (!data || typeof data !== 'object') return null;

      const toolName = data.tool_name || data.name;
      const toolInput = data.tool_input || data.input || {};
      const toolResponse = data.tool_response || data.output;

      let command: string | undefined;
      let filePath: string | undefined;

      if (typeof toolInput === 'object') {
        command = toolInput.command;
        filePath = toolInput.file_path || toolInput.path || toolInput.target;
      }

      return {
        event_id: `claude_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        source: 'claude',
        hook_type: hookType,
        timestamp: Date.now(),
        tool_name: toolName,
        command,
        file_path: filePath,
        args: typeof toolInput === 'object' ? toolInput : { raw: toolInput },
        output: toolResponse,
        metadata: { raw_claude_payload: data },
      };
    } catch {
      return null;
    }
  }

  handle(rawInput: string | Record<string, any>, hookType: HookType = 'pre_tool'): HookResult {
    const event = this.parsePayload(rawInput, hookType);
    if (!event) {
      return { event_id: 'claude_empty', verdict: 'allow', message: 'Empty payload', exit_code: 0 };
    }
    return this.engine.evaluate(event);
  }
}
