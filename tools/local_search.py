"""Enhanced local search tool for VoxelInsight edge mode."""
import json
from typing import Dict, Any, List

from langchain_core.tools import tool

from core.local_index import search_local
from core.edge_config import get_local_index_path, is_edge_mode, get_local_data_dir


@tool
def search_local_images(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search for local DICOM/NIfTI files in the local index (edge mode)."""
    if not is_edge_mode():
        return {"status": "disabled", "message": "Only available in EDGE_MODE=true"}
    idx = get_local_index_path()
    results = search_local(query, idx, limit=limit)
    return {"status": "ok", "count": len(results), "results": results, "index_path": str(idx)}


@tool
def list_local_images(modality: str = "", limit: int = 100) -> Dict[str, Any]:
    """List local images, optionally filtered by modality."""
    if not is_edge_mode():
        return {"status": "disabled", "message": "Only available in EDGE_MODE=true"}
    idx = get_local_index_path()
    if not idx.exists():
        return {"status": "ok", "count": 0, "results": [], "message": "No index found. Run scripts/index_local.sh or core/local_index.py"}
    try:
        with idx.open('r', encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception as e:
        return {"status": "error", "message": str(e)}
    results = []
    for entry in data.get('entries', []):
        if modality:
            m = (entry.get('modality') or '').upper()
            if m != modality.upper():
                continue
        results.append(entry)
    return {"status": "ok", "count": len(results[:limit]), "results": results[:limit], "data_dir": str(get_local_data_dir())}


@tool
def reindex_local() -> Dict[str, Any]:
    """Rebuild the local index from LOCAL_DATA_DIR."""
    if not is_edge_mode():
        return {"status": "disabled", "message": "Only available in EDGE_MODE=true"}
    try:
        from core.local_index import build_index
        data_dir = get_local_data_dir()
        idx_path = get_local_index_path()
        data = build_index(data_dir, idx_path)
        return {"status": "ok", "count": data.get('count', 0), "index_path": str(idx_path)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
