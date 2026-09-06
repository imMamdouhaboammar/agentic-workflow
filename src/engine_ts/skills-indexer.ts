/**
 * skills-indexer.ts — TypeScript Agentic Skills Mesh Reader & Intent Resolver
 * 
 * Provides runtime consumption of skills-index.json and skills-index.toon
 * for the Bun/TypeScript Agentic Engine and coding agents.
 */

import fs from 'node:fs';
import path from 'node:path';

export enum NodeType {
  SKILL = "skill",
  WORKFLOW = "workflow",
  AGENT = "agent",
  PLAYBOOK = "playbook",
  RULE = "rule",
  GUARD = "guard"
}

export interface AgenticNode {
  id: string;
  name: string;
  type: NodeType;
  path: string;
  description: string;
  version?: string;
  author?: string;
  tags?: string[];
  triggers?: string[];
  tools_required?: string[];
  rules_and_guards?: string[];
  edges?: string[];
  source_dir?: string;
}

export interface SkillsIndexPayload {
  version: string;
  generated_at: string;
  total_nodes: number;
  stats: Record<string, number>;
  nodes: AgenticNode[];
}

export class SkillsRegistry {
  private nodes: Map<string, AgenticNode> = new Map();
  private projectDir: string;
  private jsonPath: string;
  private toonPath: string;

  constructor(projectDir: string = ".") {
    this.projectDir = path.resolve(projectDir);
    this.jsonPath = path.join(this.projectDir, "skills-index.json");
    this.toonPath = path.join(this.projectDir, "skills-index.toon");
  }

  /**
   * Loads skills from skills-index.json or skills-index.toon.
   */
  public loadIndex(): boolean {
    if (fs.existsSync(this.jsonPath)) {
      try {
        const raw = fs.readFileSync(this.jsonPath, "utf-8");
        const payload: SkillsIndexPayload = JSON.parse(raw);
        this.nodes.clear();
        for (const n of payload.nodes) {
          this.nodes.set(n.id, n);
        }
        return true;
      } catch (e) {
        // Fall back to TOON
      }
    }

    if (fs.existsSync(this.toonPath)) {
      try {
        const raw = fs.readFileSync(this.toonPath, "utf-8");
        const parsed = this.parseToon(raw);
        this.nodes.clear();
        for (const n of parsed) {
          this.nodes.set(n.id, n);
        }
        return true;
      } catch (e) {
        return false;
      }
    }

    return false;
  }

  /**
   * Parses TOON content into typed AgenticNode array.
   */
  public parseToon(content: string): AgenticNode[] {
    const nodes: AgenticNode[] = [];
    let current: Partial<AgenticNode> | null = null;

    const lines = content.split("\n");
    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line || line.startsWith("#")) continue;

