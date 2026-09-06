import { describe, it, expect } from "bun:test";
import path from "node:path";
import fs from "node:fs";
import os from "node:os";
import {
  IntegrationsRegistry,
  getDefaultRegistry,
  IntegrationInstaller,
  LifecycleDirector
} from "../src/integrations/index.ts";

describe("TypeScript / Bun Integrations Subsystem", () => {
  const projectDir = path.resolve(__dirname, "..");

  it("loads default registry and includes foundation tools", () => {
    const reg = getDefaultRegistry(projectDir);
    const tools = reg.listAll().map(i => i.id);

    expect(tools).toContain("ponytail");
    expect(tools).toContain("toon");
    expect(tools).toContain("fable");
    expect(tools).toContain("caveman");
  });

  it("filters tools by phase correctly with continuous tools inclusion", () => {
    const reg = getDefaultRegistry(projectDir);

    const planning = reg.getForPhase("planning").map(i => i.id);
    expect(planning).toContain("ponytail");
    expect(planning).toContain("fable");
    expect(planning).toContain("toon");
    expect(planning).toContain("caveman");

    const impl = reg.getForPhase("implementation").map(i => i.id);
    expect(impl).toContain("ponytail");
    expect(impl).toContain("fable");

    const handoff = reg.getForPhase("handoff").map(i => i.id);
    expect(handoff).toContain("fable");
    expect(handoff).toContain("toon");
  });

  it("checks installer status and confirms foundation integrations are online", () => {
    const tempHome = fs.mkdtempSync(path.join(os.tmpdir(), "installer-test-ts-"));
    try {
      const skillsDir = path.join(tempHome, ".gemini", "config", "skills");
      const reg = getDefaultRegistry(projectDir);
      for (const item of reg.listAll()) {
        const skillNames = item.install?.skill_names || [item.id];
        for (const sname of skillNames) {
          const sDir = path.join(skillsDir, sname);
          fs.mkdirSync(sDir, { recursive: true });
          fs.writeFileSync(path.join(sDir, "SKILL.md"), `# ${sname}`);
        }
      }

      const installer = new IntegrationInstaller(projectDir, tempHome);
      const statuses = installer.checkAll();

      expect(statuses.length).toBe(5);
      const map = new Map(statuses.map(s => [s.id, s]));

      expect(map.get("ponytail")?.installed).toBe(true);
      expect(map.get("toon")?.installed).toBe(true);
      expect(map.get("fable")?.installed).toBe(true);
      expect(map.get("caveman")?.installed).toBe(true);
      expect(map.get("omni-skill")?.installed).toBe(true);
    } finally {
      fs.rmSync(tempHome, { recursive: true, force: true });
    }
  });

  it("synthesizes phase directives with Ponytail YAGNI and Fable contracts in planning", () => {
    const director = new LifecycleDirector(projectDir);
    const directives = director.getPhaseDirectives("planning");

    expect(directives.activeIntegrations).toContain("Ponytail");
    expect(directives.activeIntegrations).toContain("Fable (get-fable)");
    expect(directives.systemPromptOverlay).toContain("Ponytail YAGNI");
    expect(directives.systemPromptOverlay).toContain("TOON v4.1");
    expect(directives.systemPromptOverlay).toContain("Caveman");
  });

  it("enforces Fable circuit breaker in implementation pre-phase guards", () => {
    const director = new LifecycleDirector(projectDir);

    const ok = director.executePrePhaseGuards("implementation", { failure_streak: 0 });
    expect(ok.allowed).toBe(true);

    const tripped = director.executePrePhaseGuards("implementation", { failure_streak: 2 });
    expect(tripped.allowed).toBe(false);
    expect(tripped.actionsTaken).toContain("trip_circuit_breaker");
  });

  it("generates durable Fable continuation state on handoff post-phase action", () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "agentic-integ-test-"));
    try {
      const director = new LifecycleDirector(tmpDir);
      const post = director.executePostPhaseActions("handoff", {
        trace_id: "ts_test_trace",
        next_action: "Execute verification suite."
      });

      expect(post.success).toBe(true);
      const fableState = path.join(tmpDir, ".fable", "state.json");
      expect(fs.existsSync(fableState)).toBe(true);

      const data = JSON.parse(fs.readFileSync(fableState, "utf-8"));
      expect(data.trace_id).toBe("ts_test_trace");
      expect(data.status).toBe("COMPLETED");
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });
});
