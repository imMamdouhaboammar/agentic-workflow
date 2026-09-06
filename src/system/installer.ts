/**
 * src/system/installer.ts — Auto-Installer & Environment Bootstrapper Engine
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execSync } from 'node:child_process';
import type { InstallOptions, InstallReport, InstallTarget, HostPlatform } from './types.ts';

export class AutoInstaller {
  private projectDir: string;
  private homeDir: string;

  constructor(projectDir: string = '.') {
    this.projectDir = path.resolve(projectDir);
    this.homeDir = os.homedir();
  }

  private checkBinary(cmd: string): { available: boolean; version?: string } {
    try {
      const out = execSync(`${cmd} --version`, { stdio: 'pipe', encoding: 'utf-8' }).trim();
      return { available: true, version: out.split('\n')[0] };
    } catch {
      return { available: false };
    }
  }

  public getHostTargets(): InstallTarget[] {
    const targets: InstallTarget[] = [
      {
        name: 'Claude Code Skills',
        platform: 'claude',
        path: path.join(this.homeDir, '.claude', 'skills', 'agentic-workflow'),
        installed: fs.existsSync(path.join(this.homeDir, '.claude', 'skills', 'agentic-workflow'))
      },
      {
        name: 'Gemini CLI / Antigravity Skills',
        platform: 'gemini',
        path: path.join(this.homeDir, '.gemini', 'config', 'skills', 'agentic-workflow'),
        installed: fs.existsSync(path.join(this.homeDir, '.gemini', 'config', 'skills', 'agentic-workflow'))
      },
      {
        name: 'Cursor IDE Skills',
        platform: 'cursor',
        path: path.join(this.homeDir, '.cursor', 'skills', 'agentic-workflow'),
        installed: fs.existsSync(path.join(this.homeDir, '.cursor', 'skills', 'agentic-workflow'))
      },
      {
        name: 'Codex / OpenCode Skills',
        platform: 'codex',
        path: path.join(this.homeDir, '.codex', 'skills', 'agentic-workflow'),
        installed: fs.existsSync(path.join(this.homeDir, '.codex', 'skills', 'agentic-workflow'))
      },
      {
        name: 'Universal Agent Kernel',
        platform: 'agents',
        path: path.join(this.homeDir, '.agents', 'skills', 'agentic-workflow'),
        installed: fs.existsSync(path.join(this.homeDir, '.agents', 'skills', 'agentic-workflow'))
      }
    ];
    return targets;
  }

  public checkStatus(): InstallReport {
    const targets = this.getHostTargets();
    const installed = targets.filter(t => t.installed);
    const skipped = targets.filter(t => !t.installed);

    const binPaths = [
      path.join(this.homeDir, '.local', 'bin', 'agentic-workflow'),
      '/usr/local/bin/agentic-workflow'
    ];
    const linked = binPaths.filter(p => fs.existsSync(p));

    const systemDeps = [
      { name: 'bun', ...this.checkBinary('bun') },
      { name: 'node', ...this.checkBinary('node') },
      { name: 'python3', ...this.checkBinary('python3') },
      { name: 'git', ...this.checkBinary('git') },
      { name: 'brew', ...this.checkBinary('brew') }
    ];

    return {
      success: true,
      installedTargets: installed,
      skippedTargets: skipped,
      binLinked: linked,
      shellConfigured: [],
      systemDeps,
      messages: [
        `Installed in ${installed.length} agent host(s)`,
        `CLI binaries linked in ${linked.length} path(s)`
      ]
    };
  }

  public install(options: InstallOptions = {}): InstallReport {
    const messages: string[] = [];
    const installedTargets: InstallTarget[] = [];
    const skippedTargets: InstallTarget[] = [];
    const binLinked: string[] = [];
    const shellConfigured: string[] = [];

    const hostTargets = this.getHostTargets();
    const requestedPlatforms = options.targets || ['claude', 'gemini', 'cursor', 'codex', 'agents'];

    // 1. Copy or Symlink into host skills directories
    for (const target of hostTargets) {
      if (!requestedPlatforms.includes(target.platform)) {
        skippedTargets.push(target);
        continue;
      }

      const parentDir = path.dirname(target.path);
      try {
        if (!fs.existsSync(parentDir)) {
          fs.mkdirSync(parentDir, { recursive: true });
        }

        if (fs.existsSync(target.path)) {
          fs.rmSync(target.path, { recursive: true, force: true });
        }

        // Copy files excluding node_modules / .git
        fs.cpSync(this.projectDir, target.path, {
          recursive: true,
          filter: (src) => {
            const rel = path.relative(this.projectDir, src);
            if (rel.startsWith('node_modules') || rel.startsWith('.git') || rel.startsWith('__pycache__')) {
              return false;
            }
            return true;
          }
        });

        target.installed = true;
        installedTargets.push(target);
        messages.push(`✓ Installed skill to ${target.name} (${target.path})`);
      } catch (err: any) {
        messages.push(`! Failed installing to ${target.name}: ${err.message}`);
        skippedTargets.push(target);
      }
    }

    // 2. Global CLI Binary Symlink
    const cliSource = path.join(this.projectDir, 'bin', 'cli.js');
    if (fs.existsSync(cliSource)) {
      try {
        fs.chmodSync(cliSource, 0o755);
      } catch {
        // Ignore
      }

      const localBinDir = path.join(this.homeDir, '.local', 'bin');
      if (!fs.existsSync(localBinDir)) {
        fs.mkdirSync(localBinDir, { recursive: true });
      }

      const localBinTarget = path.join(localBinDir, 'agentic-workflow');
      try {
        if (fs.existsSync(localBinTarget)) {
          fs.unlinkSync(localBinTarget);
        }
        fs.symlinkSync(cliSource, localBinTarget);
        binLinked.push(localBinTarget);
        messages.push(`✓ Linked executable to ${localBinTarget}`);
      } catch (err: any) {
        messages.push(`! Failed linking ${localBinTarget}: ${err.message}`);
      }

      // Try /usr/local/bin if writable
      if (options.globalBin) {
        const usrBinTarget = '/usr/local/bin/agentic-workflow';
        try {
          if (fs.existsSync(usrBinTarget)) {
            fs.unlinkSync(usrBinTarget);
          }
          fs.symlinkSync(cliSource, usrBinTarget);
          binLinked.push(usrBinTarget);
          messages.push(`✓ Linked global executable to ${usrBinTarget}`);
        } catch {
          // May need sudo, skip gracefully
        }
      }
    }

    // 3. Update Shell RC if requested
    if (options.updateShellRc !== false) {
      const localBin = path.join(this.homeDir, '.local', 'bin');
      const exportLine = `export PATH="$PATH:${localBin}"`;
      const rcFiles = [
        path.join(this.homeDir, '.zshrc'),
        path.join(this.homeDir, '.bashrc'),
        path.join(this.homeDir, '.profile')
      ];

      for (const rc of rcFiles) {
        if (fs.existsSync(rc)) {
          try {
            const content = fs.readFileSync(rc, 'utf-8');
            if (!content.includes(localBin)) {
              fs.appendFileSync(rc, `\n# AgenticWorkflow CLI\n${exportLine}\n`);
              shellConfigured.push(rc);
              messages.push(`✓ Added PATH export to ${path.basename(rc)}`);
            }
          } catch {
            // Ignore
          }
        }
      }
    }

    // 4. System Dependencies Check
    const systemDeps = [
      { name: 'bun', ...this.checkBinary('bun') },
      { name: 'node', ...this.checkBinary('node') },
      { name: 'python3', ...this.checkBinary('python3') },
      { name: 'git', ...this.checkBinary('git') },
      { name: 'brew', ...this.checkBinary('brew') }
    ];

    return {
      success: installedTargets.length > 0 || binLinked.length > 0,
      installedTargets,
      skippedTargets,
      binLinked,
      shellConfigured,
      systemDeps,
      messages
    };
  }

  public generateShellCompletion(shell: 'zsh' | 'bash' | 'fish'): string {
    const commands = [
      'engine', 'autopilot', 'run', 'skills', 'guard', 'eval', 'traces',
      'hooks', 'integrations', 'fable', 'toon', 'init', 'validate', 'status',
      'test', 'update', 'install', 'refresh', 'doctor', 'health', 'deps',
      'notify', 'announcements', 'version', 'help'
    ].join(' ');

    if (shell === 'zsh') {
      return `#compdef agentic-workflow
_agentic_workflow() {
  local -a commands
  commands=(${commands})
  _describe 'command' commands
}
compdef _agentic_workflow agentic-workflow
`;
    } else if (shell === 'fish') {
      return `complete -c agentic-workflow -f -a "${commands}"`;
    } else {
      return `_agentic_workflow() {
  local cur="\${COMP_WORDS[COMP_CWORD]}"
  COMPREPLY=( $(compgen -W "${commands}" -- "$cur") )
}
complete -F _agentic_workflow agentic-workflow
`;
    }
  }
}
