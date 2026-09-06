/**
 * tests/test_system_engines_ts.test.ts — TypeScript / Bun Tests for 9 System Engines
 */

import { describe, it, expect, beforeEach } from 'bun:test';
import path from 'node:path';
import fs from 'node:fs';
import {
  AutoUpdater,
  AutoInstaller,
  Refresher,
  DoctorEngine,
  HealthEngine,
  DependenciesEngine,
  NotificationEngine,
  AnnouncementEngine,
  VersionTracker
} from '../src/system/index.ts';

const rootDir = path.resolve(__dirname, '..');

describe('Universal System Engines (TypeScript / Bun Parity)', () => {

  // 1. AutoUpdater
  it('AutoUpdater checks repository version and status', () => {
    const updater = new AutoUpdater(rootDir);
    const ver = updater.getLocalVersion();
    expect(typeof ver).toBe('string');
    expect(ver.length).toBeGreaterThan(0);

    const check = updater.checkForUpdates();
    expect(typeof check.hasUpdate).toBe('boolean');
    expect(check.currentVersion).toBe(ver);
    expect(check.channel).toBeDefined();
    expect(check.currentCommit.length).toBeGreaterThan(0);
  });

  // 2. AutoInstaller
  it('AutoInstaller detects multi-host agent skill targets and completions', () => {
    const installer = new AutoInstaller(rootDir);
    const targets = installer.getHostTargets();
    expect(targets.length).toBe(5);
    expect(targets.map(t => t.platform)).toContain('claude');
    expect(targets.map(t => t.platform)).toContain('gemini');
    expect(targets.map(t => t.platform)).toContain('cursor');
    expect(targets.map(t => t.platform)).toContain('codex');
    expect(targets.map(t => t.platform)).toContain('agents');

    const status = installer.checkStatus();
    expect(status.success).toBe(true);
    expect(status.systemDeps.length).toBeGreaterThanOrEqual(4);

    const zshComp = installer.generateShellCompletion('zsh');
    expect(zshComp).toContain('_agentic_workflow');
    expect(zshComp).toContain('doctor');
    expect(zshComp).toContain('health');
  });

  // 3. Refresher
  it('Refresher cleans caches and reports performance', () => {
    const refresher = new Refresher(rootDir);
    const res = refresher.refresh({
      clearBytecode: true,
      cleanLockfiles: true,
      rebuildSkillsIndex: false,
      syncIntegrations: false,
      syncHostSkills: false
    });
    expect(res.success).toBe(true);
    expect(typeof res.freedBytes).toBe('number');
    expect(typeof res.durationMs).toBe('number');
    expect(Array.isArray(res.messages)).toBe(true);
  });

  // 4. DoctorEngine
  it('DoctorEngine performs 9-point system diagnosis and remediation', () => {
    const doctor = new DoctorEngine(rootDir);
    const report = doctor.diagnose();
    expect(report.total).toBeGreaterThanOrEqual(9);
    expect(report.passed).toBeGreaterThan(0);
    expect(report.checks.some(c => c.id === 'runtime-bun')).toBe(true);
    expect(report.checks.some(c => c.id === 'runtime-python')).toBe(true);
    expect(report.checks.some(c => c.id === 'cli-permission')).toBe(true);
    expect(report.checks.some(c => c.id === 'hooks-uahf')).toBe(true);

    const fixResult = doctor.fixCheck('hooks-ledger');
    expect(fixResult.checkId).toBe('hooks-ledger');
    expect(fixResult.remediated).toBe(true);
  });

  // 5. HealthEngine
  it('HealthEngine aggregates vitals and computes TOON telemetry', () => {
    const health = new HealthEngine(rootDir);
    const report = health.getReport();

    expect(report.score.score).toBeGreaterThan(0);
    expect(['A+', 'A', 'B', 'C', 'F']).toContain(report.score.grade);
    expect(report.vitals.platform).toBeDefined();
    expect(report.services.TS_ENGINE).toBeDefined();

    const toon = health.formatToon(report);
    expect(toon).toContain('health_telemetry{');
    expect(toon).toContain('runtime[1]{os,arch,uptime_s,mem_used_pct,bun_v,py_v}:');

    const dash = health.formatDashboard(report);
    expect(dash).toContain('AGENTICWORKFLOW LIVE HEALTH ENGINE DASHBOARD');
  });

  // 6. DependenciesEngine
  it('DependenciesEngine audits packages and outputs dependency tree', () => {
    const depsEngine = new DependenciesEngine(rootDir);
    const audit = depsEngine.audit();

    expect(audit.total).toBeGreaterThan(0);
    expect(audit.satisfied).toBeGreaterThan(0);
    expect(audit.dependencies.some(d => d.name === '@toon-format/toon')).toBe(true);
    expect(audit.dependencies.some(d => d.name === 'python:asyncio')).toBe(true);

    const tree = depsEngine.formatTree();
    expect(tree).toContain('agentic-workflow@1.1.0');
    expect(tree).toContain('BUN-NPM');

    const toon = depsEngine.formatToon(audit);
    expect(toon).toContain('dependencies_audit{');
  });

  // 7. NotificationEngine
  it('NotificationEngine handles ANSI banners, deduplication, and history', () => {
    const notifier = new NotificationEngine(rootDir);
    notifier.clearHistory();

    const banner = notifier.renderBanner({
      title: 'Workflow Step Finished',
      message: 'Autonomous task executed with pACS 92/100.',
      level: 'SUCCESS'
    });
    expect(banner).toContain('SUCCESS');
    expect(banner).toContain('Workflow Step Finished');

    // Send dispatch
    const record = notifier.send({
      title: 'Test Notification 1',
      message: 'First alert message',
      level: 'INFO',
      terminal: false,
      desktop: false
    });
    expect(record.title).toBe('Test Notification 1');

    // Deduplication test (rapid second call)
    const duplicate = notifier.send({
      title: 'Test Notification 1',
      message: 'First alert message',
      level: 'INFO',
      terminal: false,
      desktop: false
    });
    expect(duplicate.title).toBe('Test Notification 1');

    const history = notifier.getHistory();
    expect(history.length).toBeGreaterThan(0);
    expect(history[0].title).toBe('Test Notification 1');

    notifier.clearHistory();
    expect(notifier.getHistory().length).toBe(0);
  });

  // 8. AnnouncementEngine
  it('AnnouncementEngine manages bulletins, unread states, and banners', () => {
    const announcer = new AnnouncementEngine(rootDir);
    const all = announcer.listAll();
    expect(all.length).toBeGreaterThanOrEqual(3);

    const first = all[0];
    announcer.markAsRead(first.id);

    const updated = announcer.listAll();
    const updatedFirst = updated.find(a => a.id === first.id);
    expect(updatedFirst?.seen).toBe(true);

    announcer.markAllAsRead();
    expect(announcer.getUnread().length).toBe(0);

    announcer.addAnnouncement({
      id: `test_ann_${Date.now()}`,
      title: 'Dynamic Test Announcement',
      body: 'Verified bulletin dispatch.',
      category: 'FEATURE',
      date: '2026-09-06',
      priority: 'high'
    });
    expect(announcer.getUnread().length).toBeGreaterThan(0);
    expect(announcer.renderBroadcastBanner()).toContain('Dynamic Test Announcement');

    // Cleanup state
    announcer.markAllAsRead();
  });

  // 9. VersionTracker
  it('VersionTracker inspects component matrix, semver diffs, and changelog', () => {
    const tracker = new VersionTracker(rootDir);
    const matrix = tracker.getVersionMatrix();
    const pkgVer = tracker.getPackageVersion();

    expect(matrix.cliVersion).toBe(pkgVer);
    expect(matrix.toonProtocolVersion).toBe('4.1.1');
    expect(matrix.components.length).toBe(7);

    expect(tracker.compareVersions('1.1.0', '1.0.5')).toBe(1);
    expect(tracker.compareVersions('1.0.5', '1.1.0')).toBe(-1);
    expect(tracker.compareVersions('1.1.0', '1.1.0')).toBe(0);

    const cl = tracker.getChangelog();
    expect(cl['1.1.0']).toBeDefined();
    expect(cl['1.1.0'].length).toBeGreaterThan(0);

    const toon = tracker.formatMatrixToon(matrix);
    expect(toon).toContain(`version_matrix{cli:"${pkgVer}"`);
    expect(toon).toContain('TOON Protocol Adapter');
  });
});
