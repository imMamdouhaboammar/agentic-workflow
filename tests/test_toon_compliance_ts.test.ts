import { describe, expect, test } from "bun:test";
import {
  encodeToon,
  decodeToon,
  formatConversationTurns,
  calculateTokenSavings
} from "../src/engine_ts/toon-adapter";

describe("TypeScript / Bun Official TOON v4.1 Integration", () => {
  test("Encodes and decodes uniform object arrays with tabular format", () => {
    const data = {
      users: [
        { id: 1, name: "Ada", role: "admin" },
        { id: 2, name: "Bob", role: "user" }
      ]
    };

    const encoded = encodeToon(data);
    expect(encoded).toContain("users[2]{id,name,role}:");
    expect(encoded).toContain("1,Ada,admin");
    expect(encoded).toContain("2,Bob,user");

    const decoded = decodeToon(encoded);
    expect(decoded).toEqual(data);
  });

  test("Encodes primitive arrays as inline headers", () => {
    const data = { tags: ["alpha", "beta", "gamma"] };
    const encoded = encodeToon(data);
    expect(encoded).toContain("tags[3]: alpha,beta,gamma");

    const decoded = decodeToon(encoded);
    expect(decoded).toEqual(data);
  });

  test("Formats multi-turn dialogue into high-density TOON context", () => {
    const turns = [
      { role: "user", content: "Run security audit" },
      { role: "assistant", content: "Audit completed with zero warnings" }
    ];

    const toonDialogue = formatConversationTurns(turns);
    expect(toonDialogue).toContain("dialogue[2]{idx,role,content}:");
    expect(toonDialogue).toContain("1,user,Run security audit");
    expect(toonDialogue).toContain("2,assistant,Audit completed with zero warnings");
  });

  test("Measures token savings of >30% over verbose JSON", () => {
    const data = {
      services: Array.from({ length: 15 }, (_, i) => ({
        id: `srv-${i + 1}`,
        host: `10.0.0.${i + 1}`,
        status: "healthy",
        port: 8000 + i
      }))
    };

    const stats = calculateTokenSavings(data);
    expect(stats.savingsPercent).toBeGreaterThanOrEqual(30);
    expect(stats.toonChars).toBeLessThan(stats.jsonChars);
    expect(stats.toonEstimatedTokens).toBeLessThan(stats.jsonEstimatedTokens);
  });
});
