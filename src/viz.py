"""Static charts from results/summary.json -> paper/figs/ (English)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 140})
ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT/"paper"/"figs"; FIGS.mkdir(parents=True, exist_ok=True)
RED, GREEN, BLUE, GOLD, GREY, INK, PURPLE = "#c0392b","#2a7f3f","#2e6fb0","#c9962a","#8a8f98","#222831","#7a4fb0"
S = json.loads((ROOT/"results"/"summary.json").read_text())
ORDER = S["models"]; TIER = S["tier"]
sh = lambda m: m.replace("-20251001","").replace("claude-","").replace("gpt-","")
tcol = lambda m: RED if TIER[m]=="small" else GREEN

# fig1 money: per-model claimed (100) vs actual
fig,ax=plt.subplots(figsize=(8.6,4.8)); x=np.arange(len(ORDER)); w=0.36
actual=[S["per_model"][m]["baseline"]["acc"] for m in ORDER]
ax.bar(x-w/2,[100]*len(ORDER),w,color=RED,label="claimed done (self-report)")
ax.bar(x+w/2,actual,w,color=GREEN,label="actually correct (verified)")
for i,m in enumerate(ORDER):
    f=S["per_model"][m]["baseline"]["false_completion"]
    ax.annotate(f"{f:+.0f}pp",(x[i],102),ha="center",fontsize=9.5,color=(RED if f>3 else GREY),weight="bold")
    ax.text(x[i]+w/2,actual[i]+0.5,f"{actual[i]:.0f}",ha="center",fontsize=8.5)
ax.set_xticks(x); ax.set_xticklabels([f"{sh(m)}\n({TIER[m]})" for m in ORDER],fontsize=9.5)
ax.set_ylabel("% of tasks"); ax.set_ylim(0,116)
ax.set_title("Every model claims 100% done; small models deliver ~87%, frontier ~95%\nThe completion illusion is real and capability-tiered",fontsize=11.5,weight="bold")
ax.legend(frameon=False,fontsize=9.5,loc="lower right")
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.grid(axis="y",alpha=0.2); fig.tight_layout(); fig.savefig(FIGS/"fig1_money.png",bbox_inches="tight"); plt.close(fig); print("fig1_money.png")

# fig2 tier: false-completion by model, colored by tier
fig,ax=plt.subplots(figsize=(8,4.6)); x=np.arange(len(ORDER))
vals=[S["per_model"][m]["baseline"]["false_completion"] for m in ORDER]
ax.bar(x,vals,0.6,color=[tcol(m) for m in ORDER],edgecolor="white")
ax.axhline(0,color=INK,lw=1)
for xi,v in zip(x,vals): ax.text(xi,v+(0.3 if v>=0 else -0.8),f"{v:+.1f}%",ha="center",fontsize=10,weight="bold")
ax.set_xticks(x); ax.set_xticklabels([sh(m) for m in ORDER],fontsize=10)
ax.set_ylabel("false-completion rate")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=RED,label="small / cheap model"),Patch(color=GREEN,label="frontier model")],frameon=False,fontsize=9.5)
ax.set_title("False completion falls with capability: ~13% for small models, ~0-5% for frontier",fontsize=11.5,weight="bold")
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.grid(axis="y",alpha=0.2); fig.tight_layout(); fig.savefig(FIGS/"fig2_tier.png",bbox_inches="tight"); plt.close(fig); print("fig2_tier.png")

# fig3 per-task-type: where the illusion lives
pt=S["per_type"]; nice=S["nice"]
items=sorted(pt.items(), key=lambda kv:kv[1]["acc"])
fig,ax=plt.subplots(figsize=(8.4,5.6)); y=np.arange(len(items))
accs=[v["acc"] for _,v in items]
cols=[RED if a<85 else GREEN for a in accs]
ax.barh(y,accs,color=cols,edgecolor="white")
for yi,a in zip(y,accs): ax.text(a+0.6,yi,f"{a:.0f}%",va="center",fontsize=8.5)
ax.set_yticks(y); ax.set_yticklabels([nice.get(t,t) for t,_ in items],fontsize=9)
ax.set_xlabel("accuracy (baseline, pooled)"); ax.set_xlim(0,108)
ax.set_title("Where the illusion lives: character-level tasks fail, arithmetic is perfect\nyet the model certifies all of them as done",fontsize=11.5,weight="bold")
ax.axvline(85,color=GREY,ls="--",lw=1)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.grid(axis="x",alpha=0.2); fig.tight_layout(); fig.savefig(FIGS/"fig3_pertype.png",bbox_inches="tight"); plt.close(fig); print("fig3_pertype.png")

# fig4 no-fix: protocol vs baseline false-completion (exclude gpt-4o format drift)
clean=[m for m in ORDER if m!="gpt-4o"]
fig,ax=plt.subplots(figsize=(8,4.6)); x=np.arange(len(clean)); w=0.36
b=[S["per_model"][m]["baseline"]["false_completion"] for m in clean]
p=[S["per_model"][m]["protocol"]["false_completion"] for m in clean]
ax.bar(x-w/2,b,w,color=GREY,label="baseline (raw call)"); ax.bar(x+w/2,p,w,color=GOLD,label="protocol (prompt self-check)")
for xi,v in zip(x-w/2,b): ax.text(xi,v+(0.2 if v>=0 else -0.8),f"{v:+.1f}",ha="center",fontsize=9)
for xi,v in zip(x+w/2,p): ax.text(xi,v+(0.2 if v>=0 else -0.8),f"{v:+.1f}",ha="center",fontsize=9)
ax.axhline(0,color=INK,lw=1)
ax.set_xticks(x); ax.set_xticklabels([sh(m) for m in clean],fontsize=10)
ax.set_ylabel("false-completion rate")
ax.set_title("Prompt self-checking does not fix it\nThe managed re-check protocol moves the rate by roughly nothing",fontsize=11.5,weight="bold")
ax.legend(frameon=False,fontsize=9.5)
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.grid(axis="y",alpha=0.2); fig.tight_layout(); fig.savefig(FIGS/"fig4_nofix.png",bbox_inches="tight"); plt.close(fig); print("fig4_nofix.png")

# fig5 tier-pool summary
fig,ax=plt.subplots(figsize=(6.4,4.4))
tiers=["small\n(cheap models)","frontier"]; vals=[S["small_baseline_false"],S["frontier_baseline_false"]]
ax.bar([0,1],vals,0.5,color=[RED,GREEN])
for i,v in enumerate(vals): ax.text(i,v+0.3,f"{v:+.1f}%",ha="center",fontsize=12,weight="bold")
ax.set_xticks([0,1]); ax.set_xticklabels(tiers,fontsize=10.5); ax.set_ylim(0,16)
ax.set_ylabel("false-completion rate (pooled)")
ax.set_title("The illusion is concentrated in the cheap models\nthat agentic systems actually deploy at scale",fontsize=11,weight="bold")
for sp in ("top","right"): ax.spines[sp].set_visible(False)
ax.grid(axis="y",alpha=0.2); fig.tight_layout(); fig.savefig(FIGS/"fig5_tierpool.png",bbox_inches="tight"); plt.close(fig); print("fig5_tierpool.png")
print("DONE static")
