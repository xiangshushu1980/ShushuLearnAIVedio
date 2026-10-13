# [Sean] ComfyUI output archive index

Owner: Sean

The ComfyUI output snapshot from 2026-09-28 is archived outside the active ComfyUI roots and project workspace at:

`/home/sean/archive/comfyui-output/2026-09-28/`

This archive contains **480 files (424,562,793 bytes; about 405 MiB)**. At the time of the move, 490 files remained in `output`; 10 text records were migrated into experiment folders first. The earlier inventory had 564 files, so 74 files had already disappeared and were skipped without further recovery attempts. The output directory is now empty.

Legacy output paths resolve by replacing `/home/sean/projects/ComfyUI/output/` with the archive path above. This preserves the original subdirectory layout. Text manifests, prompts, and analysis records that were inside output have been migrated to the corresponding `experiments/` folders.

ComfyUI output is now a temporary generation destination. Completed experiment files and their records belong in `experiments/<task>/`; long-term binary archives stay outside both ComfyUI scan roots and this project tree.
