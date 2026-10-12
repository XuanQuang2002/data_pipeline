import pandas as pd
from src.transform import normalize


def test_normalize_raw_immutability():
    original = pd.DataFrame([{'CUSTOMER_ID ': 'C1', ' EMAIL ': ' TEST@ABC.COM '}])
    copy_df = original.copy()
    cleaned = normalize(original)
    # Dữ liệu RAW không bị thay đổi
    assert list(original.columns) == list(copy_df.columns)
    assert original.iloc[0]['CUSTOMER_ID '] == 'C1'
    # Bản cleaned được chuẩn hóa
    assert list(cleaned.columns) == ['customer_id', 'email']


def test_normalize_strings_and_enums():
    df = pd.DataFrame([{
        'customer_id': ' CUS101 ',
        'email': ' John.Doe@Example.COM ',
        'status': ' ACTIVE ',
        'channel': ' MOBILE_APP ',
    }])
    cleaned = normalize(df)
    assert cleaned.iloc[0]['customer_id'] == 'CUS101'
    assert cleaned.iloc[0]['email'] == 'john.doe@example.com'
    assert cleaned.iloc[0]['status'] == 'active'
    assert cleaned.iloc[0]['channel'] == 'mobile_app'


def test_normalize_numeric_and_datetime():
    df = pd.DataFrame([{
        'unit_price': '150.50',
        'quantity': '2',
        'order_date': '2026-07-01T14:30:00+07:00',
    }])
    cleaned = normalize(df)
    assert cleaned.iloc[0]['unit_price'] == 150.50
    assert cleaned.iloc[0]['quantity'] == 2
    assert pd.api.types.is_numeric_dtype(cleaned['unit_price'])
    assert pd.api.types.is_datetime64_any_dtype(cleaned['order_date'])