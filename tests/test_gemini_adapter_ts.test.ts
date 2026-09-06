import { describe, expect, it } from 'bun:test';
import { GeminiHookAdapter } from '../src/hooks/adapters/gemini-adapter.js';
import { UniversalPolicyEngine } from '../src/hooks/policy-engine.js';

describe('Google Antigravity & Gemini CLI Hook Driver Adapter (TypeScript / Bun)', () => {
  const engine = new UniversalPolicyEngine();
  const adapter = new GeminiHookAdapter(engine);

  it('parses Antigravity run_command payload correctly', () => {
    const payload = {
      tool_name: 'run_command',
      args: {
        CommandLine: 'bun test',
        Cwd: '.',
      },
    };
    const event = adapter.parsePayload(payload, 'pre_tool');
    expect(event).not.toBeNull();
    expect(event?.source).toBe('antigravity');
    expect(event?.tool_name).toBe('run_command');
    expect(event?.command).toBe('bun test');
  });

  it('blocks dangerous commands passed through Antigravity tool call', () => {
    const payload = {
      tool_name: 'run_command',
      args: {
        CommandLine: 'rm -rf / --no-preserve-root',
      },
    };
    const result = adapter.handle(payload, 'pre_tool');
    expect(result.verdict).toBe('block');
    expect(result.message).toContain('DESTRUCTIVE COMMAND BLOCKED');
  });

  it('evaluates tool call helper for benign and blocked actions', () => {
    const allowRes = adapter.evaluateToolCall('run_command', { CommandLine: 'git status' });
    expect(allowRes.verdict).toBe('allow');

    const blockRes = adapter.evaluateToolCall('run_command', { CommandLine: 'git reset --hard HEAD~5' });
    expect(blockRes.verdict).toBe('block');
  });

  it('extracts target file from write_to_file payload', () => {
    const payload = {
      tool_name: 'write_to_file',
      args: {
        TargetFile: '/Users/test/workspace/file.ts',
        CodeContent: 'export const x = 1;',
      },
    };
    const event = adapter.parsePayload(payload, 'pre_tool');
    expect(event).not.toBeNull();
    expect(event?.file_path).toBe('/Users/test/workspace/file.ts');
  });
});
