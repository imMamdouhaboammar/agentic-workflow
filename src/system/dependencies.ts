/**
 * src/system/dependencies.ts — Lib Dependencies & Multi-Ecosystem Auditor Engine
 */

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import type { DependencyItem, DependencyAuditReport } from './types.ts';

export class DependenciesEngine {
  private projectDir: string;

  constructor(projectDir: string = '.') {
    this.projectDir = path.resolve(projectDir);
  }

  private checkNpmPackage(pkgName: string): { installed: boolean; version?: string } {
    try {
      const pkgJsonPath = path.join(this.projectDir, 'node_modules', pkgName, 'package.json');
      if (fs.existsSync(pkgJsonPath)) {
        const pkg = JSON.parse(fs.readFileSync(pkgJsonPath, 'utf-8'));
        return { installed: true, version: pkg.version };
      }
    } catch {
      // Ignore
    }
    return { installed: false };
  }

  private checkPythonModule(modName: string): { available: boolean } {
    try {
      execSync(`python3 -c "import ${modName}"`, { cwd: this.projectDir, stdio: 'pipe' });
      return { available: true };
    } catch {
      return { available: false };
    }
  }

  private checkBinary(cmd: string): { available: boolean; version?: string } {
    try {
      const out = execSync(`${cmd} --version`, { stdio: 'pipe', encoding: 'utf-8' }).trim();
      return { available: true, version: out.split('\n')[0] };
    } catch {
      return { available: false };
    }
  }

  public audit(): DependencyAuditReport {
    const deps: DependencyItem[] = [];

    // 1. Bun / Node Packages
    const packageJsonPath = path.join(this.projectDir, 'package.json');
    if (fs.existsSync(packageJsonPath)) {
      try {
        const pkgData = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
        const declared = { ...pkgData.dependencies, ...pkgData.devDependencies };

        for (const [name, reqVer] of Object.entries(declared)) {
          const check = this.checkNpmPackage(name);
          deps.push({
            name,
            type: 'bun-npm',
            requiredVersion: reqVer as string,
            installedVersion: check.version,
            status: check.installed ? 'SATISFIED' : 'MISSING',
            location: path.join('node_modules', name)
          });
        }
      } catch {
        // Ignore
      }
    }

    // 2. Python Modules
    const pyModules = ['json', 'pathlib', 'unittest', 'dataclasses', 'asyncio', 'hashlib'];
    for (const mod of pyModules) {
      const check = this.checkPythonModule(mod);
      deps.push({
        name: `python:${mod}`,
        type: 'python',
        status: check.available ? 'SATISFIED' : 'MISSING',
        description: 'Standard Python 3 dual-engine module'
      });
    }

    // 3. Supportive Tools Integrations
    const integrationsPath = path.join(this.projectDir, 'integrations.json');
    if (fs.existsSync(integrationsPath)) {
      try {
        const intData = JSON.parse(fs.readFileSync(integrationsPath, 'utf-8'));
        for (const item of intData.integrations || []) {
          deps.push({
            name: `integration:${item.id}`,
            type: 'supportive-tool',
            status: 'SATISFIED',
            description: item.description,
            location: item.repo
          });
        }
      } catch {
        // Ignore
      }
    }

    // 4. System Toolchain Binaries
    const binaries = ['bun', 'python3', 'git'];
    for (const bin of binaries) {
      const check = this.checkBinary(bin);
      deps.push({
        name: `bin:${bin}`,
        type: 'system-binary',
        installedVersion: check.version,
        status: check.available ? 'SATISFIED' : 'MISSING'
      });
    }

    const satisfied = deps.filter(d => d.status === 'SATISFIED').length;
    const missing = deps.filter(d => d.status === 'MISSING').length;
    const outdated = deps.filter(d => d.status === 'OUTDATED').length;
    const incompatible = deps.filter(d => d.status === 'INCOMPATIBLE').length;

    return {
      total: deps.length,
      satisfied,
      missing,
      outdated,
      incompatible,
      dependencies: deps,
      allSatisfied: missing === 0 && incompatible === 0
    };
  }

  public installMissing(): { success: boolean; message: string } {
    try {
      execSync('bun install', { cwd: this.projectDir, stdio: 'pipe' });
      return { success: true, message: 'Bun dependencies installed successfully.' };
    } catch (err: any) {
      return { success: false, message: `Installation failed: ${err.message}` };
    }
  }

  public formatTree(): string {
    const audit = this.audit();
    let tree = `agentic-workflow@1.1.0\n`;

    const byType: Record<string, DependencyItem[]> = {};
    for (const dep of audit.dependencies) {
      byType[dep.type] = byType[dep.type] || [];
      byType[dep.type].push(dep);
    }

    const typeKeys = Object.keys(byType);
    typeKeys.forEach((type, tIdx) => {
      const isLastType = tIdx === typeKeys.length - 1;
      const typeBranch = isLastType ? '└── ' : '├── ';
      tree += `${typeBranch}${type.toUpperCase()}\n`;

      const items = byType[type];
      items.forEach((item, iIdx) => {
        const isLastItem = iIdx === items.length - 1;
        const subBranch = (isLastType ? '    ' : '│   ') + (isLastItem ? '└── ' : '├── ');
        const statusIcon = item.status === 'SATISFIED' ? '✓' : '✗';
        const versionStr = item.installedVersion ? ` (${item.installedVersion})` : '';
        tree += `${subBranch}[${statusIcon}] ${item.name}${versionStr}\n`;
      });
    });

    return tree;
  }

  public formatToon(audit: DependencyAuditReport): string {
    return `dependencies_audit{total:${audit.total},satisfied:${audit.satisfied},missing:${audit.missing},all_ok:${audit.allSatisfied}}:
  items[${audit.dependencies.length}]{name,type,status,version}:
${audit.dependencies.map(d => `    ${d.name},${d.type},${d.status},${d.installedVersion || d.requiredVersion || 'default'}`).join('\n')}`;
  }
}
