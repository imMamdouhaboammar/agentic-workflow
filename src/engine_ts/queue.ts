/**
 * queue.ts — Pluggable Task Queue for TypeScript / Bun Engine.
 */

import { TaskInstance, TaskStatus } from "./types.js";

export interface TaskQueue {
  push(task: TaskInstance): void;
  poll(taskTypes: string[], workerId: string, leaseSeconds?: number): TaskInstance | null;
  ack(taskId: string): void;
  nack(taskId: string, requeue?: boolean): void;
  heartbeat(taskId: string, workerId: string, extendSeconds?: number): boolean;
  reclaimExpired(): string[];
  size(): number;
}

export class InMemoryTaskQueue implements TaskQueue {
  private tasks: Map<string, TaskInstance> = new Map();
  private queue: string[] = [];

  public push(task: TaskInstance): void {
    this.tasks.set(task.task_id, task);
    if (!this.queue.includes(task.task_id)) {
      this.queue.push(task.task_id);
    }
  }

  public poll(taskTypes: string[], workerId: string, leaseSeconds: number = 60): TaskInstance | null {
    for (let i = 0; i < this.queue.length; i++) {
      const taskId = this.queue[i];
      const task = this.tasks.get(taskId);
      if (task && (taskTypes.length === 0 || taskTypes.includes(task.task_def.type))) {
        this.queue.splice(i, 1);
        task.status = TaskStatus.POLLED;
        task.worker_id = workerId;
        task.lease_expires_at = Date.now() + leaseSeconds * 1000;
        return task;
      }
    }
    return null;
  }

  public ack(taskId: string): void {
    this.tasks.delete(taskId);
    const idx = this.queue.indexOf(taskId);
    if (idx !== -1) this.queue.splice(idx, 1);
  }

  public nack(taskId: string, requeue: boolean = true): void {
    const task = this.tasks.get(taskId);
    if (task) {
      task.worker_id = null;
      task.lease_expires_at = null;
      if (requeue && !this.queue.includes(taskId)) {
        task.status = TaskStatus.SCHEDULED;
        this.queue.push(taskId);
      } else if (!requeue) {
        task.status = TaskStatus.FAILED;
        this.tasks.delete(taskId);
      }
    }
  }

  public heartbeat(taskId: string, workerId: string, extendSeconds: number = 60): boolean {
    const task = this.tasks.get(taskId);
    if (task && task.worker_id === workerId) {
      task.lease_expires_at = Date.now() + extendSeconds * 1000;
      return true;
    }
    return false;
  }

  public reclaimExpired(): string[] {
    const now = Date.now();
    const reclaimed: string[] = [];
    for (const [taskId, task] of this.tasks.entries()) {
      if (task.worker_id && task.lease_expires_at && task.lease_expires_at < now) {
        task.worker_id = null;
        task.lease_expires_at = null;
        task.status = TaskStatus.SCHEDULED;
        if (!this.queue.includes(taskId)) {
          this.queue.push(taskId);
        }
        reclaimed.push(taskId);
      }
    }
    return reclaimed;
  }

  public size(): number {
    return this.queue.length;
  }
}
