# H3 run record

Copy this file to `.production-runs/<task-or-project>/<run-id>/run-log.md` before submitting a generation. Keep it as a concise chronological record, not a retrospective reconstruction from chat. Update it after meaningful decisions, submissions, retries, and reviews. Preserve failed runs. The exact prompt and workflow/history artifacts remain separate files linked here.

## Run identity and goal

- Run ID / revision:
- Task / executing agent:
- Started / finished (local timezone):
- Status: planned / running / generated / reviewed / failed / preflight-blocked
- Question this run is testing:
- Acceptance criteria:

## Inputs and authority

| Input | Path and SHA-256 | Role / what it controls | Limits or uncertainty |
|---|---|---|---|
| Source image/video/scene plan | | | |
| Other references | | | |

## Scene and camera constraint card

- Scene anchor and evidence source:
- Layout relations to preserve:
- Objects fixed / allowed to move:
- Start view and framing (known vs estimated):
- Camera path, direction, amount, speed, target:
- End view / endpoint condition:
- Height, distance, projection (known vs estimated):
- Required invariants and prohibited changes:
- Unknowns intentionally left unspecified:

## Prompt revisions

Record every submitted prompt as an immutable file (for example `prompt-v001.txt`) and link its hash. Note what changed from the preceding version and the reason. Do not overwrite earlier versions.

| Version | Prompt file / SHA-256 | Change from prior version | Evidence or reason |
|---|---|---|---|
| v001 | | Initial wording | |

## Workflow and execution

- Mode and reason:
- Workflow/API JSON and SHA-256:
- Model/checkpoint and relevant node versions:
- Actual generation settings (resolution, frames, fps, seed, steps/sampler, adapters/LoRAs, guidance values):
- ComfyUI prompt/job ID and submission receipt/history:
- GPU lease/resource evidence (acquired, renewed, released):
- Output path/hash, actual dimensions, frame count and duration:
- Peak VRAM / runtime, if available:

If blocked before inference, set status to `preflight-blocked`, label proposed prompt/settings as **planned**, and state that no job was submitted. Keep generation/QC fields as not run; do not draw a model or prompt-efficacy conclusion from a preflight-only attempt.

### Chronological events

| Time | Action / observation | Result, error, or decision | Evidence path / ID |
|---|---|---|---|
| | | | |

Include preflight results, queue state, submission outcome, timeouts and how they were resolved, retries, manual edits, and cleanup. If a step was skipped, state why. Never retry a timed-out submission until queue/history has established whether it already ran.

## Review and diagnosis

| Check | Observation | Pass / issue / not checked | Frame/time or evidence |
|---|---|---|---|
| First-frame match | | | |
| Object identity/count and layout | | | |
| Camera direction/path and view coverage | | | |
| Cuts, zoom, height/distance stability | | | |
| Temporal continuity / scene drift | | | |
| Other task criteria | | | |

- What followed the prompt:
- What did not follow it:
- Issue category (prompt / reference / model variance / workflow / review / unknown):
- Best-supported cause; separate observation from hypothesis:
- Is the output useful for its intended downstream step? Why?

## Handoff and skill improvement

- Current conclusion and confidence:
- Best prompt/workflow revision and why:
- Next controlled experiment (change one main variable):
- Reusable skill/workflow issue found:
- Proposed skill change, with evidence link:
- Limits that should remain explicit:
- Reviewer/subagent can resume from:

Do not change a shared skill solely because one output failed. Record the reproducible observation and a narrowly testable improvement proposal; update the skill after review shows it generalizes or corrects a demonstrated workflow gap.
