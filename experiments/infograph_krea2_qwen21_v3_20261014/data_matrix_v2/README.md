# [Sean] Data-to-infographic matrix v2

Task `remote-97ccaaac-e730-4c57-875c-c86954ca0518`. Adds 12 bilingual mixed-language cases and 36 planned images: one fixed seed (42) for each case on Qwen-Image-2.1 BF16 + official T2I Prompt Rewrite, Krea 2 RAW BF16, and FLUX.2-klein 9B BF16. Canvas 1536×1024.

The cases add chart forms absent from v1: a sourced line chart, dual-metric bars, heatmap, waterfall, dot distribution, population pyramid, dumbbell plot, treemap, small multiples, interval plot, conserved network flow, and scatter plot. There are six Chinese and six English cases. The World Bank electricity access time series is a sourced snapshot; the other 11 are explicitly synthetic controlled examples.

Prompts are tailored per model: Qwen receives a compact exact-data brief through its official PE node; Krea receives natural-language art direction with every data row quoted; FLUX receives a structured visual brief with exact strings quoted. Krea's negative prompt omits `text` so it does not contradict text rendering.

Reproduction: run `build_matrix.py`, then set `HIVE_RESOURCE_LEASE_ID` to an active `gpu:0` lease and run `run_matrix.py`. Each image has a model-specific input prompt, workflow, actual Qwen PE output where applicable, run JSON, GPU/RAM samples, and SHA-256. Raw World Bank response is in `sources/worldbank_electricity_access.json`. `runs/manifest.json` is the batch index.

Evaluation: compare exact strings and category/value mapping against `casebook.json`; check chart form, arithmetic/conservation, readability, visual hierarchy, and whether the art direction supports the data story. All non-World-Bank values are fictional test fixtures, not empirical claims.

Visual findings and one-row-per-case links to full resolution images and run records: [`evaluation.md`](evaluation.md). Contact sheets are included for quick side-by-side review.
