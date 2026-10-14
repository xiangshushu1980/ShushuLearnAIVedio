# [Sean] Data-to-infographic matrix v1

Task `remote-97ccaaac-e730-4c57-875c-c86954ca0518`. Eight cases × three local models = 24 core images, plus Qwen official T2I Prompt Rewrite on (8) and corrected Krea prompting (8): 40 images total. One fixed seed per case/model (42), four Chinese and four English cases. `casebook.json` is ground truth. One sourced case uses World Bank WDI/IEA 2021 renewable electricity shares; seven are explicitly synthetic controlled data, not empirical claims.

Cases span ranked bars, line chart, 100% stacked bars, donut, flow diagram, before/after bars, and timeline markers, with varied art direction. Model-adapted prompts, workflows, run JSON, per-second GPU samples, image SHA-256, actual Qwen PE outputs and contact sheets are preserved here. The initial Krea condition inherited a negative prompt containing `text`, which conflicts with requested text rendering; it is retained as a configuration control. The corrected Krea arm quotes every target string and removes `text` from negative conditioning, following the official Krea prompting guidance.

Evaluation checks exact text, completeness, ordering, data-to-visual encoding, chart type, coherence, layout and legibility. Qwen PE visually preserved target values and category mappings in all eight cases. Krea still produced repeated values, label errors and stray text in the corrected arm. One seed per cell is exploratory, not a model-wide estimate. See `runs/manifest.json`, `contact_*.jpg`, and `contact_krea2_optimized.jpg`.

Research basis: [IGenBench](https://arxiv.org/abs/2601.04498), [STRICT](https://aclanthology.org/2025.emnlp-main.1070/), [T2I-CompBench++](https://arxiv.org/abs/2307.06350).
