/**
 * lifecycle-director.ts — TypeScript Sequential Operational Lifecycle Director
 */

import fs from 'node:fs';
import path from 'node:path';
import { IntegrationsRegistry, getDefaultRegistry } from './registry.ts';

export interface PhaseDirectives {
  phase: string;
  activeIntegrations: string[];
  systemPromptOverlay: string;
  rules: string[];
  toolsEngaged: string[];
}

export class LifecycleDirector {
  private projectDir: string;
  private registry: IntegrationsRegistry;

  constructor(projectDir: string = '.', registry?: IntegrationsRegistry) {
    this.projectDir = path.resolve(projectDir);
    this.registry = registry || getDefaultRegistry(this.projectDir);
  }

  public getPhaseDirectives(phase: string): PhaseDirectives {
    const norm = phase.toLowerCase().trim();
    const matched = this.registry.getForPhase(norm);

    const activeNames = matched.map(m => m.name);
    const toolsEngaged = matched.map(m => m.id);
    const rules: string[] = [];
    const sections: string[] = [];

    // Continuous protocols (TOON & Caveman)
    const toonItem = this.registry.get('toon');
    if (toonItem && toonItem.directives?.continuous) {
      sections.push(`### [Continuous Protocol] TOON v4.1 Serialization\n${toonItem.directives.continuous}`);
      rules.push('Format all structured datasets and task tables in TOON syntax to conserve 30-60% tokens.');
    }

    const cavemanItem = this.registry.get('caveman');
    if (cavemanItem && cavemanItem.directives?.continuous) {
      sections.push(`### [Communication Protocol] Caveman Terse Mode\n${cavemanItem.directives.continuous}`);
      rules.push('Eliminate pleasantries in logs and intermediate agent thought; keep code, paths, and errors verbatim.');
    }

    for (const item of matched) {
      if (item.directives?.[norm]) {
        sections.push(`### [${item.name}] Phase Directives (${norm})\n${item.directives[norm]}`);
        rules.push(`[${item.name}] ${item.directives[norm]}`);
      }
    }

    let overview = `## ⚡ Sequential Lifecycle Directive: ${norm.toUpperCase()} Phase`;
    if (norm === 'planning') {
      overview = `## 🧭 Sequential Lifecycle Directive: Phase 2 — Architecture & Planning
Enforce Ponytail YAGNI Ladder (Rungs 1-3):
1. Question whether every proposed component needs to exist.
2. Reuse existing helpers and stdlib before creating new abstractions.
3. Formulate verifiable Fable contracts with concrete success criteria.
4. Compile and validate OmniSkill SkillSpec contracts and dynamic DAG execution paths.`;
    } else if (norm === 'implementation') {
      overview = `## 🔨 Sequential Lifecycle Directive: Phase 3 — Production Implementation
1. Shortest working diff wins. Minimum code that works (Ponytail Rungs 4-7).
2. Fix root causes across callers/callees, not symptoms.
3. Fable Circuit Breaker active: halt speculative edits if failure streak >= 2.
4. Follow OmniSkill progressive disclosure: frontmatter <=1024 chars, core SKILL.md, references/, scripts/.`;
    } else if (norm === 'verification') {
      overview = `## 🛡️ Sequential Lifecycle Directive: Phase 4 — Verification & Quality Gates
1. Run Clean Code Guard (SOLID, 24 Imperatives).
2. Perform Ponytail anti-debt check against over-engineering.
3. Pass L0 Anti-Skip, L1 Verification, L1.5 pACS (min score >= 70), and L2 Review.
4. Enforce OmniSkill 4-Layer Validation (Artifact, Discovery, Behavior, Portability).`;
    } else if (norm === 'handoff') {
      overview = `## 🏁 Sequential Lifecycle Directive: Phase 5 — Handoff & Continuation
1. Compact session into durable continuation state (.fable/state.json, PROGRESS.md).
2. Archive run traces and ledgers in high-density TOON format.`;
    }

    const systemPromptOverlay = `${overview}\n\n` + sections.join('\n\n');

    return {
      phase: norm,
      activeIntegrations: activeNames,
      systemPromptOverlay,
      rules,
      toolsEngaged
    };
  }

  public executePrePhaseGuards(phase: string, context: Record<string, any> = {}): { allowed: boolean; warnings: string[]; actionsTaken: string[] } {
    const norm = phase.toLowerCase().trim();
    const warnings: string[] = [];
    const actionsTaken: string[] = [];
    let allowed = true;

    if (norm === 'implementation') {
      const streak = context.failure_streak || 0;
      if (streak >= 2) {
        allowed = false;
        warnings.push(`Fable Circuit Breaker TRIPPED: failure streak (${streak}) >= 2. Halting to prevent thrashing.`);
        actionsTaken.push('trip_circuit_breaker');
      }
    }

    if (norm === 'planning') {
      actionsTaken.push('enforce_ponytail_yagni_gate');
    }

    return { allowed, warnings, actionsTaken };
  }

  public executePostPhaseActions(phase: string, context: Record<string, any> = {}): { success: boolean; artifactsGenerated: string[] } {
    const norm = phase.toLowerCase().trim();
    const artifactsGenerated: string[] = [];

    if (norm === 'handoff') {
      const fableDir = path.join(this.projectDir, '.fable');
      fs.mkdirSync(fableDir, { recursive: true });
      const stateFile = path.join(fableDir, 'state.json');
      const progressFile = path.join(fableDir, 'PROGRESS.md');

      const payload = {
        trace_id: context.trace_id || `trace_${Date.now()}`,
        timestamp: new Date().toISOString(),
        status: 'COMPLETED',
        next_action: context.next_action || 'All workflow stages verified cleanly.'
      };

      fs.writeFileSync(stateFile, JSON.stringify(payload, null, 2), 'utf-8');
      fs.writeFileSync(progressFile, `# Fable Continuation Progress\n\n- Timestamp: ${payload.timestamp}\n- Trace: \`${payload.trace_id}\`\n- Next Action: ${payload.next_action}\n`, 'utf-8');

      artifactsGenerated.push(stateFile, progressFile);
    }

    return { success: true, artifactsGenerated };
  }
}
