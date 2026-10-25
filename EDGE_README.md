# VoxelInsight Edge (On-Device)

This is an edge/on-device variant of VoxelInsight. Run fully offline with a local LLM (Ollama) and local DICOM/NIfTI files.

## Quick start

1. Install dependencies
```bash
python -m pip install -U pip
pip install -r requirements.txt
```

2. Setup environment
```bash
cp .env.example .env
# Edit .env: set LLM_PROVIDER=ollama, OLLAMA_MODEL=qwen2.5:7b-instruct
```

3. Start Ollama and pull a model
```bash
ollama serve
ollama pull qwen2.5:7b-instruct
```

4. Add local scans
```bash
mkdir -p data
# Put .dcm, .nii, .nii.gz files in ./data
```

5. Run in edge mode
```bash
./scripts/run_edge.sh
# or: EDGE_MODE=true chainlit run app.py
```

## Features
- Local LLM via Ollama (OpenAI-compatible)
- Local indexing of DICOM/NIfTI files
- `search_local_images` tool for querying local scans
- Auth/OAuth disabled in edge mode
- Works offline (no MIDRC/IDC/TCIA required)

## Notes
- For best tool use, use a model with function/tool calling support (e.g., qwen2.5:7b-instruct, llama-3.1-8b).
- Large imaging models (TotalSegmentator/MONAI) may need GPU and significant disk/RAM.
- If running headless, ensure dependencies are installed.
