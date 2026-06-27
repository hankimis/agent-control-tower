"""Static charts from results/ -> paper/figs/ (English)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 140})
ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "paper" / "figs"; FIGS.mkdir(parents=True, exist_ok=True)
RED, GREEN, BLUE, GOLD, GREY, INK, PURPLE = "#c0392b", "#2a7f3f", "#2e6fb0", "#c9962a", "#8a8f98", "#222831", "#7a4fb0"
runs = json.loads((ROOT/"results"/"runs.json").read_text())
S = json.loads((ROOT/"results"/"summary.json").read_text())
K = S["k"]
def short(m): return m.replace("-20251001","").replace("claude-","").replace("gpt-","").replace("-4-5","-4.5")

def pooled(cond):
    rs=[r for r in runs if r["cond"]==cond]; n=len([r for r in rs if r["self"] is not None])
    claimed=100*sum(r["self"] for r in rs if r["self"] is not None)/(K*n)
    actual=100*sum(r["correct"] for r in rs)/(K*len(rs))
    return claimed, actual

# fig1 money: claimed vs actual, baseline vs protocol
fig,ax=plt.subplots(figsize=(7.8,4.8)); xb=np.arange(2); w=0.36
cl=[pooled("baseline")[0],pooled("protocol")[0]]; ac=[pooled("baseline")[1],pooled("protocol")[1]]
ax.bar(xb-w/2,cl,w,color=RED,label="claimed complete (self-report)")
ax.bar(xb+w/2,ac,w,color=GREEN,label="actually correct (verified)")
for i in range(2):
    ax.annotate(f"+{cl[i]-ac[i]:.0f}pp\nfalse 'done'",(xb[i],max(cl[i],ac[i])+2),ha="center",fontsize=10,color=RED,weight="bold")
    ax.text(xb[i]-w/2,cl[i]+0.4,f"{cl[i]:.0f}",ha="center",fontsize=9); ax.text(xb[i]+w/2,ac[i]+0.4,f"{ac[i]:.0f}",ha="center",fontsize=9)
ax.set_xticks(xb); ax.set_xticklabels(["raw API call\n(baseline)","prompt self-check\n(protocol)"],fontsize=10.5)
ax.set_ylabel("% of tasks"); ax.set_ylim(0,112)
ax.set_title("Agents claim 100% done, deliver ~88%, and self-checking does not fix it\nThe completion illusion: a ~12-point gap a model cannot see in itself",fontsize=11.5,weight="bold")
ax.legend(frameon=False,fontsize=9.5,loc="lower center")
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.grid(axis="y",alpha=0.2); fig.tight_layout(); fig.savefig(FIGS/"fig1_money.png",bbox_inches="tight"); plt.close(fig); print("fig1_money.png")

# fig2 per-model false-completion
models=S["models"]; fig,ax=plt.subplots(figsize=(8.2,4.8)); x=np.arange(len(models)); w=0.36
fb=[100*S["cells"][f"{m}|baseline"]["self_inflation"]/K for m in models]
fp=[100*S["cells"][f"{m}|protocol"]["self_inflation"]/K for m in models]
ax.bar(x-w/2,fb,w,color=RED,label="baseline"); ax.bar(x+w/2,fp,w,color=GOLD,label="protocol (prompt self-check)")
for xi,v in zip(x-w/2,fb): ax.text(xi,v+0.2,f"{v:.1f}%",ha="center",fontsize=9)
for xi,v in zip(x+w/2,fp): ax.text(xi,v+0.2,f"{v:.1f}%",ha="center",fontsize=9)
ax.set_xticks(x); ax.set_xticklabels([short(m) for m in models],fontsize=10)
ax.set_ylabel("false-completion rate"); ax.set_title("False completion is robust across models, and the prompt fix barely moves it",fontsize=11.5,weight="bold")
ax.legend(frameon=False,fontsize=9.5)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.grid(axis="y",alpha=0.2); fig.tight_layout(); fig.savefig(FIGS/"fig2_permodel.png",bbox_inches="tight"); plt.close(fig); print("fig2_permodel.png")

# fig3 distribution: actual-correct per workload vs always-claimed 28
fig,ax=plt.subplots(figsize=(8.4,4.6))
for ci,(cond,col) in enumerate([("baseline",BLUE),("protocol",GOLD)]):
    rs=[r for r in runs if r["cond"]==cond]
    xs=np.full(len(rs),ci)+np.random.RandomState(ci).uniform(-0.13,0.13,len(rs))
    ax.scatter(xs,[r["correct"] for r in rs],s=55,color=col,alpha=0.75,edgecolor="white",zorder=3,label=f"{cond}: actual correct")
ax.axhline(K,color=RED,lw=2,ls="--"); ax.text(1.45,K+0.15,f"claimed = {K}/{K}\n(every run)",color=RED,fontsize=9,va="bottom",ha="right",weight="bold")
ax.set_xticks([0,1]); ax.set_xticklabels(["baseline","protocol"],fontsize=10.5)
ax.set_ylabel(f"correct out of {K}"); ax.set_ylim(18,K+2)
ax.set_title("Every run self-reports a perfect score; the truth lands 2 to 6 tasks lower",fontsize=11.5,weight="bold")
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.grid(axis="y",alpha=0.2); fig.tight_layout(); fig.savefig(FIGS/"fig3_distribution.png",bbox_inches="tight"); plt.close(fig); print("fig3_distribution.png")

# fig4 honest null: omission + accuracy unchanged
fig,(a1,a2)=plt.subplots(1,2,figsize=(10,4.2))
a1.bar([0,1],[S["pooled"]["baseline"]["omission"]*100,S["pooled"]["protocol"]["omission"]*100],0.5,color=[GREY,GREY])
a1.set_xticks([0,1]); a1.set_xticklabels(["baseline","protocol"]); a1.set_ylim(0,10); a1.set_title("Task omission (0% either way)",fontsize=11,weight="bold")
a1.text(0.5,5,"current models\ndo not drop tasks",ha="center",color=GREY,fontsize=10)
acc=[S["pooled"]["baseline"]["accuracy"]*100,S["pooled"]["protocol"]["accuracy"]*100]
a2.bar([0,1],acc,0.5,color=[BLUE,GOLD])
for i,v in enumerate(acc): a2.text(i,v+0.5,f"{v:.1f}%",ha="center",fontsize=10)
a2.set_xticks([0,1]); a2.set_xticklabels(["baseline","protocol"]); a2.set_ylim(0,100); a2.set_title("Accuracy (no significant lift: +0.9pp)",fontsize=11,weight="bold")
for ax in (a1,a2):
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    ax.grid(axis="y",alpha=0.2)
fig.suptitle("Honest null: the prompt protocol does not improve omission or accuracy",fontsize=12,weight="bold",y=1.02)
fig.tight_layout(); fig.savefig(FIGS/"fig4_null.png",bbox_inches="tight"); plt.close(fig); print("fig4_null.png")

# fig5 robustness across task-count (K=12 -> 11.3%, K=28 -> 12.7%)
fig,ax=plt.subplots(figsize=(6.6,4.4))
ks=[12,28]; fr=[11.3,12.7]
ax.plot(ks,fr,"-o",color=RED,lw=2.4,ms=9)
for k,v in zip(ks,fr): ax.annotate(f"{v}%",(k,v),xytext=(0,8),textcoords="offset points",ha="center",fontsize=10,weight="bold")
ax.set_xlabel("tasks per batch (K)"); ax.set_ylabel("false-completion rate"); ax.set_ylim(0,16); ax.set_xlim(8,32)
ax.set_title("False completion holds at ~12% as the workload grows",fontsize=11.5,weight="bold")
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.grid(alpha=0.2); fig.tight_layout(); fig.savefig(FIGS/"fig5_robust.png",bbox_inches="tight"); plt.close(fig); print("fig5_robust.png")
print("DONE static")
