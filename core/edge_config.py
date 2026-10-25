#!/usr/bin/env python3
"""Edge/on-device mode for VoxelInsight."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

EDGE_MODE = os.getenv('EDGE_MODE', 'false').strip().lower() in {'1', 'true', 'yes', 'on'}
LOCAL_DATA_DIR = os.getenv('LOCAL_DATA_DIR', './data')
LOCAL_INDEX_PATH = os.getenv('LOCAL_INDEX_PATH', './.voxelinsight_local_index')


def is_edge_mode() -> bool:
    return EDGE_MODE


def get_local_data_dir() -> Path:
    p = Path(LOCAL_DATA_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_local_index_path() -> Path:
    return Path(LOCAL_INDEX_PATH)
