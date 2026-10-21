from pathlib import Path
import json
import pandas as pd

def build_report(stats, run_id=None, out_dir=Path('reports')):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(stats)

    # Xuất file CSV báo cáo
    df.to_csv(out_dir / 'data_quality_report.csv', index=False)
    if run_id:
        df.to_csv(out_dir / f'data_quality_report_{run_id}.csv', index=False)

    # Invariant kiểm soát đối soát
    summary = {
        'run_id': run_id,
        'input': int(df['input'].sum()) if 'input' in df else 0,
        'valid': int(df['valid'].sum()) if 'valid' in df else 0,
        'rejected': int(df['rejected'].sum()) if 'rejected' in df else 0,
        'reconciliation_ok': bool((df['input'] == df['valid'] + df['rejected']).all()),
    }
    (out_dir / 'data_quality_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return df