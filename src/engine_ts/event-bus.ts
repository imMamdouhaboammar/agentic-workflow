/**
 * event-bus.ts — TypeScript Async EventBus & Append-Only Ledger.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { EngineEvent } from "./types.js";

export type EventHandler = (event: EngineEvent) => Promise<void> | void;

export class AsyncEventBus {
  private subscribers: Array<{ pattern: string; handler: EventHandler }> = [];
  private ledgerPath?: string;

  constructor(ledgerPath?: string) {
    this.ledgerPath = ledgerPath;
    if (this.ledgerPath) {
      fs.mkdirSync(path.dirname(path.resolve(this.ledgerPath)), { recursive: true });
    }
  }

  public subscribe(pattern: string, handler: EventHandler): void {
    this.subscribers.push({ pattern, handler });
  }

  public async publish(event: EngineEvent): Promise<void> {
    // 1. Append to durable ledger
    if (this.ledgerPath) {
      try {
        fs.appendFileSync(this.ledgerPath, JSON.stringify(event) + "\n", "utf-8");
      } catch (err) {
        console.error(`⚠️ [EventBus] Failed writing to ledger ${this.ledgerPath}:`, err);
      }
    }

    // 2. Dispatch to subscribers
    const matched = this.subscribers.filter(s => this.matchPattern(s.pattern, event.event_type));
    await Promise.all(
      matched.map(async s => {
        try {
          await s.handler(event);
        } catch (err) {
          console.error(`⚠️ [EventBus] Handler failed for ${event.event_type}:`, err);
        }
      })
    );
  }

  private matchPattern(pattern: string, eventType: string): boolean {
    if (pattern === "*" || pattern === eventType) return true;
    if (pattern.endsWith(".*")) {
      const prefix = pattern.slice(0, -2);
      return eventType.startsWith(prefix);
    }
    return false;
  }
}
