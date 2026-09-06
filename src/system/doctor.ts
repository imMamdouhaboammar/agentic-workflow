/**
 * src/system/doctor.ts — Doctor Diagnostic & Automated Remediation Engine
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execSync } from 'node:child_process';
import type { DoctorCheckItem, DoctorReport, FixResult } from './types.ts';

export class DoctorEngine {
  private projectDir: string;
  private homeDir: string;

  constructor(projectDir: string = '.') {
    this.projectDir = path.resolve(projectDir);
    this.homeDir = os.homedir();
  }

  private runCmd(cmd: string): { ok: boolean; stdout: string } {
    try {
      const out = execSync(cmd, { cwd: this.projectDir, stdio: 'pipe', encoding: 'utf-8' }).trim();
      return { ok: true, stdout: out };
    } catch {
      return { ok: false, stdout: '' };
    }
  }

  public diagnose(): DoctorReport {
    const checks: DoctorCheckItem[] = [];

    // 1. Runtime Checks
    // Bun
    const bunCheck = this.runCmd('bun --version');
    if (bunCheck.ok) {
      checks.push({
        id: 'runtime-bun',
        category: 'runtime',
        title: 'Bun JavaScript/TypeScript Runtime',
        status: 'PASS',
        details: `Bun v${bunCheck.stdout} installed and online.`,
        fixable: false
      });
    } else {
      checks.push({
        id: 'runtime-bun',
        category: 'runtime',
        title: 'Bun JavaScript/TypeScript Runtime',
        status: 'FAIL',
        details: 'Bun runtime is not installed or not in PATH.',
        recommendation: 'Install Bun via: curl -fsSL https://bun.sh/install | bash',
        fixable: false
      });
    }

    // Node
    const nodeCheck = this.runCmd('node --version');
    if (nodeCheck.ok) {
      checks.push({
        id: 'runtime-node',
        category: 'runtime',
        title: 'Node.js Runtime',
        status: 'PASS',
        details: `Node.js ${nodeCheck.stdout} detected.`,
        fixable: false
      });
    } else {
      checks.push({
        id: 'runtime-node',
        category: 'runtime',
        title: 'Node.js Runtime',
        status: 'WARN',
        details: 'Node.js runtime not found. Bun will be used as primary engine.',
        fixable: false
      });
    }

    // Python 3
    const pyCheck = this.runCmd('python3 --version');
    if (pyCheck.ok) {
      checks.push({
        id: 'runtime-python',
        category: 'runtime',
        title: 'Python 3 Runtime',
        status: 'PASS',
        details: `${pyCheck.stdout} detected and available for dual engine parity.`,
        fixable: false
      });
    } else {
      checks.push({
        id: 'runtime-python',
        category: 'runtime',
        title: 'Python 3 Runtime',
        status: 'FAIL',
        details: 'Python 3 is required for deterministic verification hooks and SOT validation.',
        recommendation: 'Install Python 3.10+ via brew install python3 or package manager.',
        fixable: false
      });
    }

    // 2. CLI & PATH Checks
    const cliPath = path.join(this.projectDir, 'bin', 'cli.js');
    if (fs.existsSync(cliPath)) {
      try {
        const stats = fs.statSync(cliPath);
        const isExecutable = !!(stats.mode & 0o111);
        checks.push({
          id: 'cli-permission',
          category: 'cli',
          title: 'CLI Executable Permission (bin/cli.js)',
          status: isExecutable ? 'PASS' : 'WARN',
          details: isExecutable ? 'bin/cli.js has executable bit set.' : 'bin/cli.js lacks execute permission.',
          recommendation: 'Run: chmod +x bin/cli.js',
          fixable: !isExecutable
        });
      } catch {
        // Ignore
      }
    } else {
      checks.push({
        id: 'cli-permission',
        category: 'cli',
        title: 'CLI Executable Permission (bin/cli.js)',
        status: 'FAIL',
        details: 'bin/cli.js not found in project repository.',
        fixable: false
      });
    }

    const localBin = path.join(this.homeDir, '.local', 'bin', 'agentic-workflow');
    const usrBin = '/usr/local/bin/agentic-workflow';
    const isLinked = fs.existsSync(localBin) || fs.existsSync(usrBin);
    checks.push({
      id: 'cli-symlink',
      category: 'cli',
      title: 'Global CLI Binary Symlink',
      status: isLinked ? 'PASS' : 'WARN',
      details: isLinked ? `Linked at ${fs.existsSync(localBin) ? localBin : usrBin}` : 'CLI binary is not symlinked into user PATH.',
      recommendation: 'Run agentic-workflow install or doctor --fix to link binary.',
      fixable: !isLinked
    });

    // 3. Git Repository Checks
    const gitDir = path.join(this.projectDir, '.git');
    if (fs.existsSync(gitDir)) {
      const branchCheck = this.runCmd('git rev-parse --abbrev-ref HEAD');
      checks.push({
        id: 'git-repo',
        category: 'git',
        title: 'Git Version Control & Tracking',
        status: 'PASS',
        details: `Git repository active on branch '${branchCheck.stdout || 'main'}'.`,
        fixable: false
      });
    } else {
      checks.push({
        id: 'git-repo',
        category: 'git',
        title: 'Git Version Control & Tracking',
        status: 'WARN',
        details: 'No .git directory found. Auto-updater requires git tracking.',
        recommendation: 'Initialize git repository: git init',
        fixable: false
      });
    }

    // 4. Dependencies Checks
    const nodeModules = path.join(this.projectDir, 'node_modules');
    const toonModule = path.join(this.projectDir, 'node_modules', '@toon-format', 'toon');
    const hasDeps = fs.existsSync(nodeModules) && fs.existsSync(toonModule);
    checks.push({
      id: 'dependencies-npm',
      category: 'dependencies',
      title: 'Node/Bun Dependencies (@toon-format/toon)',
      status: hasDeps ? 'PASS' : 'WARN',
      details: hasDeps ? 'Dependencies installed and verified.' : 'node_modules missing or @toon-format/toon not installed.',
      recommendation: 'Run bun install to resolve dependencies.',
      fixable: !hasDeps
    });

    // 5. State & SOT Checks
    const sotPath = path.join(this.projectDir, 'state.yaml');
    if (fs.existsSync(sotPath)) {
      const content = fs.readFileSync(sotPath, 'utf-8');
      const hasCore = content.includes('workflow:') && content.includes('current_step:');
      checks.push({
        id: 'state-sot',
        category: 'state',
        title: 'Single Source of Truth (state.yaml)',
        status: hasCore ? 'PASS' : 'WARN',
        details: hasCore ? 'state.yaml is present with valid workflow structure.' : 'state.yaml is missing core schema fields.',
        recommendation: 'Run agentic-workflow validate or doctor --fix.',
        fixable: !hasCore
      });
    } else {
      checks.push({
        id: 'state-sot',
        category: 'state',
        title: 'Single Source of Truth (state.yaml)',
        status: 'WARN',
        details: 'state.yaml not found. Workflow is in idle state ready for new plan.',
        fixable: false
      });
    }

    // 6. UAHF Hooks & Ledger Checks
    const hooksDir = path.join(this.projectDir, '.claude', 'hooks', 'scripts');
    const hasHooks = fs.existsSync(path.join(hooksDir, 'context_guard.py')) && fs.existsSync(path.join(hooksDir, 'block_destructive_commands.py'));
    checks.push({
      id: 'hooks-uahf',
      category: 'hooks',
      title: 'Universal Agentic Hooks Framework Scripts',
      status: hasHooks ? 'PASS' : 'FAIL',
      details: hasHooks ? 'UAHF deterministic verification and safety hooks present.' : 'UAHF hook scripts missing.',
      fixable: false
    });

    const ledgerFile = path.join(this.projectDir, 'ledger.jsonl');
    let ledgerWritable = false;
    try {
      if (!fs.existsSync(ledgerFile)) {
        fs.writeFileSync(ledgerFile, '');
      }
      fs.accessSync(ledgerFile, fs.constants.W_OK);
      ledgerWritable = true;
    } catch {
      ledgerWritable = false;
    }
    checks.push({
      id: 'hooks-ledger',
      category: 'hooks',
      title: 'Audit Ledger (ledger.jsonl)',
      status: ledgerWritable ? 'PASS' : 'WARN',
      details: ledgerWritable ? 'ledger.jsonl is writable.' : 'ledger.jsonl cannot be written.',
      fixable: !ledgerWritable
    });

    // 7. Skills Mesh Checks
    const skillsJson = path.join(this.projectDir, 'skills-index.json');
    const skillsToon = path.join(this.projectDir, 'skills-index.toon');
    const hasSkillsIndex = fs.existsSync(skillsJson) && fs.existsSync(skillsToon);
    checks.push({
      id: 'skills-mesh',
      category: 'skills',
      title: 'Agentic Skills Mesh Index (JSON & TOON)',
      status: hasSkillsIndex ? 'PASS' : 'WARN',
      details: hasSkillsIndex ? 'Dual skills index synchronized.' : 'skills-index.json or skills-index.toon missing.',
      recommendation: 'Run agentic-workflow skills index or doctor --fix.',
      fixable: !hasSkillsIndex
    });

    // 8. Supportive Integrations Checks
    const integrationsFile = path.join(this.projectDir, 'integrations.json');
    const hasIntegrations = fs.existsSync(integrationsFile);
    checks.push({
      id: 'integrations-registry',
      category: 'integrations',
      title: 'Supportive Tools Registry (integrations.json)',
      status: hasIntegrations ? 'PASS' : 'WARN',
      details: hasIntegrations ? 'integrations.json present.' : 'integrations.json missing.',
      fixable: !hasIntegrations
    });

    // 9. Security Checks
    const gitignore = path.join(this.projectDir, '.gitignore');
    const hasGitignore = fs.existsSync(gitignore) && fs.readFileSync(gitignore, 'utf-8').includes('.env');
    checks.push({
      id: 'security-env-guard',
      category: 'security',
      title: 'Environment & Secrets Protection (.gitignore)',
      status: hasGitignore ? 'PASS' : 'WARN',
      details: hasGitignore ? '.gitignore protects .env and secret files.' : '.gitignore lacks explicit .env rule.',
      recommendation: 'Add .env* to .gitignore',
      fixable: !hasGitignore
    });

    const passed = checks.filter(c => c.status === 'PASS').length;
    const warned = checks.filter(c => c.status === 'WARN').length;
    const failed = checks.filter(c => c.status === 'FAIL').length;

    return {
      passed,
      warned,
      failed,
      total: checks.length,
      checks,
      overallHealthy: failed === 0,
      timestamp: new Date().toISOString()
    };
  }

  public fixAll(): FixResult[] {
    const report = this.diagnose();
    const fixableChecks = report.checks.filter(c => c.fixable && c.status !== 'PASS');
    const results: FixResult[] = [];

    for (const check of fixableChecks) {
      const res = this.fixCheck(check.id);
      results.push(res);
    }
    return results;
  }

  public fixCheck(checkId: string): FixResult {
    switch (checkId) {
      case 'cli-permission': {
        const cliPath = path.join(this.projectDir, 'bin', 'cli.js');
        try {
          fs.chmodSync(cliPath, 0o755);
          return { checkId, remediated: true, message: 'Granted executable permission (0755) to bin/cli.js.' };
        } catch (e: any) {
          return { checkId, remediated: false, message: `Failed to chmod bin/cli.js: ${e.message}` };
        }
      }

      case 'cli-symlink': {
        const localBinDir = path.join(this.homeDir, '.local', 'bin');
        if (!fs.existsSync(localBinDir)) {
          fs.mkdirSync(localBinDir, { recursive: true });
        }
        const target = path.join(localBinDir, 'agentic-workflow');
        const src = path.join(this.projectDir, 'bin', 'cli.js');
        try {
          if (fs.existsSync(target)) fs.unlinkSync(target);
          fs.symlinkSync(src, target);
          return { checkId, remediated: true, message: `Symlinked ${target} -> ${src}.` };
        } catch (e: any) {
          return { checkId, remediated: false, message: `Failed to symlink CLI: ${e.message}` };
        }
      }

      case 'dependencies-npm': {
        try {
          execSync('bun install', { cwd: this.projectDir, stdio: 'pipe' });
          return { checkId, remediated: true, message: 'Successfully ran bun install.' };
        } catch (e: any) {
          return { checkId, remediated: false, message: `bun install failed: ${e.message}` };
        }
      }

      case 'skills-mesh': {
        try {
          execSync('python3 core/skills_indexer.py index', { cwd: this.projectDir, stdio: 'pipe' });
          return { checkId, remediated: true, message: 'Rebuilt skills-index.json and skills-index.toon.' };
        } catch (e: any) {
          return { checkId, remediated: false, message: `Skills indexing failed: ${e.message}` };
        }
      }

      case 'security-env-guard': {
        const gitignore = path.join(this.projectDir, '.gitignore');
        try {
          fs.appendFileSync(gitignore, '\n.env\n.env.*\n*.pem\n');
          return { checkId, remediated: true, message: 'Appended .env protection rules to .gitignore.' };
        } catch (e: any) {
          return { checkId, remediated: false, message: `Failed updating .gitignore: ${e.message}` };
        }
      }

      case 'hooks-ledger': {
        const ledgerFile = path.join(this.projectDir, 'ledger.jsonl');
        try {
          fs.writeFileSync(ledgerFile, '');
          return { checkId, remediated: true, message: 'Initialized ledger.jsonl.' };
        } catch (e: any) {
          return { checkId, remediated: false, message: `Failed creating ledger: ${e.message}` };
        }
      }

      default:
        return { checkId, remediated: false, message: `No automated fix available for ${checkId}.` };
    }
  }
}
