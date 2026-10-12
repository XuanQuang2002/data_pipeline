import tempfile
from pathlib import Path
import pandas as pd
import pytest
from src.extract_files import profile, read_dataset


def test_read_csv_success():
    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', encoding='utf-8', delete=False) as f:
        f.write('id,name,value\n1,Alpha,100\n2,Beta,200\n')
        f_path = Path(f.name)
    try:
        df = read_dataset(f_path)
        assert len(df) == 2
        assert list(df.columns) == ['id', 'name', 'value']
    finally:
        f_path.unlink()


def test_read_json_nested_data():
    with tempfile.NamedTemporaryFile(suffix='.json', mode='w', encoding='utf-8', delete=False) as f:
        f.write('{"data": [{"payment_id": "P01", "amount": 50.5}]}')
        f_path = Path(f.name)
    try:
        df = read_dataset(f_path)
        assert len(df) == 1
        assert df.iloc[0]['payment_id'] == 'P01'
    finally:
        f_path.unlink()


def test_read_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_dataset(Path('data/non_existent_file.csv'))


def test_unsupported_file_extension():
    with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', encoding='utf-8', delete=False) as f:
        f.write('dummy text')
        f_path = Path(f.name)
    try:
        with pytest.raises(ValueError, match='Unsupported file'):
            read_dataset(f_path)
    finally:
        f_path.unlink()


def test_profile_metrics():
    df = pd.DataFrame([
        {'id': 'A1', 'val': 10},
        {'id': 'A1', 'val': 10},
        {'id': 'A2', 'val': None},
    ])
    rep = profile(df)
    assert rep['rows'] == 3
    assert rep['columns'] == ['id', 'val']
    assert rep['missing'] == {'id': 0, 'val': 1}
    assert rep['duplicates'] == 1