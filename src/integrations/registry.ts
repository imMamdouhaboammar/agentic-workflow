/**
 * registry.ts — TypeScript Integrations Registry & Manifest Manager
 */

import fs from 'node:fs';
import path from 'node:path';

export interface IntegrationDefinition {
  id: string;
  name: string;
  repo: string;
  description: string;
  category: string;
  lifecycle_phases: string[];
  install: Record<string, any>;
  detection: Record<string, any>;
  directives: Record<string, string>;
}

export class IntegrationsRegistry {
  private integrations: Map<string, IntegrationDefinition> = new Map();
  private manifestPath: string | null = null;

  constructor(manifestPath?: string) {
    if (manifestPath && fs.existsSync(manifestPath)) {
      this.loadFromFile(manifestPath);
    }
  }

  public loadFromFile(filePath: string): void {
    this.manifestPath = path.resolve(filePath);
    const content = fs.readFileSync(this.manifestPath, 'utf-8');
    const data = JSON.parse(content);
    this.integrations.clear();
    for (const item of data.integrations || []) {
      this.integrations.set(item.id, item);
    }
  }

  public saveToFile(targetPath?: string): void {
    const dest = targetPath || this.manifestPath;
    if (!dest) {
      throw new Error("No target path specified for saving integrations manifest.");
    }
    const data = {
      version: "1.0.0",
      description: "Declarative registry of supportive tools, frameworks, and agentic skills for AgenticWorkflow",
      integrations: Array.from(this.integrations.values())
    };
    fs.writeFileSync(dest, JSON.stringify(data, null, 2), 'utf-8');
  }

  public register(item: IntegrationDefinition): void {
    this.integrations.set(item.id, item);
  }

  public get(id: string): IntegrationDefinition | undefined {
    return this.integrations.get(id);
  }

  public listAll(): IntegrationDefinition[] {
    return Array.from(this.integrations.values());
  }

  public getForPhase(phase: string): IntegrationDefinition[] {
    const norm = phase.toLowerCase().trim();
    return this.listAll().filter(item => 
      item.lifecycle_phases.includes("continuous") || item.lifecycle_phases.includes(norm)
    );
  }
}

export function getDefaultRegistry(projectDir: string = "."): IntegrationsRegistry {
  let manifestPath = path.join(path.resolve(projectDir), "integrations.json");
  if (!fs.existsSync(manifestPath)) {
    const rootFallback = path.resolve(__dirname, "..", "..", "integrations.json");
    if (fs.existsSync(rootFallback)) {
      manifestPath = rootFallback;
    }
  }
  return new IntegrationsRegistry(manifestPath);
}
