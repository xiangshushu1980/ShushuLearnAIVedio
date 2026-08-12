/** 任务轮询 hook：提交后 2s 轮询直到 done/error（单实例队列，不阻塞） */
import { useEffect, useRef, useState } from 'react'
import { api } from './api'

export interface TaskState {
  status: 'queued' | 'running' | 'done' | 'error'
  result?: unknown
  error?: string
  /** 运行已等待秒数 */
  elapsed: number
}

export function useTaskPoll(taskId: string | null, onDone?: (result: unknown) => void): TaskState | null {
  const [state, setState] = useState<TaskState | null>(null)
  const onDoneRef = useRef(onDone)
  onDoneRef.current = onDone

  useEffect(() => {
    if (!taskId) return
    setState({ status: 'queued', elapsed: 0 })
    const startedAt = Date.now()
    let stop = false
    const timer = setInterval(async () => {
      if (stop) return
      try {
        const t = await api.getTask(taskId)
        const elapsed = Math.round((Date.now() - (t.startedAt ?? startedAt)) / 1000)
        if (t.status === 'done') {
          setState({ status: 'done', result: t.result, elapsed })
          clearInterval(timer)
          onDoneRef.current?.(t.result)
        } else if (t.status === 'error') {
          setState({ status: 'error', error: t.error, elapsed })
          clearInterval(timer)
        } else {
          setState({ status: t.status, elapsed })
        }
      } catch (e) {
        // 网络抖动忽略，下次轮询重试
        void e
      }
    }, 2000)
    return () => {
      stop = true
      clearInterval(timer)
    }
  }, [taskId])

  return state
}
