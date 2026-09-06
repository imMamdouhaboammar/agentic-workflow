/**
 * src/system/health.ts — Health Telemetry & Composite Scoring Engine
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execSync } from 'node:child_process';
import type { HealthReport, HealthScore, SystemVitals, WorkflowVitals, HealthGrade } from './types.ts';

export class HealthEngine {
  private projectDir: string;

  constructor(projectDir: string = '.') {
    this.projectDir = path.resolve(projectDir);
  }

  private getDiskUsage(): { freeBytes?: number; totalBytes?: number } {
    try {
      const out = execSync("df -k . | tail -1", { cwd: this.projectDir, stdio: 'pipe', encoding: 'utf-8' }).trim();
      const parts = out.split(/\s+/);
      if (parts.length >= 4) {
        const total = parseInt(parts[1], 10) * 1024;
        const free = parseInt(parts[3], 10) * 1024;
        return { totalBytes: total, freeBytes: free };
      }
    } catch {
      // Ignore
    }
    return {};
  }

  public collectSystemVitals(): SystemVitals {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    const usedPct = totalMem > 0 ? Math.round((usedMem / totalMem) * 100) : 0;
    const rss = process.memoryUsage().rss;

    let bunVersion: string | undefined;
    try {
      bunVersion = execSync('bun --version', { stdio: 'pipe', encoding: 'utf-8' }).trim();
    } catch {
      // Ignore
    }

    let pyVersion: string | undefined;
    try {
      pyVersion = execSync('python3 --version', { stdio: 'pipe', encoding: 'utf-8' }).trim().replace('Python ', '');
    } catch {
      // Ignore
    }

    return {
      platform: os.platform(),
      arch: os.arch(),
      uptimeSeconds: Math.floor(os.uptime()),
      memory: {
        totalBytes: totalMem,
        freeBytes: freeMem,
        rssBytes: rss,
        usedPercentage: usedPct
      },
      disk: this.getDiskUsage(),
      nodeVersion: process.version,
      bunVersion,
      pythonVersion: pyVersion
    };
  }

  public collectWorkflowVitals(): WorkflowVitals {
    const sotPath = path.join(this.projectDir, 'state.yaml');
    let hasActiveWorkflow = false;
    let currentStep: string | undefined;
    let retryCount = 0;

    if (fs.existsSync(sotPath)) {
      try {
        const content = fs.readFileSync(sotPath, 'utf-8');
        hasActiveWorkflow = content.includes('status: in_progress') || content.includes('status: planning');
        const match = content.match(/current_step:\s*["']?([^"'\n]+)/);
        if (match) currentStep = match[1];
        const retryMatch = content.match(/retry_count:\s*(\d+)/);
        if (retryMatch) retryCount = parseInt(retryMatch[1], 10);
      } catch {
        // Ignore
      }
    }

    let circuitBreakerStatus: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
    let failureStreak = 0;
    const fableStatePath = path.join(this.projectDir, '.fable', 'state.json');
    if (fs.existsSync(fableStatePath)) {
      try {
        const fsData = JSON.parse(fs.readFileSync(fableStatePath, 'utf-8'));
        if (fsData.circuit_breaker_tripped) circuitBreakerStatus = 'OPEN';
        if (typeof fsData.failure_streak === 'number') failureStreak = fsData.failure_streak;
      } catch {
        // Ignore
      }
    }

    let traceSpansCount = 0;
    const traceDir = path.join(this.projectDir, '.traces');
    if (fs.existsSync(traceDir)) {
      try {
        const files = fs.readdirSync(traceDir).filter(f => f.endsWith('.jsonl'));
        for (const file of files) {
          const lines = fs.readFileSync(path.join(traceDir, file), 'utf-8').trim().split('\n');
          traceSpansCount += lines.length;
        }
      } catch {
        // Ignore
      }
    }

    return {
      hasActiveWorkflow,
      currentStep,
      circuitBreakerStatus,
      failureStreak,
      retryCount,
      traceSpansCount
    };
  }

  public evaluateHealthScore(vitals: SystemVitals, wf: WorkflowVitals): HealthScore {
    const warnings: string[] = [];
    let runtimeScore = 20;
    let workflowScore = 25;
    let securityScore = 20;
    let dependenciesScore = 15;
    let integrityScore = 20;

    // Runtime deductions
    if (!vitals.bunVersion) {
      runtimeScore -= 5;
      warnings.push('Bun runtime not detected (preferred engine).');
    }
    if (!vitals.pythonVersion) {
      runtimeScore -= 5;
      warnings.push('Python 3 runtime not detected (dual-parity hooks).');
    }
    if (vitals.memory.usedPercentage > 90) {
      runtimeScore -= 5;
      warnings.push(`High system memory utilization (${vitals.memory.usedPercentage}%).`);
    }

    // Workflow deductions
    if (wf.circuitBreakerStatus === 'OPEN') {
      workflowScore -= 15;
      warnings.push('Circuit breaker is OPEN due to repeated step failures.');
    } else if (wf.failureStreak > 0) {
      workflowScore -= Math.min(10, wf.failureStreak * 3);
      warnings.push(`Current failure streak: ${wf.failureStreak}.`);
    }
    if (wf.retryCount > 3) {
      workflowScore -= 5;
      warnings.push(`Elevated retry count in workflow: ${wf.retryCount}.`);
    }

    // Security score
    const gitignore = path.join(this.projectDir, '.gitignore');
    if (!fs.existsSync(gitignore) || !fs.readFileSync(gitignore, 'utf-8').includes('.env')) {
      securityScore -= 5;
      warnings.push('.env secret exclusion rule missing from .gitignore.');
    }

    // Dependencies score
    const hasNodeModules = fs.existsSync(path.join(this.projectDir, 'node_modules'));
    if (!hasNodeModules) {
      dependenciesScore -= 5;
      warnings.push('node_modules directory missing. Dependencies not installed.');
    }

    // Integrity score
    const hasSkillsIndex = fs.existsSync(path.join(this.projectDir, 'skills-index.toon'));
    if (!hasSkillsIndex) {
      integrityScore -= 5;
      warnings.push('High-density skills-index.toon missing.');
    }

    const total = Math.max(0, Math.min(100, runtimeScore + workflowScore + securityScore + dependenciesScore + integrityScore));
    let grade: HealthGrade = 'F';
    if (total >= 95) grade = 'A+';
    else if (total >= 85) grade = 'A';
    else if (total >= 70) grade = 'B';
    else if (total >= 50) grade = 'C';

    return {
      score: total,
      grade,
      breakdown: {
        runtime: Math.max(0, runtimeScore),
        workflow: Math.max(0, workflowScore),
        security: Math.max(0, securityScore),
        dependencies: Math.max(0, dependenciesScore),
        integrity: Math.max(0, integrityScore)
      },
      warnings
    };
  }

  public getReport(): HealthReport {
    const vitals = this.collectSystemVitals();
    const wf = this.collectWorkflowVitals();
    const score = this.evaluateHealthScore(vitals, wf);

    return {
      timestamp: new Date().toISOString(),
      score,
      vitals,
      workflow: wf,
      services: {
        TS_ENGINE: vitals.bunVersion ? 'HEALTHY' : 'DEGRADED',
        PY_ENGINE: vitals.pythonVersion ? 'HEALTHY' : 'DEGRADED',
        UAHF_HOOKS: fs.existsSync(path.join(this.projectDir, '.claude', 'hooks', 'scripts')) ? 'HEALTHY' : 'DOWN',
        SKILLS_MESH: fs.existsSync(path.join(this.projectDir, 'skills-index.toon')) ? 'HEALTHY' : 'DEGRADED',
        CIRCUIT_BREAKER: wf.circuitBreakerStatus === 'CLOSED' ? 'HEALTHY' : 'DEGRADED'
      }
    };
  }

  public formatToon(report: HealthReport): string {
    return `health_telemetry{timestamp:"${report.timestamp}",score:${report.score.score},grade:"${report.score.grade}"}:
  runtime[1]{os,arch,uptime_s,mem_used_pct,bun_v,py_v}:
    ${report.vitals.platform},${report.vitals.arch},${report.vitals.uptimeSeconds},${report.vitals.memory.usedPercentage}%,${report.vitals.bunVersion || 'none'},${report.vitals.pythonVersion || 'none'}
  workflow[1]{active,step,circuit_breaker,streak,retries,spans}:
    ${report.workflow.hasActiveWorkflow},${report.workflow.currentStep || 'idle'},${report.workflow.circuitBreakerStatus},${report.workflow.failureStreak},${report.workflow.retryCount},${report.workflow.traceSpansCount}
  services[5]{service,status}:
    TS_ENGINE,${report.services.TS_ENGINE}
    PY_ENGINE,${report.services.PY_ENGINE}
    UAHF_HOOKS,${report.services.UAHF_HOOKS}
    SKILLS_MESH,${report.services.SKILLS_MESH}
    CIRCUIT_BREAKER,${report.services.CIRCUIT_BREAKER}
  breakdown{runtime:${report.score.breakdown.runtime}/20,workflow:${report.score.breakdown.workflow}/25,security:${report.score.breakdown.security}/20,deps:${report.score.breakdown.dependencies}/15,integrity:${report.score.breakdown.integrity}/20}
  warnings[${report.score.warnings.length}]:
${report.score.warnings.map(w => `    - "${w}"`).join('\n') || '    none'}`;
  }

  public formatDashboard(report: HealthReport): string {
    const s = report.score;
    const gradeColor = s.grade.startsWith('A') ? '\x1b[32m' : s.grade === 'B' ? '\x1b[34m' : '\x1b[33m';
    const reset = '\x1b[0m';
    const bold = '\x1b[1m';

    return `
${bold}══════════════════════════════════════════════════════════════════${reset}
⚡ ${bold}AGENTICWORKFLOW LIVE HEALTH ENGINE DASHBOARD${reset} ⚡
${bold}══════════════════════════════════════════════════════════════════${reset}
Composite Health Score: ${gradeColor}${bold}${s.score}/100 [Grade: ${s.grade}]${reset}
System Vitals:          OS: ${report.vitals.platform} (${report.vitals.arch}) | Uptime: ${Math.floor(report.vitals.uptimeSeconds / 60)}m
Memory Utilization:     ${report.vitals.memory.usedPercentage}% [RSS: ${Math.round(report.vitals.memory.rssBytes / 1024 / 1024)}MB]
Dual Engine Runtimes:   Bun: ${report.vitals.bunVersion || 'N/A'} | Python: ${report.vitals.pythonVersion || 'N/A'}

Workflow Status:        ${report.workflow.hasActiveWorkflow ? `ACTIVE (Step: ${report.workflow.currentStep})` : 'IDLE / READY'}
Circuit Breaker:        ${report.workflow.circuitBreakerStatus === 'CLOSED' ? '\x1b[32mCLOSED [Healthy]\x1b[0m' : '\x1b[31mOPEN [Tripped]\x1b[0m'}
Telemetry Spans:        ${report.workflow.traceSpansCount} spans recorded

Score Subsystem Breakdown:
  • Runtime Parity:      ${s.breakdown.runtime}/20
  • Workflow Vitals:     ${s.breakdown.workflow}/25
  • Security & Secrets:  ${s.breakdown.security}/20
  • Lib Dependencies:    ${s.breakdown.dependencies}/15
  • State Integrity:     ${s.breakdown.integrity}/20
${s.warnings.length > 0 ? `\nActive Advisories:\n${s.warnings.map(w => `  ⚠️  ${w}`).join('\n')}` : '\n✅ All system invariants and health parameters optimal.'}
${bold}══════════════════════════════════════════════════════════════════${reset}
`;
  }
}
