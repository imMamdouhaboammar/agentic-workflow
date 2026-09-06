/**
 * Universal Agentic Hooks Framework (UAHF) — Policy Engine (TypeScript/Bun)
 * =========================================================================
 * Deterministic policy evaluator matching Python engine rules with sub-millisecond execution.
 */

import fs from 'node:fs';
import path from 'node:path';
import type { HookEvent, HookResult, PolicyRule } from './types.js';

export class DestructiveCommandRule implements PolicyRule {
  rule_id = 'SEC-001-DESTRUCTIVE-COMMAND';
  description = 'Blocks destructive system, git, and exfiltration commands';

  private networkPatterns = [
    { regex: /\bcurl\b.*\|\s*(ba)?sh\b/, msg: 'curl piped to shell is blocked. Download, inspect, and execute manually.' },
    { regex: /\bwget\b.*\|\s*(ba)?sh\b/, msg: 'wget piped to shell is blocked. Download, inspect, and execute manually.' },
  ];

  private systemPatterns = [
    { regex: /\bdd\b\s+if=/, msg: 'dd command with raw input file is blocked. Irreversible disk write risk.' },
    { regex: /\bmkfs\b/, msg: 'mkfs command is blocked. Filesystem formatting destroys all data.' },
  ];

  private gitPatterns = [
    { regex: /\bgit\s+push\b.*(?<![-\w])--force(?![-\w])/, msg: 'git push --force is blocked. Use --force-with-lease to protect remote history.' },
    { regex: /\bgit\s+push\b.*\s-[a-zA-Z]*f/, msg: 'git push -f is blocked. Use --force-with-lease to protect remote history.' },
    { regex: /\bgit\s+reset\b.*\s--hard\b/, msg: 'git reset --hard is blocked. Discards uncommitted work permanently.' },
    { regex: /\bgit\s+checkout\b\s+(?:--\s+)?\./, msg: 'git checkout . is blocked. Discards unstaged modifications.' },
    { regex: /\bgit\s+restore\b\s+\./, msg: 'git restore . is blocked. Discards unstaged modifications.' },
    { regex: /\bgit\s+clean\b.*\s-[a-zA-Z]*f/, msg: 'git clean -f is blocked. Permanently deletes untracked files.' },
    { regex: /\bgit\s+branch\b.*\s-D\b/, msg: 'git branch -D is blocked. Use git branch -d for safe deletion.' },
    { regex: /\bgit\s+branch\b.*\s--delete\b.*\s--force\b/, msg: 'git branch --delete --force is blocked. Use git branch -d for safe deletion.' },
  ];

  private dangerousTargets = new Set(['/', '/*', '~', '~/', '$HOME', '$HOME/', '$HOME/*']);

