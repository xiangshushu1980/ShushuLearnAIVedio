#!/usr/bin/env node
// Node.js Worker probe for the same Conductor REST contract used by conductor_probe.py.
const base = process.argv[2] || 'http://127.0.0.1:18080';
const suffix = Math.random().toString(16).slice(2, 10);
const task = `t32_node_${suffix}`;
const workflow = `t32_node_probe_${suffix}`;

async function request(path, options = {}) {
  const response = await fetch(`${base}${path}`, {
    headers: {'content-type': 'application/json'}, ...options,
  });
  const text = await response.text();
  if (!response.ok) throw new Error(`${response.status} ${path}: ${text}`);
  try { return JSON.parse(text); } catch { return text; }
}

await request('/api/metadata/taskdefs', {method: 'POST', body: JSON.stringify([{
  name: task, description: 'T-32 Node worker probe', retryCount: 1,
  timeoutSeconds: 60, responseTimeoutSeconds: 20,
}])});
await request('/api/metadata/workflow', {method: 'POST', body: JSON.stringify({
  name: workflow, version: 1, schemaVersion: 2, restartable: true,
  timeoutSeconds: 120, inputParameters: ['topic'],
  tasks: [{name: task, taskReferenceName: task, type: 'SIMPLE', workflowTaskType: 'SIMPLE', inputParameters: {topic: '${workflow.input.topic}'}}],
  outputParameters: {result: "${" + task + ".output.result}"},
})});
const id = await request(`/api/workflow/${workflow}`, {method: 'POST', body: JSON.stringify({topic: 'Node.js Worker 验证'})});
const workerId = `node-probe-${suffix}`;
for (;;) {
  const state = await request(`/api/workflow/${id}`);
  if (['COMPLETED', 'FAILED', 'TERMINATED', 'TIMED_OUT'].includes(state.status)) {
    console.log(JSON.stringify({workflow, workflow_id: id, status: state.status}));
    break;
  }
  const polled = await request(`/api/tasks/poll/${task}?workerid=${workerId}`);
  if (polled?.taskId) {
    const result = {stage: 'node', artifact_ref: `artifact://conductor-node/${task}`};
    await request('/api/tasks', {method: 'POST', body: JSON.stringify({
      taskId: polled.taskId, workflowInstanceId: id, workerId,
      status: 'COMPLETED', outputData: {result},
    })});
  }
  await new Promise(resolve => setTimeout(resolve, 150));
}
