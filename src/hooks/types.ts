/**
 * Universal Agentic Hooks Framework (UAHF) — TypeScript Types & Data Models
 * =========================================================================
 * Canonical types for multi-platform hook events, verdicts, and policies in Bun/TypeScript.
 */

export type HookSource =
  | 'claude'
  | 'cursor'
  | 'antigravity'
  | 'codex'
  | 'kimi'
  | 'bash'
  | 'terminal'
  | 'homebrew'
  | 'mcp'
  | 'cli';

export type HookType =
  | 'pre_tool'
  | 'post_tool'
  | 'pre_command'
  | 'post_command'
  | 'session_start'
  | 'session_end'
  | 'error_trap';

export type HookVerdict = 'allow' | 'block' | 'mutate' | 'warn' | 'ask_user';

export interface HookEvent {
  event_id: string;
  source: HookSource;
  hook_type: HookType;
  timestamp: number;
  tool_name?: string;
  command?: string;
  args?: Record<string, any>;
  output?: any;
  file_path?: string;
  cwd?: string;
  env?: Record<string, string>;
  agent_id?: string;
  metadata?: Record<string, any>;
}

export interface HookResult {
  event_id: string;
  verdict: HookVerdict;
  message: string;
  exit_code: number;
  mutated_input?: Record<string, any>;
  mutated_command?: string;
  rule_id?: string;
  metadata?: Record<string, any>;
}

export interface PolicyRule {
  rule_id: string;
  description: string;
  evaluate(event: HookEvent): HookResult | null;
}
