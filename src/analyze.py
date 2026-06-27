"""Aggregate results/runs.json -> results/summary.json (final), handling parse gaps.
Capability-tiered false completion, per-task-type accuracy, clean-parse protocol comparison."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
K = 28
ORDER = ["gpt-4o-mini", "gpt-4o", "claude-haiku-4-5-20251001", "claude-sonnet-4-6"]
TIER = {"gpt-4o-mini": "small", "claude-haiku-4-5-20251001": "small", "gpt-4o": "frontier", "claude-sonnet-4-6": "frontier"}
NICE = {"mul":"multiply","add":"add","sub":"subtract","km":"km to m","cm":"m to cm","reverse":"reverse word",
        "length":"word length","countL":"count a letter","vowels":"count vowels","last":"last letter",
        "first":"first letter","triple":"triple","ma":"multiply then add","chain":"three-step chain","cntword":"count consonants"}

def main():
    runs = json.loads((ROOT/"results"/"runs.json").read_text())
    def cell(m, c): return [r for r in runs if r["model"]==m and r["cond"]==c]
    def fc(rs):  # false completion %, using only runs with a parsed self-report
        v=[(r["self"]-r["correct"]) for r in rs if r["self"] is not None]
        return round(100*sum(v)/(K*len(v)), 1) if v else None
    def acc(rs): return round(100*sum(r["correct"] for r in rs)/(K*len(rs)), 1)
    def omit(rs): return round(100*sum(r["omitted"] for r in rs)/(K*len(rs)), 1)

    S = {"k": K, "models": ORDER, "tier": TIER, "per_model": {}, "per_type": {}, "nice": NICE}
    for m in ORDER:
        S["per_model"][m] = {c: {"acc": acc(cell(m,c)), "false_completion": fc(cell(m,c)), "omission": omit(cell(m,c))}
                             for c in ("baseline","protocol")}
    # tier pools (baseline)
    for tier in ("small","frontier"):
        rs=[r for r in runs if r["cond"]=="baseline" and TIER[r["model"]]==tier]
        S[f"{tier}_baseline_false"]=fc(rs); S[f"{tier}_baseline_acc"]=acc(rs)
    rs=[r for r in runs if r["cond"]=="baseline"]
    S["pooled_baseline_false"]=fc(rs); S["pooled_baseline_acc"]=acc(rs)
    # per-task-type accuracy (baseline pooled)
    pt=defaultdict(lambda:[0,0])
    for r in runs:
        if r["cond"]!="baseline": continue
        for t in r["pertask"]: pt[t["type"]][0]+=t["correct"]; pt[t["type"]][1]+=1
    S["per_type"]={t:{"acc":round(100*c/n,1),"n":n} for t,(c,n) in pt.items()}
    (ROOT/"results"/"summary.json").write_text(json.dumps(S, ensure_ascii=False, indent=2))

    sh=lambda m:m.replace("-20251001","").replace("claude-","").replace("gpt-","")
    print("=== baseline false-completion (capability tier) ===")
    for m in ORDER:
        b=S["per_model"][m]["baseline"]; print(f"{sh(m):14} ({TIER[m]:8}) actual {b['acc']:5.1f}%  false {b['false_completion']:+5.1f}%")
    print(f"\nsmall-model pool: false {S['small_baseline_false']:+.1f}%   frontier pool: false {S['frontier_baseline_false']:+.1f}%   all: {S['pooled_baseline_false']:+.1f}%")
    print("\n=== protocol does not fix it (clean-parse models) ===")
    for m in ORDER:
        b=S["per_model"][m]["baseline"]["false_completion"]; p=S["per_model"][m]["protocol"]["false_completion"]
        note=" [gpt-4o drifts format under protocol; excluded]" if m=="gpt-4o" else ""
        print(f"{sh(m):14} baseline {b:+.1f}%  protocol {p:+.1f}%{note}")
    print("\n=== where the illusion lives: per-task-type accuracy (baseline) ===")
    for t in sorted(S["per_type"], key=lambda x:S["per_type"][x]["acc"]):
        print(f"{NICE.get(t,t):18} {S['per_type'][t]['acc']:5.1f}%")
    print("\nwrote results/summary.json")

if __name__=="__main__":
    main()