      if (line.startsWith("@node:")) {
        if (current && current.id) {
          nodes.push(current as AgenticNode);
        }
        current = {
          id: "",
          name: "",
          type: NodeType.SKILL,
          path: "",
          description: "",
          triggers: [],
          tools_required: [],
          rules_and_guards: [],
          edges: []
        };

        const match = line.match(/^@node:([^\s\[]+)(?:\s*\[(.*)\])?/);
        if (match) {
          current.id = match[1];
          const attrs = match[2];
          if (attrs) {
            const parts = attrs.split(/,\s*(?=[a-zA-Z_]+:)/);
            for (const p of parts) {
              if (p.includes(":")) {
                const [k, v] = p.split(":", 2);
                const key = k.trim();
                const val = v.trim().replace(/^["']|["']$/g, "");
                if (key === "type") {
                  current.type = val as NodeType;
                } else if (key === "name") {
                  current.name = val;
                } else if (key === "tools") {
                  current.tools_required = val.split(",").map(x => x.trim()).filter(Boolean);
                }
              }
            }
          }
        }
      } else if (current) {
        if (line.startsWith("path:")) {
          current.path = line.substring(5).trim();
        } else if (line.startsWith("summary:")) {
          current.description = line.substring(8).trim();
        } else if (line.startsWith("triggers:")) {
          current.triggers = line.substring(9).split(",").map(x => x.trim()).filter(Boolean);
        } else if (line.startsWith("links:")) {
          current.edges = line.substring(6).split(",").map(x => x.trim()).filter(Boolean);
        } else if (line.startsWith("rules:")) {
          current.rules_and_guards = line.substring(6).split(",").map(x => x.trim()).filter(Boolean);
        }
      }
    }

    if (current && current.id) {
      nodes.push(current as AgenticNode);
    }

    return nodes;
  }

  public getNode(id: string): AgenticNode | undefined {
    if (this.nodes.size === 0) this.loadIndex();
    return this.nodes.get(id);
  }

  public getAllNodes(): AgenticNode[] {
    if (this.nodes.size === 0) this.loadIndex();
    return Array.from(this.nodes.values());
  }

  public search(query: string, limit: number = 10): AgenticNode[] {
    if (this.nodes.size === 0) this.loadIndex();
    const terms = query.toLowerCase().split(/[\s\-_]+/).filter(Boolean);
    if (terms.length === 0) return Array.from(this.nodes.values()).slice(0, limit);

    const scored: Array<{ score: number; node: AgenticNode }> = [];
    for (const node of this.nodes.values()) {
      let score = 0;
      const haystack = `${node.id} ${node.name} ${node.description} ${(node.tags || []).join(' ')} ${(node.triggers || []).join(' ')}`.toLowerCase();

      for (const t of terms) {
        if (node.id.toLowerCase() === t) score += 20;
        else if (node.name.toLowerCase().includes(t)) score += 10;
        else if ((node.triggers || []).some(tr => tr.toLowerCase().includes(t))) score += 5;
        else if (haystack.includes(t)) score += 2;
      }

      if (score > 0) {
        scored.push({ score, node });
      }
    }

    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, limit).map(s => s.node);
  }

  public resolveForIntent(intent: string, limit: number = 5): AgenticNode[] {
    const candidates = this.search(intent, limit * 2);
    const selected: AgenticNode[] = [];
    const seenIds = new Set<string>();

    const intentLower = intent.toLowerCase();
    const needsCodeGuard = /write|code|implement|refactor|fix|feature/.test(intentLower);
    const needsTestGuard = /test|verify|qa|assert|spec/.test(intentLower);

    if (needsCodeGuard) {
      for (const gid of ["clean-code-guard", "autoreview"]) {
        const node = this.getNode(gid);
        if (node && !seenIds.has(gid)) {
          selected.push(node);
          seenIds.add(gid);
        }
      }
    }

    if (needsTestGuard) {
      for (const tid of ["test-guard", "test-driven-development", "fable-tdd"]) {
        const node = this.getNode(tid);
        if (node && !seenIds.has(tid)) {
          selected.push(node);
          seenIds.add(tid);
        }
      }
    }

    for (const c of candidates) {
      if (!seenIds.has(c.id) && selected.length < limit) {
        selected.push(c);
        seenIds.add(c.id);
      }
    }

    return selected;
  }

  public getToonContext(nodeIds?: string[]): string {
    if (this.nodes.size === 0) this.loadIndex();
    const targetNodes = nodeIds
      ? nodeIds.map(id => this.nodes.get(id)).filter((n): n is AgenticNode => Boolean(n))
      : Array.from(this.nodes.values());

    const lines: string[] = [
      "# AGENTIC SKILLS MESH (TOON CONTEXT)",
      `# Total Active Nodes: ${targetNodes.length}`,
      ""
    ];

    for (const n of targetNodes) {
      const tools = n.tools_required?.join(",") || "none";
      const triggers = n.triggers?.slice(0, 6).join(",") || "";
      const links = n.edges?.join(",") || "";
      lines.push(`@node:${n.id} [type:${n.type}, name:"${n.name}", tools:${tools}]`);
      lines.push(`path:${n.path}`);
      lines.push(`summary:${n.description}`);
      if (triggers) lines.push(`triggers:${triggers}`);
      if (links) lines.push(`links:${links}`);
      lines.push("");
    }

    return lines.join("\n");
  }
}
