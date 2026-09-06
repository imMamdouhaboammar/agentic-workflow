/**
 * OpenAI Codex & ChatGPT Plugin Hook Driver Adapter (TypeScript / Bun)
 * ====================================================================
 * Consumes execution events from OpenAI Codex and ChatGPT plugin environments.
 * Normalizes events to HookEvent(source='codex') and applies sandbox security
 * and governance policies.
 */

import type { HookEvent, HookResult, HookType } from '../types.js';
import { UniversalPolicyEngine } from '../policy-engine.js';

export class CodexHookAdapter {
  constructor(private engine: UniversalPolicyEngine = new UniversalPolicyEngine()) {}

  parsePayload(rawInput: string | Record<string, any>, hookType: HookType = 'pre_tool'): HookEvent | null {
    try {
      const data = typeof rawInput === 'string' ? JSON.parse(rawInput) : rawInput;
      if (!data || typeof data !== 'object') return null;

      const toolName = data.name || data.tool_name || data.function;
      let toolArgs = data.arguments || data.args || data.input || {};
      const output = data.output || data.response;

      if (typeof toolArgs === 'string') {
        try {
          toolArgs = JSON.parse(toolArgs);
        } catch {
          toolArgs = { raw: toolArgs };
        }
      }

      let command: string | undefined;
      let filePath: string | undefined;

      if (typeof toolArgs === 'object') {
        command = toolArgs.command || toolArgs.cmd || toolArgs.code;
        filePath = toolArgs.path || toolArgs.file_path || toolArgs.filename;
      }

      return {
        event_id: `codex_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        source: 'codex',
        hook_type: hookType,
        timestamp: Date.now(),
        tool_name: toolName || (command ? 'exec' : 'plugin_call'),
        command,
        file_path: filePath,
        args: typeof toolArgs === 'object' ? toolArgs : { raw: toolArgs },
        output,
        metadata: { raw_codex_payload: data },
      };
    } catch {
      return null;
    }
  }

  handle(rawInput: string | Record<string, any>, hookType: HookType = 'pre_tool'): HookResult {
    const event = this.parsePayload(rawInput, hookType);
    if (!event) {
      return { event_id: 'codex_empty', verdict: 'allow', message: 'Empty payload', exit_code: 0 };
    }
    return this.engine.evaluate(event);
  }

  evaluateTool(name: string, args: Record<string, any>, isPre: boolean = true, output?: any): HookResult {
    const hookType: HookType = isPre ? 'pre_tool' : 'post_tool';
    return this.handle({ name, arguments: args, output }, hookType);
  }
}
