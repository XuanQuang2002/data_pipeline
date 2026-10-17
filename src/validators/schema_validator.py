import pandas as pd

REQUIRED = {
    'customers':['customer_id','full_name','email','status'],
    'products':['product_id','category_id','product_name','unit_price','status'],
    'orders':['order_id','customer_id','order_date','status','order_total'],
    'order_items':['order_item_id','order_id','product_id','quantity','unit_price','discount_amount'],
    'payments':['payment_id','order_id','payment_date','payment_status','amount'],
}


def validate_schema(name, df):
    """Kiểm tra thiếu cột so với Data Contract."""
    missing = [c for c in REQUIRED[name] if c not in df.columns]

    if missing:
        raise ValueError(
            f"{name}: missing columns {missing}"
        )

    return True

def score_rows(name:str, df: pd.DataFrame):
    """Tính điểm chất lượng từng row (0-100%) và danh sách lỗi."""
    req_cols = REQUIRED[name]
    scored_rows = []
    for _, row in df.iterrows():
        errors = []
        valid_count = 0
        for col in req_cols:
            val = row.get(col)
            if pd.isna(val) or (isinstance(val,str) and val.strip()) == '':
                errors.append(f'MISSING_{col.upper()}')
            else:
                valid_count += 1
        score = int((valid_count/ len(req_cols)) * 100)
        pk_val = row.get(req_cols[0], 'UNKOWN')
        scored_rows.append((pk_val,score,errors))
    return scored_rows

# if __name__ == '__main__':
#     from pathlib import Path
#     file_path = Path('data/dirty/day_2026-07-02/customers_daily.csv')

#     if file_path.exists():
#         df = pd.read_csv(file_path)
#         validate_schema('customers', df)
#         scores = score_rows('customers', df)

#         output_lines = ["=== Schema Validation & Row Scoring Demo (customers) ==="]
#         for pk, score, errors in scores[:10]:
#             err_str = f"[{', '.join(errors)}]"
#             output_lines.append(f"row_id={pk} score={score:<3} errors={err_str}")

#         result = "/n".join(output_lines)
#         print(result)
#     else:
#         print(f"Khong tim thay file: {file_path}")