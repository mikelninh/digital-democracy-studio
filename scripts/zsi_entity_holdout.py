from __future__ import annotations
import json
from pathlib import Path
from zsi_entity_benchmark_v11 import predict

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT = ROOT / 'zero-suffering-intelligence' / 'entity-resolution' / 'holdout-v1.json'
OUT = ROOT / 'zero-suffering-intelligence' / 'entity-resolution' / 'results-holdout-v1.json'


def main():
    data = json.loads(HOLDOUT.read_text(encoding='utf-8'))
    rows = []
    tp = fp = fn = tn = 0
    for case in data['cases']:
        predicted, reason = predict(case['record_a'], case['record_b'])
        expected = case['ground_truth']
        correct = predicted == expected
        if expected == 'merge' and predicted == 'merge': tp += 1
        elif expected == 'separate' and predicted == 'merge': fp += 1
        elif expected == 'merge' and predicted == 'separate': fn += 1
        else: tn += 1
        rows.append({
            'case_id': case['case_id'], 'expected': expected, 'predicted': predicted,
            'correct': correct, 'reason': reason,
            'record_a': case['record_a']['name'], 'record_b': case['record_b']['name'],
            'ground_truth_reason': case['ground_truth_reason']
        })
    precision = tp/(tp+fp) if tp+fp else 0.0
    recall = tp/(tp+fn) if tp+fn else 0.0
    f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.0
    result = {
        'schema': 'zsi.entity-resolution/holdout-results-1.0',
        'holdout': 'holdout-v1.json',
        'resolver': 'zsi_entity_benchmark_v11.predict — unchanged after holdout freeze',
        'cases': len(rows),
        'metrics': {
            'true_positives': tp, 'false_positives': fp, 'false_negatives': fn, 'true_negatives': tn,
            'precision': round(precision,4), 'recall': round(recall,4), 'f1': round(f1,4),
            'accuracy': round((tp+tn)/len(rows),4)
        },
        'errors': [r for r in rows if not r['correct']],
        'results': rows,
        'guardrail': 'This is the first evaluation on frozen holdout-v1. Do not tune and re-report against this same holdout as if it remained unseen. Any resolver repair after inspecting these errors requires a fresh holdout-v2 for the next unbiased score.'
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result['metrics'], indent=2))

if __name__ == '__main__': main()
