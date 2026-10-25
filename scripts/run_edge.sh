#!/usr/bin/env bash
# Run VoxelInsight in edge/on-device mode
set -e

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Edit it to set LLM_PROVIDER=ollama and OLLAMA_MODEL."
fi

# Check if ollama is running if using ollama
if grep -q "^LLM_PROVIDER=ollama" .env 2>/dev/null; then
  if ! curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "Warning: Ollama does not appear to be running at http://localhost:11434"
    echo "Start Ollama with: ollama serve"
  fi
fi

# Ensure data dir exists
mkdir -p ./data

# Build local index if it doesn't exist
if [ ! -f ./.voxelinsight_local_index ]; then
  echo "Building local index..."
  python core/local_index.py --data ./data --out ./.voxelinsight_local_index || true
fi

# Run in edge mode
export EDGE_MODE=true
echo "Starting VoxelInsight in EDGE mode..."
chainlit run app.py -w
