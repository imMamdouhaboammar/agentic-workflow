/**
 * src/system/updater.ts — Auto-Updater Engine for AgenticWorkflow
 */

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import type { UpdateCheckResult, UpdateOptions, UpdateResult, RollbackResult } from './types.ts';

export class AutoUpdater {
  private projectDir: string;
  private historyFile: string;

  constructor(projectDir: string = '.') {
    this.projectDir = path.resolve(projectDir);
    this.historyFile = path.join(this.projectDir, '.update_history.json');
  }

  private runGit(cmd: string): string {
    try {
      return execSync(`git ${cmd}`, { cwd: this.projectDir, stdio: 'pipe', encoding: 'utf-8' }).trim();
    } catch (e: any) {
      return '';
    }
  }

  public getLocalVersion(): string {
    try {
      const pkgPath = path.join(this.projectDir, 'package.json');
      if (fs.existsSync(pkgPath)) {
        const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
        return pkg.version || '1.0.0';
      }
    } catch {
      // Ignore
    }
    return '1.0.0';
  }

  public checkForUpdates(): UpdateCheckResult {
    const currentCommit = this.runGit('rev-parse HEAD') || 'unknown';
    const branch = this.runGit('rev-parse --abbrev-ref HEAD') || 'main';
    const currentVersion = this.getLocalVersion();

    let remoteCommit = currentCommit;
    let behindCount = 0;
    const commits: Array<{ hash: string; message: string; date: string }> = [];

    // Try checking remote via ls-remote or fetch
    try {
      const remoteHead = this.runGit(`ls-remote origin refs/heads/${branch}`);
      if (remoteHead) {
        remoteCommit = remoteHead.split(/\s+/)[0] || currentCommit;
      }
      if (remoteCommit && remoteCommit !== currentCommit) {
        // We have a difference
        behindCount = 1;
        commits.push({
          hash: remoteCommit.substring(0, 7),
          message: `Upstream update available on origin/${branch}`,
          date: new Date().toISOString()
        });
      }
    } catch {
      // Remote might be offline
    }

    return {
      hasUpdate: remoteCommit !== currentCommit && remoteCommit !== 'unknown',
      currentCommit,
      currentVersion,
      remoteCommit,
      remoteVersion: remoteCommit !== currentCommit ? `${currentVersion}-next` : currentVersion,
      branch,
      behindCount,
      commits,
      channel: branch === 'main' ? 'stable' : 'nightly'
    };
  }

  public update(options: UpdateOptions = {}): UpdateResult {
    const strategy = options.strategy || 'stash-and-pull';
    const branch = options.branch || this.runGit('rev-parse --abbrev-ref HEAD') || 'main';
    const previousCommit = this.runGit('rev-parse HEAD');

    const status = this.runGit('status --porcelain');
    const isDirty = status.length > 0;
    let stashed = false;

    if (isDirty) {
      if (strategy === 'stash-and-pull') {
        const stashMsg = `agentic-auto-update-${Date.now()}`;
        this.runGit(`stash push -m "${stashMsg}"`);
        stashed = true;
      } else if (!options.force) {
        return {
          success: false,
          previousCommit,
          newCommit: previousCommit,
          message: 'Working directory has uncommitted changes. Use --force or stash changes first.',
          stashed: false,
          reinstalled: false,
          refreshed: false
        };
      }
    }

    try {
      // Perform pull
      this.runGit(`pull origin ${branch}`);
      const newCommit = this.runGit('rev-parse HEAD');

      let reinstalled = false;
      if (options.autoReinstall) {
        try {
          execSync('bun install', { cwd: this.projectDir, stdio: 'pipe' });
          reinstalled = true;
        } catch {
          // Fallback or ignore
        }
      }

      // Record update in history file
      this.saveHistoryRecord({
        timestamp: new Date().toISOString(),
        previousCommit,
        newCommit,
        branch,
        stashed
      });

      return {
        success: true,
        previousCommit,
        newCommit,
        message: `Updated successfully from ${previousCommit.substring(0, 7)} to ${newCommit.substring(0, 7)}`,
        stashed,
        reinstalled,
        refreshed: !!options.autoRefresh
      };
    } catch (err: any) {
      // Rollback on failure if stashed
      if (stashed) {
        this.runGit('stash pop');
      }
      return {
        success: false,
        previousCommit,
        newCommit: previousCommit,
        message: `Update failed: ${err.message || String(err)}`,
        stashed: false,
        reinstalled: false,
        refreshed: false
      };
    }
  }

  public rollback(): RollbackResult {
    const history = this.getHistory();
    if (history.length === 0) {
      return {
        success: false,
        rolledBackTo: '',
        message: 'No update history found to rollback.'
      };
    }

    const last = history[history.length - 1];
    const targetCommit = last.previousCommit;

    try {
      this.runGit(`reset --hard ${targetCommit}`);
      if (last.stashed) {
        try {
          this.runGit('stash pop');
        } catch {
          // Ignore stash conflicts
        }
      }

      // Remove last record
      history.pop();
      fs.writeFileSync(this.historyFile, JSON.stringify(history, null, 2));

      return {
        success: true,
        rolledBackTo: targetCommit,
        message: `Successfully rolled back to commit ${targetCommit.substring(0, 7)}`
      };
    } catch (err: any) {
      return {
        success: false,
        rolledBackTo: '',
        message: `Rollback failed: ${err.message}`
      };
    }
  }

  public getHistory(): any[] {
    try {
      if (fs.existsSync(this.historyFile)) {
        return JSON.parse(fs.readFileSync(this.historyFile, 'utf-8'));
      }
    } catch {
      // Ignore
    }
    return [];
  }

  private saveHistoryRecord(record: any): void {
    try {
      const history = this.getHistory();
      history.push(record);
      fs.writeFileSync(this.historyFile, JSON.stringify(history, null, 2));
    } catch {
      // Ignore write errors
    }
  }
}
