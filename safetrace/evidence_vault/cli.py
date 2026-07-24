from __future__ import annotations
import argparse, json
from pathlib import Path
from .bootstrap import build_bootstrap_report
from .registry import SourceRegistry
from .vault import EvidenceVault

def main()->int:
    p=argparse.ArgumentParser(description="SafeTrace v1.3 Evidence Vault")
    sub=p.add_subparsers(dest="command",required=True)
    b=sub.add_parser("bootstrap"); b.add_argument("--safetrace-root",type=Path,default=Path("safetrace")); b.add_argument("--registry-root",type=Path,default=Path("safetrace/evidence_vault/registry")); b.add_argument("--report",type=Path)
    v=sub.add_parser("verify"); v.add_argument("--registry",type=Path,required=True); v.add_argument("--vault",type=Path,required=True); v.add_argument("--output",type=Path)
    a=p.parse_args()
    if a.command=="bootstrap":
        report=build_bootstrap_report(a.safetrace_root,a.registry_root)
    else:
        report=EvidenceVault(a.vault,SourceRegistry.load(a.registry)).verify_integrity()
    encoded=json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    output=getattr(a,"report",None) or getattr(a,"output",None)
    if output:
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(encoded,encoding="utf-8")
    else:
        print(encoded,end="")
    return 0 if report["status"]=="pass" else 2
if __name__=="__main__":raise SystemExit(main())
