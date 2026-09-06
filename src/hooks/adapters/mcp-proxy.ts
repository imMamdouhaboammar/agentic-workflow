/**
 * Universal MCP (Model Context Protocol) Hook Proxy (TypeScript / Bun)
 * ====================================================================
 * Intercepts JSON-RPC tool calls for Cursor, Antigravity, Claude, Codex, and Kimi.
 */

import type { HookEvent, HookResult } from '../types.js';
import { UniversalPolicyEngine } from '../policy-engine.js';

export class McpHookProxy {
  constructor(private engine: UniversalPolicyEngine = new UniversalPolicyEngine()) {}

  inspectRequest(message: Record<string, any>): Record<string, any> | null {
    if (message.method !== 'tools/call') return null;

    const params = message.params || {};
    const toolName = params.name;
    const toolArgs = params.arguments || {};

    const event: HookEvent = {
      event_id: `mcp_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      source: 'mcp',
      hook_type: 'pre_tool',
      timestamp: Date.now(),
      tool_name: toolName,
      command: toolArgs.command || toolArgs.cmd,
      file_path: toolArgs.path || toolArgs.file_path,
      args: toolArgs,
    };

    const result = this.engine.evaluate(event);
    if (result.verdict === 'block') {
      return {
        jsonrpc: '2.0',
        id: message.id,
        error: {
          code: -32000,
          message: `MCP Tool Execution Blocked by Policy: ${result.message}`,
          data: { rule_id: result.rule_id, verdict: 'blocked' },
        },
      };
    }
    return null;
  }

  inspectResponse(response: Record<string, any>): Record<string, any> {
    const resultPayload = response.result;
    if (!resultPayload) return response;

    const event: HookEvent = {
      event_id: `mcp_resp_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      source: 'mcp',
      hook_type: 'post_tool',
      timestamp: Date.now(),
      output: resultPayload,
    };

    const res = this.engine.evaluate(event);
    if (res.verdict === 'warn' && res.message.includes('SECRET LEAK DETECTED')) {
      if (typeof resultPayload === 'object' && resultPayload !== null) {
        resultPayload._security_advisory = res.message;
      }
    }
    return response;
  }
}
