#!/usr/bin/env bash
# Index local data for VoxelInsight edge mode
set -e

cd "$(dirname "$0")/.."

DATA_DIR=${LOCAL_DATA_DIR:-./data}
INDEX_PATH=${LOCAL_INDEX_PATH:-./.voxelinsight_local_index}

mkdir -p "$DATA_DIR"
echo "Indexing $DATA_DIR -> $INDEX_PATH"
python core/local_index.py --data "$DATA_DIR" --out "$INDEX_PATH"
echo "Done."
