import { describe, expect, test } from "bun:test";
import { SkillsRegistry, NodeType, AgenticNode } from "../src/engine_ts/skills-indexer";

describe("TypeScript Agentic Skills Mesh & TOON Registry", () => {
  test("SkillsRegistry parses TOON format accurately", () => {
    const registry = new SkillsRegistry(".");
    const mockToon = `
# TOON MESH SPEC
@node:mock-guard [type:guard, name:"Mock Guard", tools:run_command,view_file]
path:/path/to/mock/SKILL.md
summary:Security guard blocking unsafe operations.
triggers:guard,safety,block
links:clean-code-guard
rules:enforce-safety

@node:mock-engineer [type:agent, name:"Mock Engineer", tools:run_command]
path:/path/to/mock/engineer/SKILL.md
summary:Senior engineer implementing core features.
triggers:engineer,code,build
links:mock-guard
`;

    const nodes = registry.parseToon(mockToon);
    expect(nodes.length).toBe(2);

    const guard = nodes.find(n => n.id === "mock-guard");
    expect(guard).toBeDefined();
    expect(guard?.type).toBe(NodeType.GUARD);
    expect(guard?.name).toBe("Mock Guard");
    expect(guard?.tools_required).toContain("run_command");
    expect(guard?.tools_required).toContain("view_file");
    expect(guard?.description).toBe("Security guard blocking unsafe operations.");
    expect(guard?.triggers).toContain("safety");
    expect(guard?.edges).toContain("clean-code-guard");
    expect(guard?.rules_and_guards).toContain("enforce-safety");

    const agent = nodes.find(n => n.id === "mock-engineer");
    expect(agent).toBeDefined();
    expect(agent?.type).toBe(NodeType.AGENT);
  });

  test("SkillsRegistry loads project skills-index.json if present", () => {
    const registry = new SkillsRegistry(".");
    const loaded = registry.loadIndex();
    expect(loaded).toBe(true);

    const all = registry.getAllNodes();
    expect(all.length).toBeGreaterThan(0);

    // Search for clean code guard
    const searchResults = registry.search("guard", 5);
    expect(searchResults.length).toBeGreaterThan(0);
    expect(searchResults.some(n => n.id.includes("guard"))).toBe(true);

    // Test intent resolution
    const resolved = registry.resolveForIntent("write code and run tests", 4);
    expect(resolved.length).toBeGreaterThan(0);

    // Test TOON context formatting
    const toonContext = registry.getToonContext(["clean-code-guard", "test-guard"]);
    expect(toonContext).toContain("@node:");
    expect(toonContext).toContain("path:");
    expect(toonContext).toContain("summary:");
  });
});
