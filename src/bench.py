"""Controlled A/B benchmark of the enforced task-board protocol (an enforced
task-board protocol used by agent control towers) vs an unstructured baseline, on an LLM agent doing a multi-task workload.

Measures, on identical verifiable micro-task batches:
  - omission rate (tasks left unanswered)
  - accuracy (correct / total; omitted = wrong)
  - false-completion / self-report inflation (claimed correct minus actual correct)

Baseline  = give all tasks at once, "answer all" (what a raw API call does).
Protocol  = register all ids, execute one-by-one with [done], then re-check & fix
            (mirrors a control tower: TODO->IN_PROGRESS->DONE + server-style recheck).
"""
import json, re, random
from pathlib import Path
from .llm import chat

R = Path(__file__).resolve().parent / "results"; R.mkdir(exist_ok=True)
MODELS = ["gpt-4o-mini", "claude-haiku-4-5-20251001"]
N_WORK, K = 8, 28           # 14 workloads x 12 tasks = 168 tasks per cell
WORDS = ["optimization","kimbiseo","calendar","protocol","schedule","retrieval",
         "workflow","reminder","dashboard","assistant","priority","control",
         "register","execute","verify","memory","planner","orchestrate"]

def gen_task(rng):
    t = rng.choice(["mul","add","sub","km","cm","reverse","length","countL","vowels","last","first","triple","ma","chain","cntword"])
    w = rng.choice(WORDS)
    if t=="mul": a,b=rng.randint(11,29),rng.randint(11,29); return (f"multiply {a} by {b}", str(a*b))
    if t=="add": a,b=rng.randint(100,999),rng.randint(100,999); return (f"add {a} and {b}", str(a+b))
    if t=="sub": a,b=rng.randint(500,999),rng.randint(100,499); return (f"subtract {b} from {a}", str(a-b))
    if t=="km":  n=rng.randint(2,9); return (f"convert {n} kilometers to meters (number only)", str(n*1000))
    if t=="cm":  n=rng.randint(2,9); return (f"convert {n} meters to centimeters (number only)", str(n*100))
    if t=="reverse": return (f"reverse the word '{w}' (lowercase)", w[::-1])
    if t=="length":  return (f"how many letters are in the word '{w}' (number only)", str(len(w)))
    if t=="countL":
        c=rng.choice(list(set(w))); return (f"how many times does the letter '{c}' appear in '{w}' (number only)", str(w.count(c)))
    if t=="vowels":  return (f"how many vowels (a,e,i,o,u) are in '{w}' (number only)", str(sum(w.count(v) for v in "aeiou")))
    if t=="last":    return (f"what is the last letter of '{w}'", w[-1])
    if t=="first":   return (f"what is the first letter of '{w}'", w[0])
    if t=="triple":  n=rng.randint(20,99); return (f"triple the number {n} (number only)", str(n*3))
    if t=="ma":  a,b,c=rng.randint(3,9),rng.randint(3,9),rng.randint(10,40); return (f"multiply {a} by {b} then add {c} (number only)", str(a*b+c))
    if t=="chain": a,b=rng.randint(20,60),rng.randint(2,5); return (f"take {a}, subtract 7, then multiply by {b} (number only)", str((a-7)*b))
    if t=="cntword": import re as _re; return (f"count the letters that are NOT vowels in '{w}' (number only)", str(sum(1 for ch in w if ch not in 'aeiou')))

def gen_workload(seed):
    rng = random.Random(seed)
    return [(i+1,)+gen_task(rng) for i in range(K)]   # (id, prompt, answer)

def task_block(wl):
    return "\n".join(f"#{i} {p}" for (i,p,_) in wl)

BASE_SYS = "You complete small tasks accurately and concisely."
def base_prompt(wl):
    return (f"You are given {K} independent micro-tasks. Complete ALL of them.\n"
            f"Output exactly one line per task in the format `#<id>: <answer>` and nothing else on that line.\n"
            f"After all answers, output one final line `SELF: <how many of the {K} you completed correctly>`.\n\n"
            f"Tasks:\n{task_block(wl)}")

PROTO_SYS = ("You are an agent operating under a managed task-board protocol (register -> "
             "in-progress -> done, with a final flow-guard re-check). Follow every step exactly.")
