#!/usr/bin/env python3
"""End-to-end demo script for VoxelInsight edge/on-device mode."""
import os
import json
import sys
import time
from pathlib import Path

# Set up edge mode
os.environ['EDGE_MODE'] = 'true'
os.environ['LLM_PROVIDER'] = os.environ.get('LLM_PROVIDER', 'ollama')
os.environ['LOCAL_DATA_DIR'] = os.environ.get('LOCAL_DATA_DIR', './data')
os.environ['LOCAL_INDEX_PATH'] = os.environ.get('LOCAL_INDEX_PATH', './.voxelinsight_local_index')

from core.local_index import build_index, search_local
from core.edge_config import get_local_data_dir, get_local_index_path, is_edge_mode


def demo():
    print("=" * 60)
    print("VoxelInsight Edge/On-Device Demo")
    print("=" * 60)
    print()
    
    print(f"Edge mode: {is_edge_mode()}")
    data_dir = get_local_data_dir()
    idx_path = get_local_index_path()
    print(f"Data dir: {data_dir}")
    print(f"Index path: {idx_path}")
    print()
    
    # Create sample data if none exists
    if not any(data_dir.iterdir()):
        print("No data files found. Creating sample structure...")
        (data_dir / "sample").mkdir(exist_ok=True)
        print(f"Created {data_dir / 'sample'}. Add .dcm or .nii.gz files here.")
        print()
    
    # Index
    print("Building local index...")
    try:
        idx = build_index(data_dir, idx_path)
        print(f"✓ Indexed {idx['count']} files")
    except Exception as e:
        print(f"✗ Error indexing: {e}")
        return
    print()
    
    # Search demo
    print("Testing search...")
    for query in ["ct", "mri", "brain", "chest"]:
        results = search_local(query, idx_path, limit=5)
        print(f"  Search '{query}': {len(results)} results")
    print()
    
    # Show index summary
    print("Index summary:")
    try:
        with idx_path.open() as f:
            data = json.load(f)
        types = {}
        modalities = {}
        for entry in data['entries']:
            t = entry.get('type', 'unknown')
            types[t] = types.get(t, 0) + 1
            m = entry.get('modality')
            if m:
                modalities[m] = modalities.get(m, 0) + 1
        print(f"  Types: {types}")
        print(f"  Modalities: {modalities}")
    except Exception as e:
        print(f"  Error: {e}")
    print()
    
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Add your DICOM/NIfTI files to ./data/")
    print("2. Run: python core/local_index.py")
    print("3. Start Ollama: ollama serve && ollama pull qwen2.5:7b-instruct")
    print("4. Run edge mode: ./scripts/run_edge.sh")
    print()


if __name__ == '__main__':
    demo()
