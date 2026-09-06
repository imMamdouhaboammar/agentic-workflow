/**
 * Google Antigravity & Gemini CLI Hook Driver Adapter (TypeScript / Bun)
 * =======================================================================
 * Consumes tool execution events from Google Antigravity and Gemini CLI environments.
 * Normalizes tool calls (run_command, write_to_file, replace_file_content, view_file, invoke_subagent)
 * into canonical HookEvent instances and applies UAHF policy engine gates.
 */

import type { HookEvent, HookResult, HookType } from '../types.js';
import { UniversalPolicyEngine } from '../policy-engine.js';

export class GeminiHookAdapter {
  constructor(private engine: UniversalPolicyEngine = new UniversalPolicyEngine()) {}

  parsePayload(rawInput: string | Record<string, any>, hookType: HookType = 'pre_tool'): HookEvent | null {
    try {
      const data = typeof rawInput === 'string' ? JSON.parse(rawInput) : rawInput;
      if (!data || typeof data !== 'object') return null;

      const toolName = data.tool_name || data.name || data.tool;
      const toolArgs = data.args || data.arguments || data.parameters || {};
      const toolResponse = data.response || data.output || data.result;

      let command: string | undefined;
      let filePath: string | undefined;

      if (typeof toolArgs === 'object') {
        command = toolArgs.CommandLine || toolArgs.command || toolArgs.cmd;
        filePath = toolArgs.AbsolutePath || toolArgs.TargetFile || toolArgs.file_path || toolArgs.path;
      }

      return {
        event_id: `gemini_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        source: 'antigravity',
        hook_type: hookType,
        timestamp: Date.now(),
        tool_name: toolName,
        command,
        file_path: filePath,
        args: typeof toolArgs === 'object' ? toolArgs : { raw: toolArgs },
        output: toolResponse,
        metadata: { raw_gemini_payload: data },
      };
    } catch {
      return null;
    }
  }

  handle(rawInput: string | Record<string, any>, hookType: HookType = 'pre_tool'): HookResult {
    const event = this.parsePayload(rawInput, hookType);
    if (!event) {
      return { event_id: 'gemini_empty', verdict: 'allow', message: 'Empty payload', exit_code: 0 };
    }
    return this.engine.evaluate(event);
  }

  evaluateToolCall(
    toolName: string,
    args: Record<string, any>,
    isPre: boolean = true,
    output?: any
  ): HookResult {
    const hookType: HookType = isPre ? 'pre_tool' : 'post_tool';
    const payload = {
      tool_name: toolName,
      args,
      output,
    };
    return this.handle(payload, hookType);
  }
}
