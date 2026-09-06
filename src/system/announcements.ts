/**
 * src/system/announcements.ts — Announcement & Bulletin Engine
 */

import fs from 'node:fs';
import path from 'node:path';
import type { AnnouncementItem, AnnouncementState, AnnouncementCategory } from './types.ts';

export class AnnouncementEngine {
  private projectDir: string;
  private announcementsFile: string;
  private stateFile: string;

  constructor(projectDir: string = '.') {
    this.projectDir = path.resolve(projectDir);
    this.announcementsFile = path.join(this.projectDir, '.announcements.json');
    this.stateFile = path.join(this.projectDir, '.announcements_seen.json');
  }

  private getDefaultAnnouncements(): AnnouncementItem[] {
    return [
      {
        id: 'ann_v110_engines',
        title: 'Universal System Engines Suite Online',
        body: 'AgenticWorkflow v1.1.0 now integrates 9 core toolchain engines: Auto-Updater, Auto-Installer, Refresher, Doctor, Health Engine, Dependencies Engine, Notifications, Announcements, and Version Tracker with dual-runtime parity.',
        category: 'FEATURE',
        date: '2026-09-06',
        version: '1.1.0',
        priority: 'high'
      },
      {
        id: 'ann_toon_v41',
        title: 'TOON Protocol v4.1 Released',
        body: 'Token-Oriented Object Notation (v4.1) delivers 30-60% token compression across all multi-agent dialogues and workflow telemetry.',
        category: 'UPDATE',
        date: '2026-09-01',
        version: '1.0.5',
        priority: 'normal'
      },
      {
        id: 'ann_uahf_online',
        title: 'Universal Agentic Hooks Framework (UAHF)',
        body: 'UAHF governs Claude Code, Cursor, Codex, OpenCode, and shell processes with zero-drift safety policies.',
        category: 'FEATURE',
        date: '2026-08-25',
        version: '1.0.0',
        priority: 'normal'
      }
    ];
  }

  private getState(): AnnouncementState {
    try {
      if (fs.existsSync(this.stateFile)) {
        const raw = JSON.parse(fs.readFileSync(this.stateFile, 'utf-8'));
        const seenIds = Array.isArray(raw.seenIds) ? raw.seenIds : (Array.isArray(raw.seen_ids) ? raw.seen_ids : []);
        return { seenIds, lastChecked: raw.lastChecked || raw.last_checked || new Date().toISOString() };
      }
    } catch {
      // Ignore
    }
    return { seenIds: [], lastChecked: new Date().toISOString() };
  }

  private saveState(state: AnnouncementState): void {
    try {
      const data = {
        seenIds: state.seenIds,
        seen_ids: state.seenIds,
        lastChecked: state.lastChecked
      };
      fs.writeFileSync(this.stateFile, JSON.stringify(data, null, 2));
    } catch {
      // Ignore
    }
  }

  public listAll(): Array<AnnouncementItem & { seen: boolean }> {
    let list = this.getDefaultAnnouncements();
    if (fs.existsSync(this.announcementsFile)) {
      try {
        const custom = JSON.parse(fs.readFileSync(this.announcementsFile, 'utf-8'));
        if (Array.isArray(custom)) {
          list = [...custom, ...list];
        }
      } catch {
        // Ignore
      }
    }

    const state = this.getState();
    return list.map(item => ({
      ...item,
      seen: state.seenIds.includes(item.id)
    }));
  }

  public getUnread(): AnnouncementItem[] {
    return this.listAll().filter(a => !a.seen);
  }

  public markAsRead(id: string): void {
    const state = this.getState();
    if (!state.seenIds.includes(id)) {
      state.seenIds.push(id);
      this.saveState(state);
    }
  }

  public markAllAsRead(): void {
    const all = this.listAll();
    const state: AnnouncementState = {
      seenIds: all.map(a => a.id),
      lastChecked: new Date().toISOString()
    };
    this.saveState(state);
  }

  public addAnnouncement(item: AnnouncementItem): void {
    let custom: AnnouncementItem[] = [];
    if (fs.existsSync(this.announcementsFile)) {
      try {
        custom = JSON.parse(fs.readFileSync(this.announcementsFile, 'utf-8'));
      } catch {
        // Ignore
      }
    }
    custom.unshift(item);
    fs.writeFileSync(this.announcementsFile, JSON.stringify(custom, null, 2));
  }

  public renderBroadcastBanner(): string | null {
    const unread = this.getUnread();
    if (unread.length === 0) return null;

    const top = unread[0];
    const color = '\x1b[35m'; // Magenta
    const reset = '\x1b[0m';
    const bold = '\x1b[1m';

    return `\n${color}📢 [Announcement]${reset} ${bold}${top.title}${reset} (${top.date})\n   ${top.body.substring(0, 100)}${top.body.length > 100 ? '...' : ''}\n   Run 'agentic-workflow announcements' to view all.\n`;
  }
}
