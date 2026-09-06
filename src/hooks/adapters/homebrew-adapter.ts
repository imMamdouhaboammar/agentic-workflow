/**
 * Homebrew Package Manager Hook Adapter (TypeScript / Bun)
 * =========================================================
 * Dedicated gatekeeper for Homebrew command interception and package hygiene.
 */

import type { HookEvent, HookResult } from '../types.js';
import { UniversalPolicyEngine } from '../policy-engine.js';

export class HomebrewHookAdapter {
  constructor(private engine: UniversalPolicyEngine = new UniversalPolicyEngine()) {}

  evaluateBrewArgs(args: string[]): HookResult {
    const fullCommand = `brew ${args.join(' ')}`.trim();
    let packageTarget: string | undefined;

    for (let i = 0; i < args.length; i++) {
      if (['install', 'reinstall', 'cask'].includes(args[i]) && i + 1 < args.length) {
        packageTarget = args[i + 1];
        break;
      }
    }

    const event: HookEvent = {
      event_id: `brew_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      source: 'homebrew',
      hook_type: 'pre_command',
      timestamp: Date.now(),
      command: fullCommand,
      tool_name: 'homebrew',
      args: { raw_args: args, package: packageTarget },
    };

    return this.engine.evaluate(event);
  }
}
