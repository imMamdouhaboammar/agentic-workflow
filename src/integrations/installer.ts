/**
 * installer.ts — TypeScript/Bun Autonomous Supportive Tools Provisioner
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execSync } from 'node:child_process';
import { IntegrationDefinition, IntegrationsRegistry, getDefaultRegistry } from './registry.ts';

export interface InstallationStatus {
  id: string;
  name: string;
  installed: boolean;
  status: 'INSTALLED' | 'MISSING' | 'ERROR' | 'PROVISIONED';
  details: string;
  locations: string[];
}

export class IntegrationInstaller {
  private projectDir: string;
  private homeDir: string;
  private targetSkillDirs: string[];

  constructor(projectDir: string = '.', homeDir?: string) {
    this.projectDir = path.resolve(projectDir);
    this.homeDir = homeDir ? path.resolve(homeDir) : os.homedir();
    this.targetSkillDirs = [
      path.join(this.homeDir, '.gemini', 'config', 'skills'),
      path.join(this.homeDir, '.claude', 'skills'),
      path.join(this.homeDir, '.agents', 'skills'),
      path.join(this.homeDir, '.codex', 'skills'),
    ];
  }

  private findExistingSkillDir(skillName: string): string | null {
    const searchDirs = [
      ...this.targetSkillDirs,
      path.join(this.homeDir, '.agent-kernel', 'plugins', skillName, 'skills', skillName),
      path.join(this.homeDir, '.agent-kernel', 'plugins', skillName, 'skills'),
      path.join(this.homeDir, '.claude', 'plugins', 'marketplaces', skillName),
    ];

    for (const dir of searchDirs) {
      if (fs.existsSync(dir) && fs.statSync(dir).isDirectory()) {
        const skillFile = path.join(dir, 'SKILL.md');
        if (fs.existsSync(skillFile)) {
          return dir;
        }
        const childDir = path.join(dir, skillName);
        if (fs.existsSync(childDir) && fs.existsSync(path.join(childDir, 'SKILL.md'))) {
          return childDir;
        }
      }
    }
    return null;
  }

  public checkStatus(item: IntegrationDefinition): InstallationStatus {
    const detectedLocations: string[] = [];

    // 1. Skill directories
    const skillNames: string[] = item.install?.skill_names || [item.id];
    for (const sname of skillNames) {
      for (const base of this.targetSkillDirs) {
        const candidate = path.join(base, sname);
        if (fs.existsSync(candidate)) {
          detectedLocations.push(candidate);
        }
      }
    }

    // 2. npm / bun package
    const npmPkg = item.detection?.npm_package;
    if (npmPkg) {
      const pkgPath = path.join(this.projectDir, 'node_modules', npmPkg);
      if (fs.existsSync(pkgPath)) {
        detectedLocations.push(`node_modules/${npmPkg}`);
      }
    }

    // 3. state dir
    const stateDir = item.detection?.state_dir;
    if (stateDir) {
      const fullState = path.join(this.projectDir, stateDir);
      if (fs.existsSync(fullState)) {
        detectedLocations.push(stateDir);
      }
    }

    const isInstalled = detectedLocations.length > 0;
    return {
      id: item.id,
      name: item.name,
      installed: isInstalled,
      status: isInstalled ? 'INSTALLED' : 'MISSING',
      details: isInstalled ? `Active at ${detectedLocations.length} location(s)` : 'Not found in environment paths',
      locations: detectedLocations
    };
  }

  public provision(item: IntegrationDefinition, synchronizeAll: boolean = true): InstallationStatus {
    const strategy = item.install?.strategy || 'skill';
    const createdLocations: string[] = [];

    try {
      if (strategy === 'skill' || strategy === 'hybrid') {
        const skillNames: string[] = item.install?.skill_names || [item.id];
        for (const sname of skillNames) {
          const existing = this.findExistingSkillDir(sname);
          if (existing) {
            for (const targetDir of this.targetSkillDirs) {
              const dest = path.join(targetDir, sname);
              if (!fs.existsSync(dest)) {
                fs.mkdirSync(targetDir, { recursive: true });
                try {
                  fs.symlinkSync(existing, dest);
                  createdLocations.push(dest);
                } catch {
                  fs.cpSync(existing, dest, { recursive: true });
                  createdLocations.push(dest);
                }
              }
            }
          } else {
            const fallbackGit = item.install?.fallback_git;
            if (fallbackGit) {
              const primaryTarget = path.join(this.homeDir, '.agents', 'skills', sname);
              fs.mkdirSync(path.dirname(primaryTarget), { recursive: true });
              try {
                execSync(`git clone --depth 1 "${fallbackGit}" "${primaryTarget}"`, { stdio: 'pipe', timeout: 30000 });
                createdLocations.push(primaryTarget);
                for (const targetDir of this.targetSkillDirs) {
                  const dest = path.join(targetDir, sname);
                  if (!fs.existsSync(dest)) {
                    fs.mkdirSync(targetDir, { recursive: true });
                    try {
                      fs.symlinkSync(primaryTarget, dest);
                      createdLocations.push(dest);
                    } catch {
                      fs.cpSync(primaryTarget, dest, { recursive: true });
                      createdLocations.push(dest);
                    }
                  }
                }
              } catch {
                // Ignore clone errors
              }
            }
          }
        }
      }

      if (strategy === 'package' || strategy === 'hybrid') {
        const bunPkg = item.install?.bun_package;
        const npmPkg = item.detection?.npm_package;
        if (bunPkg && (!npmPkg || !fs.existsSync(path.join(this.projectDir, 'node_modules', npmPkg)))) {
          try {
            execSync(`bun add "${bunPkg}"`, { cwd: this.projectDir, stdio: 'pipe', timeout: 30000 });
            createdLocations.push(`bun:${bunPkg}`);
          } catch {
            // Ignore if bun fails
          }
        }
      }

      const postStatus = this.checkStatus(item);
      if (postStatus.installed || createdLocations.length > 0) {
        return {
          id: item.id,
          name: item.name,
          installed: true,
          status: createdLocations.length > 0 ? 'PROVISIONED' : postStatus.status,
          details: `Active at ${postStatus.locations.length} location(s)` + (createdLocations.length > 0 ? ` (${createdLocations.length} newly synced)` : ''),
          locations: postStatus.locations
        };
      }

      return {
        id: item.id,
        name: item.name,
        installed: false,
        status: 'ERROR',
        details: 'Provisioning completed without active targets confirmed',
        locations: []
      };
    } catch (err: any) {
      return {
        id: item.id,
        name: item.name,
        installed: false,
        status: 'ERROR',
        details: `Provisioning error: ${err?.message || String(err)}`,
        locations: []
      };
    }
  }

  public provisionAll(registry?: IntegrationsRegistry): InstallationStatus[] {
    const reg = registry || getDefaultRegistry(this.projectDir);
    return reg.listAll().map(item => this.provision(item, true));
  }

  public checkAll(registry?: IntegrationsRegistry): InstallationStatus[] {
    const reg = registry || getDefaultRegistry(this.projectDir);
    return reg.listAll().map(item => this.checkStatus(item));
  }
}
