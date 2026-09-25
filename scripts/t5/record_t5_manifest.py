#!/usr/bin/env python3
"""Append the T5 stage record to the existing output manifest. Owner: Sean."""
import json
from pathlib import Path

path = Path("/home/sean/projects/ComfyUI/output/sean_h3_character_reference_test/sean_h3_character_reference_manifest.json")
data = json.loads(path.read_text(encoding="utf-8"))
data["t5_reference_role_conflict"] = {
    "status": "phase_1_complete_preliminary",
    "assets_manifest": "t5_reference_roles/t5_asset_manifest.json",
    "smoke_cases": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t5_smoke_cases.json.results.json",
    "quality_cases": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t5_ab_quality_cases.json.results.json",
    "conditions": {"resolution": "768x448", "frames": 124, "steps": 20, "sampler": "res_multistep", "seeds": [20260924, 20260925, 20260926]},
    "cells": {
        "T5-A": ["F_face_identity", "W_wardrobe_full"],
        "T5-B": ["F_face_identity", "WB_wardrobe_body"]
    },
    "runs": 6,
    "successful": 6,
    "preliminary_observation": "WB showed no obvious identity swap or extra person in sampled frames; some samples had larger subject/clearer wardrobe detail, but composition and subject-occupancy confounds remain.",
    "not_a_conclusion": "Do not promote wardrobe_body to the skill baseline before anonymous scoring and view-trigger cells T5-C/T5-D/T5-E.",
    "view_trigger_phase": {
        "D": ["F_face_identity", "WB_wardrobe_body", "S_view_side"],
        "E": ["F_face_identity", "WB_wardrobe_body", "B_view_back"],
        "quality_runs": 6,
        "successful": 6,
        "observation": "The side/back endpoints were reached in sampled frames without obvious identity drift; causal benefit over no side/back reference remains untested and requires D0/E0.",
        "results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t5_de_quality_cases.json.results.json"
    },
    "no_view_ablation_phase": {
        "cells": {
            "D0": ["F_face_identity", "WB_wardrobe_body"],
            "E0": ["F_face_identity", "WB_wardrobe_body"]
        },
        "quality_runs": 6,
        "successful": 6,
        "results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t5_d0e0_quality_cases.json.results.json",
        "observation": "Without dedicated side/back reference images, D0 and E0 still reached reasonable strict-side and direct-back endpoints in all sampled formal runs; seed-to-seed framing/scale varied, but no obvious identity or wardrobe failure was observed.",
        "interpretation": "For this restrained static turn, dedicated side/back references are not yet shown necessary. Their benefit remains plausible for difficult poses, occlusion, dynamic action, or exact rear/side accessory detail.",
        "status": "phase_2_complete_preliminary"
    },
    "three_quarter_asset_phase": {
        "status": "asset_valid_but_h3_endpoint_control_unproven",
        "attempt": "local Krea2 Identity Edit from accepted front reference",
        "output": "t5_q_krea2_3q_00001_.png",
        "qc": "failed: output remained near-front rather than an approximately 45-degree three-quarter view",
        "h3_runs_started": 0,
        "h3_quality_cases": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t5_q_quality_cases.json.results.json",
        "h3_runs": 6,
        "h3_successful": 6,
        "endpoint_observation": "Q and no-Q conditions both tended toward a side-facing endpoint; Q did not reliably preserve the approximately 45-degree target across seeds.",
        "interpretation": "The Q image was accepted as a valid asset and did not cause obvious identity or wardrobe failure, but this batch does not demonstrate causal endpoint-angle control or a quality gain from Q.",
        "next": "do not promote Q as mandatory; use a more explicit endpoint/shot test only if three-quarter control is production-critical"
    },
    "full_wardrobe_plus_three_quarter_phase": {
        "cell": "F+W+Q",
        "results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t5_f_quality_cases.json.results.json",
        "runs": 3,
        "successful": 3,
        "observation": "Adding ordinary full-body W alongside face F and three-quarter Q did not show a clear endpoint or identity/wardrobe benefit over the F+WB+Q comparison under the same restrained turn setup.",
        "status": "phase_3_complete_preliminary"
    },
    "closeup_face_phase": {
        "cells": ["F+W", "F+WB"],
        "results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t5_closeup_quality_cases.json.results.json",
        "runs": 6,
        "successful": 6,
        "conditions": {"resolution": "768x448", "frames": 124, "steps": 20, "sampler": "res_multistep", "seeds": [20260924, 20260925, 20260926]},
        "observation": "In sampled close-up frames, F+W and F+WB showed very similar face identity, eyes, nose, mouth, hairline, and pointed-ear stability; no obvious WB degradation or clear improvement was observed.",
        "status": "phase_4_complete_preliminary"
    },
    "anonymous_scoring_phase": {
        "status": "preliminary_manual_complete",
        "scoring_file": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t5_anonymous_scoring.json",
        "scope": "all completed T5 cells, anonymized before condition reveal",
        "summary": "No hard failures in the reviewed samples. WB sometimes improved subject occupancy/wardrobe readability in full-body shots, but close-up F+W and F+WB were effectively tied; dedicated Q/S/B and repeated W did not show stable gains in the restrained slow-turn setup.",
        "limitation": "Manual ordinal review by one reviewer; not a population-level statistical claim.",
        "next": "Move to difficult-action/occlusion validation or obtain a second reviewer before making WB a formal skill baseline."
    },
    "t6_difficult_action_phase": {
        "cells": {"T6-A": ["F_face_identity", "WB_wardrobe_body"], "T6-B": ["F_face_identity", "WB_wardrobe_body", "S_view_side"]},
        "results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t6_action_quality_cases.json.results.json",
        "runs": 6,
        "successful": 6,
        "conditions": {"resolution": "768x448", "frames": 124, "steps": 20, "sampler": "res_multistep", "seeds": [20260924, 20260925, 20260926]},
        "observation": "In the bow-drawing and self-occlusion action, adding S did not produce more stable action/endpoint behavior. Sampled B outputs were sometimes smaller in frame or had weaker composition than the F+WB baseline.",
        "interpretation": "This first difficult-action cell does not support adding a side reference by default; a harder occlusion or exact side-detail task may still justify a dedicated view image.",
        "status": "phase_5_complete_preliminary"
    },
    "t7_hidden_view_consistency_phase": {
        "status": "phase_1_seed_complete_preliminary",
        "invalid_first_batch": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t7_hidden_view_consistency_cases.json.results.json (first run; prompt leakage, exclude from scoring)",
        "corrected_cases": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t7_hidden_view_consistency_cases.json",
        "corrected_runs": 6,
        "successful": 6,
        "seed_scope": [20260924],
        "observation": "At the corrected seed, B0/B1 showed similar broad rear silhouette but different accessory visibility and framing; Q0 tended toward a side-like endpoint while Q1 also did not reliably preserve the intended 45-degree endpoint. This supports the hidden-detail divergence hypothesis but is not yet a multi-seed conclusion.",
        "s_consistency_extension": {
            "results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t7_s_consistency_cases_25_26.json.results.json",
            "runs": 4,
            "successful": 4,
            "observation": "Across the three corrected S seed pairs, no-S side endpoints varied substantially in crop and bow placement; with-S outputs more consistently approached a strict side silhouette and stabilized bow/body relation, but often reduced subject occupancy.",
            "status": "preliminary_signal"
        },
        "q_consistency_extension": {
            "results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t7_q_consistency_cases_25_26.json.results.json",
            "runs": 4,
            "successful": 4,
            "observation": "Across three corrected Q seed pairs, no-Q endpoints varied from front/three-quarter to side-like views; with-Q outputs more consistently trended toward a side-facing silhouette, but did not reliably reproduce the approximately 45-degree target. Bow/wardrobe identity stayed broadly coherent while framing and occupancy shifted.",
            "status": "preliminary_signal"
        },
        "b_consistency_extension": {
            "results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/t7_b_consistency_cases_25_26.json.results.json",
            "runs": 4,
            "successful": 4,
            "observation": "Across three corrected B seed pairs, no-B outputs freely varied in quiver/arrows, hair tie/shape, accessory visibility, and crop; with-B outputs converged on the same broad rear costume configuration and accessory binding.",
            "status": "positive_preliminary_signal"
        },
        "cross_video_consistency_conclusion": "B shows the clearest evidence of improving hidden-view asset consistency; S shows a weaker side-structure/bow-binding signal with occupancy cost; Q mainly biases turn direction/side-facing silhouette and does not reliably lock a 45-degree endpoint.",
        "next": "Do not make Q mandatory; consider B conditional for shots where exact rear costume/accessory identity matters, and keep S conditional pending production framing priorities."
    },
    "wb_head_processing_phase": {
        "assets": ["WB_wardrobe_body (legacy rectangular crop)", "WB_face_erased", "WB_head_removed"],
        "smoke_results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/wb_variant_smoke_cases.json.results.json",
        "runs": 3,
        "successful": 3,
        "observation": "The two mask/inpaint-derived variants reduced the obvious face/head leakage of the legacy crop in the smoke comparison; head_removed is the cleanest separation, while face_erased preserves rear-head/ear/shoulder context.",
        "formal_results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/wb_variant_quality_cases.json.results.json",
        "formal_runs": 9,
        "formal_successful": 9,
        "observation_formal": "Both mask/inpaint-derived WB variants reduced redundant face information in the reference asset, but H3 still generated the face from F_face_identity as intended. The new variants often reduced subject occupancy; head_removed produced an occasional black-edge/composition artifact. No quality win over the legacy crop is established.",
        "candidate_preference": "WB_face_erased is the safer next candidate because it retains rear-head/ear/shoulder context; WB_head_removed remains experimental pending a cleaner mask/inpaint plate.",
        "status": "formal_complete_preliminary",
        "source_model": "built-in image generation edit; not yet a local ComfyUI mask-node production baseline",
        "next": "use neck_only vs face_erased findings to design the next WB asset; do not replace the skill default until local mask/inpaint is validated"
    },
    "wb_neck_anchor_phase": {
        "cells": ["WB_face_erased", "WB_neck_only"],
        "results": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/wb_neck_vs_head_quality_cases.json.results.json",
        "runs": 6,
        "successful": 6,
        "conditions": {"resolution": "768x448", "frames": 124, "steps": 20, "sampler": "res_multistep", "seeds": [20260924, 20260925, 20260926]},
        "asset_qc_correction": "WB_face_erased is not a valid production candidate: visual QC shows a front-facing body combined with a rear-facing head/rear hair silhouette, which conflicts with F_face_identity and with any separate rear-view reference.",
        "observation": "The prior face_erased-vs-neck_only comparison is engineering evidence only, not a fair semantic comparison, because face_erased has a front/rear viewpoint conflict. WB_neck_only remains the cleaner current candidate; a true front-head-silhouette face-erased plate must be remade before retesting.",
        "status": "formal_complete_preliminary",
        "scoring": ".pi/tasks/remote-c1c2bb3a-432b-4586-af9d-f6ffdde54196/wb_neck_focus_scoring.json",
        "score_observation": "Both variants passed the focused review with no hard failures; face_erased retained richer rear-head/hair context, while neck_only provided cleaner role separation. No clear quality winner in this action cell.",
        "next": "keep both as conditional candidates; do not replace the skill baseline without a static/close-up control and local mask/inpaint validation"
    },
    "owner": "Sean"
}
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(path)
