/**
 * src/system/refresher.ts — Refresher & Cache Invalidation Engine
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execSync } from 'node:child_process';
import type { RefreshOptions, RefreshReport } from './types.ts';

export class Refresher {
  private projectDir: string;
  private homeDir: string;

  constructor(projectDir: string = '.') {
    this.projectDir = path.resolve(projectDir);
    this.homeDir = os.homedir();
  }

  private removeDirRecursive(dirPath: string): { count: number; bytes: number } {
    let count = 0;
    let bytes = 0;
    if (!fs.existsSync(dirPath)) return { count, bytes };

    try {
      const entries = fs.readdirSync(dirPath, { withFileTypes: true });
      for (const entry of entries) {
        const full = path.join(dirPath, entry.name);
        if (entry.isDirectory()) {
          const res = this.removeDirRecursive(full);
          count += res.count;
          bytes += res.bytes;
        } else {
          try {
            const stat = fs.statSync(full);
            bytes += stat.size;
            fs.unlinkSync(full);
            count++;
          } catch {
            // Ignore
          }
        }
      }
      fs.rmdirSync(dirPath);
    } catch {
      // Ignore
    }
    return { count, bytes };
  }

  private clearBytecodeCaches(): { items: string[]; bytes: number } {
    const items: string[] = [];
    let bytes = 0;

    const findPycache = (dir: string) => {
      if (!fs.existsSync(dir)) return;
      try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
          const full = path.join(dir, entry.name);
          if (entry.isDirectory()) {
            if (entry.name === '__pycache__' || entry.name === '.pytest_cache') {
              const res = this.removeDirRecursive(full);
              items.push(path.relative(this.projectDir, full));
              bytes += res.bytes;
            } else if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
              findPycache(full);
            }
          }
        }
      } catch {
        // Ignore
      }
    };

    findPycache(this.projectDir);
    return { items, bytes };
  }

  private cleanStaleLocks(): string[] {
    const cleared: string[] = [];
    const lockFiles = [
      path.join(this.projectDir, '.lock'),
      path.join(this.projectDir, '.git', 'index.lock'),
      path.join(this.projectDir, '.git', 'refs', 'heads', 'main.lock')
    ];

    for (const lf of lockFiles) {
      if (fs.existsSync(lf)) {
        try {
          const stat = fs.statSync(lf);
          // If older than 5 minutes, consider stale
          if (Date.now() - stat.mtimeMs > 5 * 60 * 1000) {
            fs.unlinkSync(lf);
            cleared.push(path.relative(this.projectDir, lf));
          }
        } catch {
          // Ignore
        }
      }
    }
    return cleared;
  }

  public refresh(options: RefreshOptions = {}): RefreshReport {
    const startTime = Date.now();
    const clearedItems: string[] = [];
    let freedBytes = 0;
    const messages: string[] = [];
    const hostsSynced: string[] = [];

    // 1. Clear Bytecode
    if (options.clearBytecode !== false) {
      const { items, bytes } = this.clearBytecodeCaches();
      clearedItems.push(...items);
      freedBytes += bytes;
      if (items.length > 0) {
        messages.push(`✓ Cleared ${items.length} Python bytecode cache directory(ies)`);
      }
    }

    // 2. Clean Stale Lockfiles
    if (options.cleanLockfiles !== false) {
      const locks = this.cleanStaleLocks();
      clearedItems.push(...locks);
      if (locks.length > 0) {
        messages.push(`✓ Removed ${locks.length} stale lockfile(s)`);
      }
    }

    // 3. Reset Risk Scores
    if (options.resetRiskScores) {
      const riskPath = path.join(this.projectDir, 'risk-scores.json');
      if (fs.existsSync(riskPath)) {
        try {
          fs.unlinkSync(riskPath);
          clearedItems.push('risk-scores.json');
          messages.push(`✓ Reset predictive debugging risk scores cache`);
        } catch {
          // Ignore
        }
      }
    }

    // 4. Rebuild Skills Index
    let skillsReindexed = false;
    if (options.rebuildSkillsIndex !== false) {
      try {
        execSync('python3 core/skills_indexer.py index', { cwd: this.projectDir, stdio: 'pipe' });
        skillsReindexed = true;
        messages.push(`✓ Rebuilt skills-index.json and skills-index.toon`);
      } catch (err: any) {
        messages.push(`! Skills re-indexing notice: ${err.message}`);
      }
    }

    // 5. Sync Integrations
    let integrationsSynced = false;
    if (options.syncIntegrations !== false) {
      try {
        const script = `from core.integrations import IntegrationInstaller; IntegrationInstaller('${this.projectDir}').provision_all()`;
        execSync(`python3 -c "${script}"`, { cwd: this.projectDir, stdio: 'pipe' });
        integrationsSynced = true;
        messages.push(`✓ Synchronized supportive integrations (Ponytail, TOON, Fable, Caveman)`);
      } catch (err: any) {
        messages.push(`! Integrations sync notice: ${err.message}`);
      }
    }

    // 6. Sync Host Skills
    if (options.syncHostSkills) {
      const hostDirs = [
        path.join(this.homeDir, '.claude', 'skills', 'agentic-workflow'),
        path.join(this.homeDir, '.gemini', 'config', 'skills', 'agentic-workflow'),
        path.join(this.homeDir, '.cursor', 'skills', 'agentic-workflow'),
        path.join(this.homeDir, '.agents', 'skills', 'agentic-workflow')
      ];

      for (const hDir of hostDirs) {
        if (fs.existsSync(hDir)) {
          try {
            // Update SKILL.md and marketplace.json
            fs.copyFileSync(path.join(this.projectDir, 'SKILL.md'), path.join(hDir, 'SKILL.md'));
            hostsSynced.push(hDir);
          } catch {
            // Ignore
          }
        }
      }
      if (hostsSynced.length > 0) {
        messages.push(`✓ Updated skill definitions across ${hostsSynced.length} host environments`);
      }
    }

    const durationMs = Date.now() - startTime;
    return {
      success: true,
      clearedItems,
      freedBytes,
      skillsReindexed,
      integrationsSynced,
      hostsSynced,
      durationMs,
      messages
    };
  }
}
