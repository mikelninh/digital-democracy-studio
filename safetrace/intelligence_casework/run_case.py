from __future__ import annotations
import argparse, json
from pathlib import Path
from safetrace.intelligence_casework.engine import investigate, render_markdown, validate_input

ROOT=Path(__file__).resolve().parent
INPUT=ROOT/"data"/"investigation_input_v001.json"
OUT_JSON=ROOT/"results"/"v001_result.json"
OUT_MD=ROOT/"RESULTS_V001.md"

def build(path=INPUT):
    data=json.loads(path.read_text(encoding="utf-8"))
    errors=validate_input(data)
    if errors: raise ValueError("\n".join(errors))
    result=investigate(data)
    return json.dumps(result,indent=2,sort_keys=True)+"\n", render_markdown(result)

def main():
    p=argparse.ArgumentParser(description="Run SafeTrace intelligence casework end to end.")
    p.add_argument("--input",type=Path,default=INPUT)
    m=p.add_mutually_exclusive_group(); m.add_argument("--write",action="store_true"); m.add_argument("--check",action="store_true")
    a=p.parse_args(); js,md=build(a.input)
    if a.check:
        stale=[str(path) for path,text in ((OUT_JSON,js),(OUT_MD,md)) if not path.exists() or path.read_text(encoding="utf-8")!=text]
        if stale:
            print("FAIL: stale generated investigation outputs"); [print("-",x) for x in stale]; return 1
        print("PASS: committed investigation results match a fresh end-to-end run")
    else:
        OUT_JSON.parent.mkdir(parents=True,exist_ok=True); OUT_JSON.write_text(js,encoding="utf-8"); OUT_MD.write_text(md,encoding="utf-8")
        print("PASS: investigation executed")
    r=json.loads(js); ex=r["executive_result"]
    print("  decision:",ex["decision"]); print("  confirmed sanctions match:",ex["confirmed_sanctions_match"])
    print("  material findings:",ex["material_findings"]); print("  open actions:",ex["open_actions"])
    return 0

if __name__=="__main__": raise SystemExit(main())