  private checkDangerousRm(subCommand: string): string | null {
    const tokens = subCommand.trim().split(/\s+/);
    if (!tokens.length || tokens[0] !== 'rm') return null;

    let flags = '';
    const targets: string[] = [];

    for (let i = 1; i < tokens.length; i++) {
      const t = tokens[i];
      if (t.startsWith('-') && !t.startsWith('--')) {
        flags += t.slice(1);
      } else if (!t.startsWith('-')) {
        targets.push(t.replace(/^['"]|['"]$/g, ''));
      }
    }

    const hasRecursive = flags.includes('r') || flags.includes('R');
    const hasForce = flags.includes('f');

    if (!hasRecursive || !hasForce) return null;

    for (const tgt of targets) {
      if (this.dangerousTargets.has(tgt)) {
        return `rm -rf targeting ${tgt} is blocked. Catastrophic, irreversible file deletion.`;
      }
    }
    return null;
  }

  evaluate(event: HookEvent): HookResult | null {
    const cmd = event.command || (event.args?.command as string);
    if (!cmd || typeof cmd !== 'string') return null;

    for (const { regex, msg } of this.networkPatterns) {
      if (regex.test(cmd)) {
        return {
          event_id: event.event_id,
          verdict: 'block',
          message: `DESTRUCTIVE COMMAND BLOCKED: ${msg}`,
          exit_code: 2,
          rule_id: this.rule_id,
        };
      }
    }

    for (const { regex, msg } of this.systemPatterns) {
      if (regex.test(cmd)) {
        return {
          event_id: event.event_id,
          verdict: 'block',
          message: `DESTRUCTIVE COMMAND BLOCKED: ${msg}`,
          exit_code: 2,
          rule_id: this.rule_id,
        };
      }
    }

    for (const { regex, msg } of this.gitPatterns) {
      if (regex.test(cmd)) {
        return {
          event_id: event.event_id,
          verdict: 'block',
          message: `DESTRUCTIVE COMMAND BLOCKED: ${msg}`,
          exit_code: 2,
          rule_id: this.rule_id,
        };
      }
    }

    const subCommands = cmd.split(/\s*(?:&&|\|\||;)\s*/);
    for (const sc of subCommands) {
      for (const seg of sc.split('|')) {
        const rmErr = this.checkDangerousRm(seg);
        if (rmErr) {
          return {
            event_id: event.event_id,
            verdict: 'block',
            message: `DESTRUCTIVE COMMAND BLOCKED: ${rmErr}`,
            exit_code: 2,
            rule_id: this.rule_id,
          };
        }
      }
    }

    return null;
  }
}

export class PackagePolicyRule implements PolicyRule {
  rule_id = 'PKG-002-PACKAGE-HYGIENE';
  description = 'Enforces container and package manager governance policies';

  private forbiddenPackages: Record<string, string> = {
    colima: 'Colima is prohibited per project constitution due to large footprint. Use lightweight alternatives.',
  };

  private brewInstallRegex = /\bbrew\s+(?:install|reinstall|cask)\s+([^\s;]+)/i;
  private sudoBrewRegex = /\bsudo\s+brew\b/i;

  evaluate(event: HookEvent): HookResult | null {
    const cmd = event.command || (event.args?.command as string);
    const argsTarget = (event.args?.target || event.args?.package) as string;

    if (cmd && typeof cmd === 'string') {
      if (this.sudoBrewRegex.test(cmd)) {
        return {
          event_id: event.event_id,
          verdict: 'block',
          message: "PACKAGE POLICY VIOLATION: 'sudo brew' is prohibited. Homebrew must not run as root.",
          exit_code: 2,
          rule_id: this.rule_id,
        };
      }

      const match = cmd.match(this.brewInstallRegex);
      if (match) {
        const pkgCandidate = match[1].toLowerCase().replace(/^['"]|['"]$/g, '');
        for (const [forbidden, reason] of Object.entries(this.forbiddenPackages)) {
          if (pkgCandidate.includes(forbidden)) {
            return {
              event_id: event.event_id,
              verdict: 'block',
              message: `PACKAGE POLICY VIOLATION: Package '${forbidden}' is blocked. ${reason}`,
              exit_code: 2,
              rule_id: this.rule_id,
            };
          }
        }
      }
    }

    if (argsTarget && typeof argsTarget === 'string') {
      const tgt = argsTarget.toLowerCase();
      for (const [forbidden, reason] of Object.entries(this.forbiddenPackages)) {
        if (tgt === forbidden || tgt.includes(forbidden)) {
          return {
            event_id: event.event_id,
            verdict: 'block',
            message: `PACKAGE POLICY VIOLATION: Package '${forbidden}' is blocked. ${reason}`,
            exit_code: 2,
            rule_id: this.rule_id,
          };
        }
      }
    }

    return null;
  }
}

export class SensitiveFileRule implements PolicyRule {
  rule_id = 'SEC-003-SENSITIVE-FILES';
  description = 'Prevents tampering with credentials, environment secrets, and private keys';

  private sensitivePatterns = [
    { regex: /(^|[/\\])\.env(\.[a-zA-Z0-9_-]+)?$/, label: 'Environment secret file (.env)' },
    { regex: /\.(pem|key|p12|pfx)$/i, label: 'Private key or certificate' },
    { regex: /(^|[/\\])id_(rsa|ed25519|ecdsa|dsa)$/, label: 'SSH private key' },
    { regex: /(^|[/\\])(credentials|secrets|passwords)\.(json|ya?ml|toml)$/i, label: 'Secrets store' },
    { regex: /(^|[/\\])(service[-_]?account|token)\.json$/i, label: 'Service account / Token file' },
    { regex: /\.(tfstate|tfvars)$/i, label: 'Terraform state / variable secrets' },
  ];

  evaluate(event: HookEvent): HookResult | null {
    const filePath = event.file_path || (event.args?.file_path as string) || (event.args?.path as string);
    if (!filePath || typeof filePath !== 'string') return null;

    for (const { regex, label } of this.sensitivePatterns) {
      if (regex.test(filePath)) {
        return {
          event_id: event.event_id,
          verdict: 'warn',
          message: `SECURITY ADVISORY: Access/modification to sensitive file '${filePath}' (${label}).`,
          exit_code: 0,
          rule_id: this.rule_id,
        };
      }
    }
    return null;
  }
}

export class TddIntegrityRule implements PolicyRule {
  rule_id = 'GOV-004-TDD-INTEGRITY';
  description = 'Protects test files from modification during implementation phases';

  private testFilePatterns = [
    /(^|[/\\])test_[^/\\]+\.py$/,
    /[._]test\.[jt]sx?$/,
    /[._]spec\.[jt]sx?$/,
  ];

  constructor(private projectDir: string = process.cwd()) {}

  isGuardActive(): boolean {
    return (
      fs.existsSync(path.join(this.projectDir, '.tdd-guard')) ||
      fs.existsSync(path.join(process.cwd(), '.tdd-guard'))
    );
  }

  evaluate(event: HookEvent): HookResult | null {
    if (!this.isGuardActive()) return null;

    const filePath = event.file_path || (event.args?.file_path as string) || (event.args?.path as string);
    if (!filePath || typeof filePath !== 'string') return null;

    const tool = (event.tool_name || '').toLowerCase();
    if (!tool.includes('edit') && !tool.includes('write')) return null;

    for (const pattern of this.testFilePatterns) {
      if (pattern.test(filePath)) {
        return {
          event_id: event.event_id,
          verdict: 'block',
          message: `TDD GUARD ACTIVE: Modification of test file '${filePath}' is blocked. Modify implementation code to make tests pass.`,
          exit_code: 2,
          rule_id: this.rule_id,
        };
      }
    }
    return null;
  }
}

export class SecretLeakRule implements PolicyRule {
  rule_id = 'SEC-005-SECRET-LEAK-FILTER';
  description = 'Detects and blocks leakage of API keys and authentication tokens in telemetry';

  private patterns = [
    { regex: /sk-(?:proj|ant|live)-[a-zA-Z0-9_\-]{20,}/, label: 'OpenAI / Anthropic API Key' },
    { regex: /AKIA[0-9A-Z]{16}/, label: 'AWS Access Key ID' },
    { regex: /gh[pousr][_-][A-Za-z0-9_]{36,255}/, label: 'GitHub Personal Access Token' },
    { regex: /xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32}/, label: 'Slack Token' },
    { regex: /-----BEGIN (?:RSA )?PRIVATE KEY-----/, label: 'Private Cryptographic Key' },
  ];

  evaluate(event: HookEvent): HookResult | null {
    if (!event.output) return null;
    const text = typeof event.output === 'string' ? event.output : JSON.stringify(event.output);

    for (const { regex, label } of this.patterns) {
      if (regex.test(text)) {
        return {
          event_id: event.event_id,
          verdict: 'warn',
          message: `SECRET LEAK DETECTED: ${label} found in output stream. Redacting.`,
          exit_code: 0,
          rule_id: this.rule_id,
          metadata: { leak_type: label },
        };
      }
    }
    return null;
  }
}

export class CircuitBreakerRule implements PolicyRule {
  rule_id = 'RES-006-CIRCUIT-BREAKER';
  description = 'Halts speculative retry loops when failure threshold is exceeded';

  private streakCounters: Map<string, number> = new Map();

  constructor(private failureThreshold: number = 2) {}

  recordFailure(agentId: string) {
    const current = this.streakCounters.get(agentId) || 0;
    this.streakCounters.set(agentId, current + 1);
  }

  recordSuccess(agentId: string) {
    this.streakCounters.set(agentId, 0);
  }

  evaluate(event: HookEvent): HookResult | null {
    const agentId = event.agent_id || 'default_agent';
    const streak = this.streakCounters.get(agentId) || 0;
    if (streak >= this.failureThreshold) {
      return {
        event_id: event.event_id,
        verdict: 'block',
        message: `CIRCUIT BREAKER TRIPPED: Agent '${agentId}' has ${streak} consecutive failures. Halting speculative edits. Run Abductive Diagnosis before retrying.`,
        exit_code: 2,
        rule_id: this.rule_id,
      };
    }
    return null;
  }
}

export class UniversalPolicyEngine {
  public rules: PolicyRule[];

  constructor(public projectDir: string = process.cwd()) {
    this.rules = [
      new DestructiveCommandRule(),
      new PackagePolicyRule(),
      new SensitiveFileRule(),
      new TddIntegrityRule(this.projectDir),
      new SecretLeakRule(),
      new CircuitBreakerRule(),
    ];
  }

  addRule(rule: PolicyRule) {
    this.rules.push(rule);
  }

  evaluate(event: HookEvent): HookResult {
    const warnings: string[] = [];
    for (const rule of this.rules) {
      const res = rule.evaluate(event);
      if (res) {
        if (res.verdict === 'block') {
          return res;
        } else if (res.verdict === 'warn') {
          warnings.push(res.message);
        }
      }
    }

    if (warnings.length > 0) {
      return {
        event_id: event.event_id,
        verdict: 'warn',
        message: warnings.join('; '),
        exit_code: 0,
      };
    }

    return {
      event_id: event.event_id,
      verdict: 'allow',
      message: 'Operation allowed by policy',
      exit_code: 0,
    };
  }
}
