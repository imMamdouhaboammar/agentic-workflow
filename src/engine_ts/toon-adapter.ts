/**
 * toon-adapter.ts — Official TOON v4.1 Integration for TypeScript / Bun
 * 
 * Powered by @toon-format/toon (https://github.com/toon-format/toon)
 * Enforces high-density, token-efficient serialization across all TS engine workers,
 * inter-agent communications, and conversation history context injection.
 */

import { encode, decode } from "@toon-format/toon";

export interface ToonEncodeOptions {
  delimiter?: "," | "\t" | "|";
  indent?: number;
  lengthMarker?: boolean;
}

export interface ToonDecodeOptions {
  indent?: number;
  strict?: boolean;
}

export interface TokenSavingsStats {
  jsonChars: number;
  toonChars: number;
  jsonEstimatedTokens: number;
  toonEstimatedTokens: number;
  savingsPercent: number;
  bytesRatio: number;
}

export interface ConversationTurn {
  role: string;
  content: string;
  [key: string]: any;
}

/**
 * Encodes arbitrary JavaScript/TypeScript object or array to official TOON string.
 */
export function encodeToon(data: any, options?: ToonEncodeOptions): string {
  return encode(data, options as any);
}

/**
 * Decodes official TOON formatted text back into JavaScript objects.
 */
export function decodeToon(content: string, options?: ToonDecodeOptions): any {
  return decode(content, options as any);
}

/**
 * Encodes multi-turn agent conversation history into a dense TOON tabular block.
 * Cuts context token consumption by ~40-60% compared to JSON.
 */
export function formatConversationTurns(turns: ConversationTurn[]): string {
  const normalized = turns.map((t, idx) => ({
    idx: idx + 1,
    role: t.role || "assistant",
    content: (t.content || "").replace(/\r?\n/g, " ").trim()
  }));

  return encodeToon({ dialogue: normalized });
}

/**
 * Calculates token efficiency and savings percentage vs standard formatted JSON.
 */
export function calculateTokenSavings(data: any): TokenSavingsStats {
  const jsonStr = JSON.stringify(data, null, 2);
  const toonStr = encodeToon(data);

  const jsonChars = jsonStr.length;
  const toonChars = toonStr.length;

  const jsonTokens = Math.max(1, Math.floor(jsonChars / 4));
  const toonTokens = Math.max(1, Math.floor(toonChars / 4));

  const savingsPercent = Math.max(0, Math.round((1 - toonTokens / jsonTokens) * 100));
  const bytesRatio = Number((toonChars / Math.max(1, jsonChars)).toFixed(2));

  return {
    jsonChars,
    toonChars,
    jsonEstimatedTokens: jsonTokens,
    toonEstimatedTokens: toonTokens,
    savingsPercent,
    bytesRatio
  };
}

export { encode, decode };
