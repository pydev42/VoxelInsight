import os
import json
import tempfile
from pathlib import Path

from core.local_index import build_index, search_local, index_dicom, index_nifti, collect_files
from core.edge_config import is_edge_mode, get_local_data_dir, get_local_index_path


class TestEdgeConfig:
    def test_is_edge_mode_false_by_default(self):
        # Reset env
        old = os.environ.get('EDGE_MODE')
        os.environ.pop('EDGE_MODE', None)
        from importlib import reload
        import core.edge_config
        reload(core.edge_config)
        assert core.edge_config.is_edge_mode() == False
        if old is not None:
            os.environ['EDGE_MODE'] = old
    
    def test_is_edge_mode_true(self):
        old = os.environ.get('EDGE_MODE')
        os.environ['EDGE_MODE'] = 'true'
        from importlib import reload
        import core.edge_config
        reload(core.edge_config)
        assert core.edge_config.is_edge_mode() == True
        os.environ['EDGE_MODE'] = old if old is not None else os.environ.pop('EDGE_MODE')


class TestLocalIndex:
    def test_collect_files_empty_dir(self):
        with tempfile.TemporaryDirectory() as td:
            files = collect_files(Path(td))
            assert files == []
    
    def test_collect_files_finds_dicom(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / 'test.dcm').write_text('dummy')
            (p / 'test.nii.gz').write_text('dummy')
            (p / 'test.nii').write_text('dummy')
            (p / 'readme.txt').write_text('dummy')
            files = collect_files(p)
            names = [f.name for f in files]
            assert 'test.dcm' in names
            assert 'test.nii.gz' in names
            assert 'test.nii' in names
            assert 'readme.txt' not in names
    
    def test_build_index_empty(self):
        with tempfile.TemporaryDirectory() as td:
            data_dir = Path(td)
            out_path = Path(td) / 'index.json'
            idx = build_index(data_dir, out_path)
            assert idx['count'] == 0
            assert out_path.exists()
            with out_path.open() as f:
                data = json.load(f)
            assert data['count'] == 0
    
    def test_build_index_with_files(self):
        with tempfile.TemporaryDirectory() as td:
            data_dir = Path(td)
            (data_dir / 'scan1.dcm').write_text('dummy')
            (data_dir / 'scan2.nii.gz').write_text('dummy')
            out_path = Path(td) / 'index.json'
            idx = build_index(data_dir, out_path)
            assert idx['count'] == 2
            assert len(idx['entries']) == 2
    
    def test_search_local_no_index(self):
        with tempfile.TemporaryDirectory() as td:
            results = search_local('test', Path(td) / 'nope.json')
            assert results == []
    
    def test_search_local_finds_by_filename(self):
        with tempfile.TemporaryDirectory() as td:
            data_dir = Path(td)
            (data_dir / 'ct_brain.dcm').write_text('dummy')
            out_path = Path(td) / 'index.json'
            build_index(data_dir, out_path)
            results = search_local('brain', out_path)
            assert len(results) >= 1
            assert results[0]['filename'] == 'ct_brain.dcm'
    
    def test_search_local_case_insensitive(self):
        with tempfile.TemporaryDirectory() as td:
            data_dir = Path(td)
            (data_dir / 'CT_CHEST.dcm').write_text('dummy')
            out_path = Path(td) / 'index.json'
            build_index(data_dir, out_path)
            results = search_local('ct', out_path)
            assert len(results) >= 1
    
    def test_index_dicom_graceful_no_pydicom(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'test.dcm'
            p.write_text('dummy')
            meta = index_dicom(p)
            assert meta['type'] == 'dicom'
            assert meta['filename'] == 'test.dcm'
            assert 'path' in meta
    
    def test_index_nifti_graceful_no_nibabel(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'test.nii.gz'
            p.write_text('dummy')
            meta = index_nifti(p)
            assert meta['type'] == 'nifti'
            assert meta['filename'] == 'test.nii.gz'
            assert 'path' in meta
