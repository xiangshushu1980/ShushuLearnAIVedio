#!/usr/bin/env node
// Owner: Sean — isolated test response; no remote Task Center mutation.
const fs=require('node:fs');const task=JSON.parse(fs.readFileSync(process.env.FILM_TEST_TASK_RESPONSE,'utf8'));const a=process.argv.slice(2);if(a.length!==2||a[0]!=='info'||a[1]!==task.id)process.exit(2);process.stdout.write(JSON.stringify(task));
