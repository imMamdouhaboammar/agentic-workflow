/**
 * src/system/types.ts — Shared Type Definitions for AgenticWorkflow System Engines
 */

// 1. Auto-Updater Types
export type UpdateStrategy = 'fast-forward' | 'stash-and-pull' | 'force-reset';

export interface UpdateCheckResult {
  hasUpdate: boolean;
  currentCommit: string;
  currentVersion: string;
  remoteCommit: string;
  remoteVersion?: string;
  branch: string;
  behindCount: number;
  commits: Array<{ hash: string; message: string; date: string }>;
  channel: 'stable' | 'beta' | 'nightly';
}

export interface UpdateOptions {
  strategy?: UpdateStrategy;
  force?: boolean;
  branch?: string;
  autoReinstall?: boolean;
  autoRefresh?: boolean;
}

export interface UpdateResult {
  success: boolean;
  previousCommit: string;
  newCommit: string;
  message: string;
  stashed: boolean;
  reinstalled: boolean;
  refreshed: boolean;
}

export interface RollbackResult {
  success: boolean;
  rolledBackTo: string;
  message: string;
}

// 2. Auto-Installer Types
export type HostPlatform = 'claude' | 'gemini' | 'cursor' | 'codex' | 'agents' | 'cli-symlink' | 'shell-profile';

export interface InstallTarget {
  name: string;
  platform: HostPlatform;
  path: string;
  installed: boolean;
}

export interface InstallOptions {
  targets?: HostPlatform[];
  globalBin?: boolean;
  updateShellRc?: boolean;
  provisionTools?: boolean;
  dryRun?: boolean;
  force?: boolean;
}

export interface InstallReport {
  success: boolean;
  installedTargets: InstallTarget[];
  skippedTargets: InstallTarget[];
  binLinked: string[];
  shellConfigured: string[];
  systemDeps: Array<{ name: string; available: boolean; version?: string }>;
  messages: string[];
}

// 3. Refresher Types
export interface RefreshOptions {
  clearBytecode?: boolean;
  clearTemp?: boolean;
  rebuildSkillsIndex?: boolean;
  syncIntegrations?: boolean;
  syncHostSkills?: boolean;
  resetRiskScores?: boolean;
  cleanLockfiles?: boolean;
}

export interface RefreshReport {
  success: boolean;
  clearedItems: string[];
  freedBytes: number;
  skillsReindexed: boolean;
  integrationsSynced: boolean;
  hostsSynced: string[];
  durationMs: number;
  messages: string[];
}

// 4. Doctor Types
export type DoctorSeverity = 'PASS' | 'WARN' | 'FAIL';

export interface DoctorCheckItem {
  id: string;
  category: 'runtime' | 'cli' | 'git' | 'dependencies' | 'state' | 'hooks' | 'skills' | 'integrations' | 'security';
  title: string;
  status: DoctorSeverity;
  details: string;
  recommendation?: string;
  fixable: boolean;
}

export interface DoctorReport {
  passed: number;
  warned: number;
  failed: number;
  total: number;
  checks: DoctorCheckItem[];
  overallHealthy: boolean;
  timestamp: string;
}

export interface FixResult {
  checkId: string;
  remediated: boolean;
  message: string;
}

// 5. Health Engine Types
export type HealthGrade = 'A+' | 'A' | 'B' | 'C' | 'F';

export interface SystemVitals {
  platform: string;
  arch: string;
  uptimeSeconds: number;
  memory: {
    totalBytes: number;
    freeBytes: number;
    rssBytes: number;
    usedPercentage: number;
  };
  disk: {
    freeBytes?: number;
    totalBytes?: number;
  };
  nodeVersion: string;
  bunVersion?: string;
  pythonVersion?: string;
}

export interface WorkflowVitals {
  hasActiveWorkflow: boolean;
  currentStep?: string;
  circuitBreakerStatus: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
  failureStreak: number;
  retryCount: number;
  traceSpansCount: number;
}

export interface HealthScore {
  score: number; // 0 - 100
  grade: HealthGrade;
  breakdown: {
    runtime: number;     // max 20
    workflow: number;    // max 25
    security: number;    // max 20
    dependencies: number;// max 15
    integrity: number;   // max 20
  };
  warnings: string[];
}

export interface HealthReport {
  timestamp: string;
  score: HealthScore;
  vitals: SystemVitals;
  workflow: WorkflowVitals;
  services: Record<string, 'HEALTHY' | 'DEGRADED' | 'DOWN'>;
}

// 6. Dependencies Engine Types
export type DependencyType = 'bun-npm' | 'python' | 'supportive-tool' | 'system-binary';

export interface DependencyItem {
  name: string;
  type: DependencyType;
  requiredVersion?: string;
  installedVersion?: string;
  status: 'SATISFIED' | 'OUTDATED' | 'MISSING' | 'INCOMPATIBLE';
  description?: string;
  location?: string;
}

export interface DependencyAuditReport {
  total: number;
  satisfied: number;
  missing: number;
  outdated: number;
  incompatible: number;
  dependencies: DependencyItem[];
  allSatisfied: boolean;
}

// 7. Notifications Engine Types
export type NotificationLevel = 'INFO' | 'SUCCESS' | 'WARN' | 'ERROR' | 'CRITICAL' | 'ANNOUNCEMENT';

export interface NotificationPayload {
  id?: string;
  title: string;
  message: string;
  level?: NotificationLevel;
  source?: string;
  timestamp?: number;
  sound?: boolean;
  desktop?: boolean;
  terminal?: boolean;
  actionUrl?: string;
}

export interface NotificationRecord extends NotificationPayload {
  id: string;
  timestamp: number;
  read: boolean;
}

// 8. Announcement Engine Types
export type AnnouncementCategory = 'SECURITY' | 'FEATURE' | 'UPDATE' | 'TIP' | 'MAINTENANCE';

export interface AnnouncementItem {
  id: string;
  title: string;
  body: string;
  category: AnnouncementCategory;
  date: string;
  version?: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  url?: string;
}

export interface AnnouncementState {
  seenIds: string[];
  lastChecked: string;
}

// 9. Version Tracker Types
export interface ComponentVersion {
  name: string;
  version: string;
  channel: string;
  path?: string;
}

export interface VersionMatrix {
  cliVersion: string;
  tsEngineVersion: string;
  pyEngineVersion: string;
  toonProtocolVersion: string;
  uahfHooksVersion: string;
  gitCommit: string;
  gitBranch: string;
  gitClean: boolean;
  buildDate: string;
  components: ComponentVersion[];
}

export interface MigrationStep {
  fromVersion: string;
  toVersion: string;
  name: string;
  description: string;
  executed: boolean;
  timestamp?: string;
}
