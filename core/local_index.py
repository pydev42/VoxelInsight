"""Enhanced local indexer for VoxelInsight edge mode with better DICOM/NIfTI support."""
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

try:
    import pydicom
    from pydicom.errors import InvalidDicomError
except Exception:
    pydicom = None
    InvalidDicomError = Exception

try:
    import nibabel as nib
except Exception:
    nib = None

try:
    import numpy as np
except Exception:
    np = None


INDEX_VERSION = 2


def collect_files(data_dir: Path) -> List[Path]:
    exts = {'.dcm', '.dicom', '.nii', '.nii.gz'}
    files = []
    for root, dirs, filenames in os.walk(data_dir):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fn in filenames:
            if fn.startswith('.'):
                continue
            lower = fn.lower()
            if lower.endswith('.nii.gz') or lower.endswith('.dcm') or lower.endswith('.dicom') or lower.endswith('.nii'):
                files.append(Path(root) / fn)
    return files


def index_dicom(path: Path) -> Dict[str, Any]:
    meta = {
        'type': 'dicom',
        'path': str(path.resolve()),
        'filename': path.name,
        'series_description': None,
        'study_description': None,
        'modality': None,
        'body_part': None,
        'patient_id': None,
        'series_instance_uid': None,
        'study_instance_uid': None,
    }
    if pydicom is None:
        return meta
    try:
        ds = pydicom.dcmread(str(path), stop_before_pixels=True, force=True)
        meta['modality'] = getattr(ds, 'Modality', None)
        meta['series_description'] = getattr(ds, 'SeriesDescription', None)
        meta['study_description'] = getattr(ds, 'StudyDescription', None)
        meta['body_part'] = getattr(ds, 'BodyPartExamined', None)
        meta['patient_id'] = getattr(ds, 'PatientID', None)
        meta['series_instance_uid'] = getattr(ds, 'SeriesInstanceUID', None)
        meta['study_instance_uid'] = getattr(ds, 'StudyInstanceUID', None)
        try:
            meta['patient_name'] = str(getattr(ds, 'PatientName', '')) or None
        except Exception:
            pass
        try:
            meta['manufacturer'] = getattr(ds, 'Manufacturer', None)
        except Exception:
            pass
    except Exception as e:
        meta['error'] = str(e)
    return meta


def index_nifti(path: Path) -> Dict[str, Any]:
    meta = {
        'type': 'nifti',
        'path': str(path.resolve()),
        'filename': path.name,
    }
    if nib is None:
        return meta
    try:
        img = nib.load(str(path))
        shape = img.shape
        meta['shape'] = list(shape)
        hdr = img.header
        try:
            meta['voxel_size'] = [float(x) for x in hdr.get_zooms()]
        except Exception:
            pass
        try:
            meta['affine'] = img.affine.tolist()
        except Exception:
            pass
    except Exception as e:
        meta['error'] = str(e)
    return meta


def build_index(data_dir: Path, out_path: Path) -> Dict[str, Any]:
    files = collect_files(data_dir)
    entries = []
    for f in files:
        lower = f.name.lower()
        if lower.endswith('.dcm') or lower.endswith('.dicom'):
            entries.append(index_dicom(f))
        elif lower.endswith('.nii') or lower.endswith('.nii.gz'):
            entries.append(index_nifti(f))
        else:
            entries.append({'type': 'unknown', 'path': str(f.resolve()), 'filename': f.name})
    index_data = {
        'version': INDEX_VERSION,
        'data_dir': str(data_dir.resolve()),
        'count': len(entries),
        'entries': entries,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as fh:
        json.dump(index_data, fh, indent=2)
    return index_data


def search_local(query: str, index_path: Path, limit: int = 50) -> List[Dict[str, Any]]:
    if not index_path.exists():
        return []
    try:
        with index_path.open('r', encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception:
        return []
    q = str(query).lower()
    results = []
    for entry in data.get('entries', []):
        score = 0
        for key in ['filename', 'series_description', 'study_description', 'modality', 'body_part', 'patient_id', 'patient_name', 'manufacturer']:
            val = entry.get(key)
            if val and q in str(val).lower():
                score += 2
        if q in str(entry.get('path', '')).lower():
            score += 1
        if score > 0:
            results.append({**entry, '_score': score})
    results.sort(key=lambda x: x.get('_score', 0), reverse=True)
    return results[:limit]


def main():
    parser = argparse.ArgumentParser(description='Build local index for VoxelInsight edge mode')
    parser.add_argument('--data', default=os.getenv('LOCAL_DATA_DIR', './data'), help='Directory containing DICOM/NIfTI files')
    parser.add_argument('--out', default=os.getenv('LOCAL_INDEX_PATH', './.voxelinsight_local_index'), help='Output index JSON path')
    parser.add_argument('--search', help='Test search after indexing')
    parser.add_argument('--limit', type=int, default=20)
    args = parser.parse_args()

    data_dir = Path(args.data)
    out_path = Path(args.out)
    if not data_dir.exists():
        print(f'Warning: data dir {data_dir} does not exist. Creating it.')
        data_dir.mkdir(parents=True, exist_ok=True)

    print(f'Indexing {data_dir} -> {out_path}')
    idx = build_index(data_dir, out_path)
    print(f'Indexed {idx["count"]} files')

    if args.search:
        res = search_local(args.search, out_path, limit=args.limit)
        print(json.dumps(res, indent=2))


if __name__ == '__main__':
    main()
