/**
 * 单实例任务队列（简单版）
 * 所有耗时生成（实体抽取/设定图/音色）统一走这里：
 * - 提交立即返回 taskId，后台异步执行（不阻塞请求）
 * - 同一时刻仅一个任务运行（running 时新任务返回冲突，不排队）
 * - 前端轮询 GET /api/tasks/:id 获取状态
 */
export type TaskKind = 'extract' | 'art' | 'voice'

export interface Task {
  id: string
  kind: TaskKind
  status: 'queued' | 'running' | 'done' | 'error'
  input: Record<string, unknown>
  result?: unknown
  error?: string
  createdAt: number
  startedAt?: number
  finishedAt?: number
}

type Runner = (task: Task) => Promise<unknown>

const tasks = new Map<string, Task>()
const runners = new Map<TaskKind, Runner>()
let current: Task | null = null

let seq = 0
function nextId(): string {
  seq += 1
  return `t${Date.now().toString(36)}${seq.toString(36)}`
}

export function registerRunner(kind: TaskKind, runner: Runner): void {
  runners.set(kind, runner)
}

/**
 * 提交任务。已有运行中任务时返回 { conflict: true, current }
 */
export function submitTask(kind: TaskKind, input: Record<string, unknown>): { task?: Task; conflict?: boolean; current?: Task } {
  if (current) {
    return { conflict: true, current }
  }
  const task: Task = { id: nextId(), kind, status: 'queued', input, createdAt: Date.now() }
  tasks.set(task.id, task)
  void run(task)
  return { task }
}

async function run(task: Task): Promise<void> {
  const runner = runners.get(task.kind)
  if (!runner) {
    task.status = 'error'
    task.error = `未注册任务类型: ${task.kind}`
    task.finishedAt = Date.now()
    return
  }
  current = task
  task.status = 'running'
  task.startedAt = Date.now()
  try {
    task.result = await runner(task)
    task.status = 'done'
  } catch (e) {
    task.status = 'error'
    task.error = (e as Error).message
  } finally {
    task.finishedAt = Date.now()
    current = null
  }
}

export function getTask(id: string): Task | undefined {
  return tasks.get(id)
}

export function getCurrentTask(): Task | null {
  return current
}

/** 清理已完成任务（防内存膨胀；简单版保留最近 20 个） */
export function pruneTasks(): void {
  if (tasks.size <= 20) return
  const done = [...tasks.values()].filter((t) => t.status === 'done' || t.status === 'error').sort((a, b) => (b.finishedAt ?? 0) - (a.finishedAt ?? 0))
  for (const t of done.slice(20)) tasks.delete(t.id)
}
