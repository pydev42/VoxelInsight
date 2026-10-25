"""Local search tool for VoxelInsight edge mode."""
from typing import Dict, Any

from langchain_core.tools import tool

from core.local_index import search_local
from core.edge_config import get_local_index_path, is_edge_mode


@tool
def search_local_images(query: str, limit: int = 20) -> Dict[str, Any]:
    """Search for local DICOM/NIfTI files in the local index (edge mode)."""
    if not is_edge_mode():
        return {"status": "disabled", "message": "Only available in EDGE_MODE=true"}
    idx = get_local_index_path()
    results = search_local(query, idx, limit=limit)
    return {"status": "ok", "count": len(results), "results": results}