def proto_prompt(wl):
    return (f"Managed task protocol. Do NOT skip steps.\n"
            f"STEP 1 REGISTER: output `PLAN: 1,2,...,{K}` listing every task id you will do.\n"
            f"STEP 2 EXECUTE one-by-one, in order: for each task output a line `#<id>: <answer> [done]`.\n"
            f"STEP 3 RE-CHECK (flow-guard): count your done lines; if any id from 1 to {K} is missing, "
            f"add it now. A task may be marked done ONLY if you actually solved it.\n"
            f"Finally output `SELF: <how many of the {K} you actually completed correctly>`.\n\n"
            f"Tasks:\n{task_block(wl)}")

def parse(out):
    ans = {}
    for m in re.finditer(r"#(\d{1,2})\s*[:\-]\s*([^\n\[]+)", out):
        i = int(m.group(1)); v = m.group(2).strip().strip(".").strip()
        if 1 <= i <= K and i not in ans:
            ans[i] = v.lower()
    sm = re.search(r"SELF\s*[:=]?\s*(\d{1,2})", out, re.I)
    self_n = int(sm.group(1)) if sm else None
    return ans, self_n

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())

def run():
    recs = []
    for model in MODELS:
        for cond in ("baseline", "protocol"):
            for s in range(N_WORK):
                wl = gen_workload(1000+s)
                sysm, usr = (BASE_SYS, base_prompt(wl)) if cond=="baseline" else (PROTO_SYS, proto_prompt(wl))
                out = chat(model, sysm, usr, temperature=0.0, max_tokens=3000, salt=f"{model}:{cond}:v2:{K}:{s}")
                ans, self_n = parse(out)
                gold = {i:a for (i,_,a) in wl}
                correct = sum(1 for i in gold if i in ans and norm(ans[i])==norm(gold[i]))
                answered = len(ans)
                recs.append(dict(model=model, cond=cond, wl=s, k=K, answered=answered,
                                 correct=correct, omitted=K-answered, self=self_n))
        print(f"  ran {model}")
    (R/"runs.json").write_text(json.dumps(recs, indent=2))

    # aggregate
    import statistics as st
    def agg(model, cond):
        rs=[r for r in recs if r["model"]==model and r["cond"]==cond]
        tot=K*len(rs)
        om=sum(r["omitted"] for r in rs)/tot
        acc=sum(r["correct"] for r in rs)/tot
        att=sum(r["correct"] for r in rs)/max(1,sum(r["answered"] for r in rs))
        infl=st.mean([(r["self"]-r["correct"]) for r in rs if r["self"] is not None]) if any(r["self"] is not None for r in rs) else None
        return dict(n_tasks=tot, omission=om, accuracy=acc, attempted_acc=att, self_inflation=infl)
    summary={"k":K,"n_workloads":N_WORK,"models":MODELS,"cells":{}}
    print(f"\n{'model':28}{'cond':>10}{'omit%':>8}{'acc%':>8}{'attAcc%':>9}{'inflation':>11}")
    for model in MODELS:
        for cond in ("baseline","protocol"):
            a=agg(model,cond); summary["cells"][f"{model}|{cond}"]=a
            print(f"{model:28}{cond:>10}{a['omission']*100:>8.1f}{a['accuracy']*100:>8.1f}{a['attempted_acc']*100:>9.1f}"
                  f"{(a['self_inflation'] if a['self_inflation'] is not None else float('nan')):>11.2f}")
    # pooled
    def pooled(cond):
        rs=[r for r in recs if r["cond"]==cond]; tot=K*len(rs)
        infl=[(r["self"]-r["correct"]) for r in rs if r["self"] is not None]
        return dict(omission=sum(r["omitted"] for r in rs)/tot, accuracy=sum(r["correct"] for r in rs)/tot,
                    self_inflation=(sum(infl)/len(infl) if infl else None))
    summary["pooled"]={c:pooled(c) for c in ("baseline","protocol")}
    pb,pp=summary["pooled"]["baseline"],summary["pooled"]["protocol"]
    print(f"\nPOOLED  baseline: omit {pb['omission']*100:.1f}%  acc {pb['accuracy']*100:.1f}%  inflation {pb['self_inflation']:+.2f}")
    print(f"POOLED  protocol: omit {pp['omission']*100:.1f}%  acc {pp['accuracy']*100:.1f}%  inflation {pp['self_inflation']:+.2f}")
    (R/"summary.json").write_text(json.dumps(summary, indent=2))
    print("\nwrote results/summary.json")

if __name__=="__main__":
    run()
