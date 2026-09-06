/**
 * types.ts — TypeScript Interfaces and Enums for Agentic Engine.
 * 
 * Provides 100% schema parity with Python engine and shared JSON specs.
 */

export enum TaskStatus {
  SCHEDULED = "SCHEDULED",
  POLLED = "POLLED",
  IN_PROGRESS = "IN_PROGRESS",
  GATE_EVALUATING = "GATE_EVALUATING",
  DIAGNOSING = "DIAGNOSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
  TIMED_OUT = "TIMED_OUT",
  SKIPPED = "SKIPPED",
  CANCELLED = "CANCELLED"
}

export enum WorkflowStatus {
  RUNNING = "RUNNING",
  PAUSED = "PAUSED",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
  CANCELLED = "CANCELLED"
}

export enum BackoffType {
  FIXED = "FIXED",
  LINEAR = "LINEAR",
  EXPONENTIAL = "EXPONENTIAL"
}

export enum AgentRole {
  ORCHESTRATOR = "orchestrator",
  RESEARCHER = "researcher",
  ARCHITECT = "architect",
  ENGINEER = "engineer",
  REVIEWER = "reviewer",
  FACT_CHECKER = "fact_checker",
  CLEAN_CODE_GUARD = "clean_code_guard",
  RECOVERY = "recovery"
}

export interface RetryPolicy {
  max_retries: number;
  delay_seconds: number;
  backoff_rate: BackoffType;
}

export interface CircuitBreakerConfig {
  failure_threshold: number;
  cooldown_seconds: number;
}

export interface TaskDefinition {
  id: string;
  type: string; // system.code, system.wait, agent.task, agent.human, agent.review
  name?: string;
  description?: string;
  role?: AgentRole;
  deliverable_path?: string;
  criteria?: string[];
  input_parameters?: Record<string, any>;
  retry_policy?: RetryPolicy;
  timeout_seconds?: number;
  circuit_breaker?: CircuitBreakerConfig;
  compensation_task?: string;
  branches?: Record<string, any>;
}

export interface StageDefinition {
  id: string;
  name: string;
  stage_type?: "research" | "planning" | "implementation" | "verification" | "custom";
  tasks: TaskDefinition[];
}

export interface WorkflowDefinition {
  name: string;
  version: string;
  description?: string;
  stages: StageDefinition[];
  input_parameters?: Record<string, any>;
  timeout_seconds?: number;
  failure_workflow?: string;
}

export interface TaskInstance {
  task_id: string;
  workflow_id: string;
  stage_id: string;
  task_def: TaskDefinition;
  status: TaskStatus;
  attempt: number;
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  worker_id?: string | null;
  scheduled_at: number;
  started_at?: number | null;
  completed_at?: number | null;
  lease_expires_at?: number | null;
  pacs_score?: number | null;
  gate_verdict?: string | null;
  error_message?: string | null;
  trace_id: string;
}

export interface WorkflowInstance {
  workflow_id: string;
  workflow_def: WorkflowDefinition;
  trace_id: string;
  status: WorkflowStatus;
  current_stage_index: number;
  tasks: Record<string, TaskInstance>;
  variables: Record<string, any>;
  outputs: Record<string, any>;
  started_at: number;
  completed_at?: number | null;
  autopilot_enabled: boolean;
  error_message?: string | null;
}

export interface EngineEvent {
  event_id: string;
  event_type: string;
  timestamp: number;
  trace_id: string;
  workflow_id: string;
  stage_id?: string | null;
  task_id?: string | null;
  worker_id?: string | null;
  payload?: Record<string, any>;
}
