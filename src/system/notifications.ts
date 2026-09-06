/**
 * src/system/notifications.ts — CLI/Terminal Banner & Desktop Notification Engine
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execSync } from 'node:child_process';
import type { NotificationPayload, NotificationRecord, NotificationLevel } from './types.ts';

export class NotificationEngine {
  private projectDir: string;
  private historyFile: string;
  private recentDispatches: Map<string, number> = new Map();

  constructor(projectDir: string = '.') {
    this.projectDir = path.resolve(projectDir);
    this.historyFile = path.join(this.projectDir, '.notifications.json');
  }

  private isHeadless(): boolean {
    return !!(process.env.CI || !process.stdout.isTTY);
  }

  public renderBanner(payload: NotificationPayload): string {
    const level = payload.level || 'INFO';
    const timestamp = new Date(payload.timestamp || Date.now()).toLocaleTimeString();
    const source = payload.source ? ` [${payload.source}]` : '';

    let color = '\x1b[36m'; // Cyan
    let icon = 'ℹ️';
    switch (level) {
      case 'SUCCESS':
        color = '\x1b[32m'; // Green
        icon = '✅';
        break;
      case 'WARN':
        color = '\x1b[33m'; // Yellow
        icon = '⚠️';
        break;
      case 'ERROR':
      case 'CRITICAL':
        color = '\x1b[31m'; // Red
        icon = '🛑';
        break;
      case 'ANNOUNCEMENT':
        color = '\x1b[35m'; // Magenta
        icon = '📢';
        break;
    }

    const reset = '\x1b[0m';
    const bold = '\x1b[1m';
    const titleLine = `${icon} ${bold}${color}${level}${reset}${bold}: ${payload.title}${source} (${timestamp})${reset}`;
    const lines = payload.message.split('\n');

    const width = Math.min(80, Math.max(60, payload.title.length + 20, ...lines.map(l => l.length + 6)));
    const border = '═'.repeat(width);

    return `
${color}╔${border}╗${reset}
  ${titleLine}
${color}╟${border}╢${reset}
${lines.map(l => `  ${l}`).join('\n')}
${color}╚${border}╝${reset}
`;
  }

  public sendDesktop(title: string, message: string, sound: boolean = true): boolean {
    if (this.isHeadless()) return false;

    const cleanTitle = title.replace(/"/g, '\\"');
    const cleanMsg = message.replace(/"/g, '\\"');
    const platform = os.platform();

    try {
      if (platform === 'darwin') {
        const soundParam = sound ? 'sound name "Glass"' : '';
        const script = `display notification "${cleanMsg}" with title "${cleanTitle}" ${soundParam}`;
        execSync(`osascript -e '${script}'`, { stdio: 'ignore' });
        return true;
      } else if (platform === 'linux') {
        execSync(`notify-send "${cleanTitle}" "${cleanMsg}"`, { stdio: 'ignore' });
        return true;
      }
    } catch {
      // Ignore desktop notification failures gracefully
    }
    return false;
  }

  public ringBell(): void {
    if (!this.isHeadless()) {
      process.stdout.write('\x07');
    }
  }

  public send(payload: NotificationPayload): NotificationRecord {
    const key = `${payload.level || 'INFO'}:${payload.title}:${payload.message.substring(0, 30)}`;
    const now = Date.now();
    const lastSent = this.recentDispatches.get(key) || 0;

    // Rate-limiting deduplication: skip if identical within 3 seconds
    if (now - lastSent < 3000) {
      return {
        id: payload.id || `notif_${now}`,
        ...payload,
        timestamp: now,
        read: false
      };
    }
    this.recentDispatches.set(key, now);

    const record: NotificationRecord = {
      id: payload.id || `notif_${now}_${Math.random().toString(36).substring(2, 6)}`,
      title: payload.title,
      message: payload.message,
      level: payload.level || 'INFO',
      source: payload.source || 'system',
      timestamp: payload.timestamp || now,
      sound: payload.sound !== false,
      desktop: payload.desktop !== false,
      terminal: payload.terminal !== false,
      actionUrl: payload.actionUrl,
      read: false
    };

    // 1. Terminal banner
    if (record.terminal) {
      console.log(this.renderBanner(record));
    }

    // 2. Audible bell
    if (record.sound && (record.level === 'CRITICAL' || record.level === 'ERROR')) {
      this.ringBell();
    }

    // 3. Desktop dispatch
    if (record.desktop) {
      this.sendDesktop(record.title, record.message, record.sound);
    }

    // 4. Save to history
    this.saveToHistory(record);
    return record;
  }

  public getHistory(): NotificationRecord[] {
    try {
      if (fs.existsSync(this.historyFile)) {
        return JSON.parse(fs.readFileSync(this.historyFile, 'utf-8'));
      }
    } catch {
      // Ignore
    }
    return [];
  }

  public clearHistory(): void {
    try {
      if (fs.existsSync(this.historyFile)) {
        fs.unlinkSync(this.historyFile);
      }
    } catch {
      // Ignore
    }
  }

  private saveToHistory(record: NotificationRecord): void {
    try {
      const history = this.getHistory();
      history.unshift(record);
      // Keep at most 50
      const trimmed = history.slice(0, 50);
      fs.writeFileSync(this.historyFile, JSON.stringify(trimmed, null, 2));
    } catch {
      // Ignore write errors
    }
  }
}
