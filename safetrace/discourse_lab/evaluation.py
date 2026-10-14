"""Developer-authored search sanity set; NOT an independent or real-data benchmark."""
import json
from pathlib import Path
from pipeline import load_case, search_sources
TESTS = [
    ("42% near misses", "s3"),
    ("€1.9 million disbursed", "s2"),
    ("kerb ramps", "s6"),
    ("68% calmer pedestrian crossings", "s7"),
    ("60% faster travellers", "s8"),
    ("self-selected respondents", "s5"),
    ("raw counts sampling details", "s3"),
]

def evaluate():
    data = load_case()
    rows=[]
    for question, expected in TESTS:
        got=search_sources(data, question, limit=1)
        actual=got[0]['source_id'] if got else None
        rows.append({'query': question, 'expected': expected, 'top_1': actual, 'pass': expected==actual})
    return {'benchmark': 'developer-authored synthetic sanity set', 'samples': len(rows),
            'top_1_match_rate': round(sum(row['pass'] for row in rows)/len(rows), 3),
            'external_validation': False, 'rows': rows}

if __name__ == '__main__':
    report=evaluate()
    (Path(__file__).parent/'data'/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
