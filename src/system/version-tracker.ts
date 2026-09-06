/**
 * src/system/version-tracker.ts — Version Tracker, Matrix & Migration Engine
 */

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import type { VersionMatrix, ComponentVersion, MigrationStep } from './types.ts';

export class VersionTracker {
  private projectDir: string;
  private migrationFile: string;

  constructor(projectDir: string = '.') {
    this.projectDir = path.resolve(projectDir);
    this.migrationFile = path.join(this.projectDir, '.migration_history.json');
  }

  private runGit(cmd: string): string {
    try {
      return execSync(`git ${cmd}`, { cwd: this.projectDir, stdio: 'pipe', encoding: 'utf-8' }).trim();
    } catch {
      return '';
    }
  }

  public getPackageVersion(): string {
    try {
      const pkgPath = path.join(this.projectDir, 'package.json');
      if (fs.existsSync(pkgPath)) {
        const data = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));
        return data.version || '1.1.0';
      }
    } catch {
      // Ignore
    }
    return '1.1.0';
  }

  public getVersionMatrix(): VersionMatrix {
    const pkgVersion = this.getPackageVersion();
    const commit = this.runGit('rev-parse HEAD') || 'unknown';
    const branch = this.runGit('rev-parse --abbrev-ref HEAD') || 'main';
    const dirty = this.runGit('status --porcelain').length > 0;

    const components: ComponentVersion[] = [
      { name: 'AgenticWorkflow CLI', version: pkgVersion, channel: branch === 'main' ? 'stable' : 'dev', path: 'bin/cli.js' },
      { name: 'TypeScript Async Engine', version: pkgVersion, channel: 'stable', path: 'src/engine_ts/' },
      { name: 'Python AsyncIO Engine', version: pkgVersion, channel: 'stable', path: 'core/engine_py/' },
      { name: 'TOON Protocol Adapter', version: '4.1.1', channel: 'standard', path: 'src/engine_ts/toon-adapter.ts' },
      { name: 'Universal Agentic Hooks', version: '1.2.0', channel: 'governed', path: 'src/hooks/' },
      { name: 'Skills Mesh Indexer', version: '2.0.0', channel: 'dynamic', path: 'core/skills_indexer.py' },
      { name: 'Supportive Tools Director', version: '1.1.0', channel: 'continuous', path: 'src/integrations/' }
    ];

    return {
      cliVersion: pkgVersion,
      tsEngineVersion: pkgVersion,
      pyEngineVersion: pkgVersion,
      toonProtocolVersion: '4.1.1',
      uahfHooksVersion: '1.2.0',
      gitCommit: commit,
      gitBranch: branch,
      gitClean: !dirty,
      buildDate: '2026-09-06T14:40:00Z',
      components
    };
  }

  public compareVersions(v1: string, v2: string): number {
    const clean1 = v1.replace(/^v/, '').split('.').map(Number);
    const clean2 = v2.replace(/^v/, '').split('.').map(Number);

    for (let i = 0; i < 3; i++) {
      const num1 = clean1[i] || 0;
      const num2 = clean2[i] || 0;
      if (num1 > num2) return 1;
      if (num1 < num2) return -1;
    }
    return 0;
  }

  public getAvailableMigrations(): MigrationStep[] {
    return [
      {
        fromVersion: '1.0.0',
        toVersion: '1.0.5',
        name: 'migrate_to_toon_v41',
        description: 'Convert JSON state caches to TOON v4.1 format and generate skills-index.toon',
        executed: true,
        timestamp: '2026-09-01T00:00:00Z'
      },
      {
        fromVersion: '1.0.5',
        toVersion: '1.1.0',
        name: 'provision_supportive_tools',
        description: 'Initialize integrations.json and provision Ponytail, Fable, Caveman',
        executed: true,
        timestamp: '2026-09-05T00:00:00Z'
      },
      {
        fromVersion: '1.1.0',
        toVersion: '1.2.0',
        name: 'enable_system_engines',
        description: 'Bootstrap system engines: updater, installer, doctor, health, notifications',
        executed: true,
        timestamp: '2026-09-06T14:40:00Z'
      }
    ];
  }

  public getChangelog(): Record<string, string[]> {
    return {
      '1.1.0': [
        'Universal System Engines Suite: Auto-Updater, Auto-Installer, Refresher, Doctor, Health Engine, Dependencies Engine, Notifications, Announcements, Version Tracker',
        'Full dual-runtime parity across TypeScript/Bun and Python 3 engines',
        'Doctor automated remediation (--fix) and real-time health telemetry',
        'Rich ANSI terminal toast banners and native macOS desktop notifications'
      ],
      '1.0.5': [
        'Integrated official TOON v4.1 adapter delivering 30-60% token savings',
        'Built Agentic Skills Mesh with synchronized JSON and TOON indexing',
        'Supportive Tools Subsystem: Ponytail YAGNI ladder, Fable circuit breakers, Caveman mode'
      ],
      '1.0.0': [
        'Universal Agentic Hooks Framework (UAHF) governing multi-agent sessions',
        'Autopilot self-fueling execution loop with 4-layer verification (L0-L2)'
      ]
    };
  }

  public formatMatrixToon(matrix: VersionMatrix): string {
    return `version_matrix{cli:"${matrix.cliVersion}",branch:"${matrix.gitBranch}",commit:"${matrix.gitCommit.substring(0, 7)}",clean:${matrix.gitClean}}:
  components[${matrix.components.length}]{name,version,channel,path}:
${matrix.components.map(c => `    "${c.name}",${c.version},${c.channel},${c.path || ''}`).join('\n')}`;
  }
}
