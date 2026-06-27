"""Conceptual diagrams -> paper/figs/ (matplotlib-drawn)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 140})
FIGS = Path(__file__).resolve().parent.parent / "paper" / "figs"; FIGS.mkdir(parents=True, exist_ok=True)
RED, GREEN, BLUE, GOLD, GREY, INK, PURPLE = "#c0392b", "#2a7f3f", "#2e6fb0", "#c9962a", "#8a8f98", "#222831", "#7a4fb0"

def box(ax,x,y,w,h,text,fc,tc="white",fs=10,bold=True):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02,rounding_size=0.04",fc=fc,ec="white",lw=1.5,zorder=2))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",color=tc,fontsize=fs,weight=("bold" if bold else "normal"),zorder=3)

# ---- fig6 maturity ladder ----
fig,ax=plt.subplots(figsize=(8.6,5.6)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,6.4)
levels=[("L0  Chat","ephemeral, no record",GREY),
        ("L1  Visible board","agent posts tasks (advisory)",BLUE),
        ("L2  Enforced workflow","server gates state transitions",GREEN),
        ("L3  Verified completion","done requires evidence",PURPLE),
        ("L4  Multi-agent coordination","claim queue + dependencies",GOLD),
        ("L5  Accountable autonomy","human owns outcome, full audit",INK)]
for i,(t,d,c) in enumerate(levels):
    box(ax,1.2+i*0.28,0.4+i*0.92,5.6,0.74,"",c)
    ax.text(1.45+i*0.28,0.4+i*0.92+0.5,t,color="white",fontsize=11,weight="bold")
    ax.text(1.45+i*0.28,0.4+i*0.92+0.2,d,color="white",fontsize=8.3)
ax.annotate("the open frontier\n(the moat)",(7.1,3.6),(8.6,3.1),fontsize=9.5,color=PURPLE,weight="bold",
            arrowprops=dict(arrowstyle="->",color=PURPLE),ha="center")
ax.text(5,6.15,"The agent control-tower maturity ladder",ha="center",fontsize=13,weight="bold")
fig.tight_layout(); fig.savefig(FIGS/"fig6_ladder.png",bbox_inches="tight"); plt.close(fig); print("fig6_ladder.png")

# ---- fig7 positioning ----
fig,ax=plt.subplots(figsize=(8.4,6)); ax.set_xlim(0,10); ax.set_ylim(0,10)
ax.axhline(5,color=GREY,lw=1); ax.axvline(5,color=GREY,lw=1)
ax.text(5,9.7,"agent-native + enforced workflow",ha="center",fontsize=10,color=INK)
ax.text(5,0.2,"human PM tool + advisory AI",ha="center",fontsize=10,color=INK)
ax.text(0.2,5,"developer\nSDK",ha="center",va="center",fontsize=10,color=INK,rotation=90)
ax.text(9.8,5,"non-technical\nowner",ha="center",va="center",fontsize=10,color=INK,rotation=90)
pts=[("Asana AI Teammates",3.2,2.4,BLUE),("Linear Agents",2.6,2.0,BLUE),("monday sidekick",3.6,1.7,BLUE),
     ("LangGraph / HumanLayer",2.4,7.4,GREEN),("MCP Tasks / A2A\n(protocol)",5.0,6.4,GREY),
     ("agent control tower\n(the open quadrant)",7.6,7.6,RED)]
for t,x,y,c in pts:
    ax.scatter(x,y,s=170,color=c,edgecolor="white",zorder=3)
    ax.annotate(t,(x,y),xytext=(6,6),textcoords="offset points",fontsize=8.8,weight=("bold" if c==RED else "normal"),color=(RED if c==RED else INK))
ax.set_xticks([]); ax.set_yticks([])
ax.set_title("Where the control tower sits: owner-facing + agent-native is the open quadrant",fontsize=11.5,weight="bold")
for sp in ax.spines.values(): sp.set_visible(False)
fig.tight_layout(); fig.savefig(FIGS/"fig7_positioning.png",bbox_inches="tight"); plt.close(fig); print("fig7_positioning.png")

# ---- fig8 architecture ----
fig,ax=plt.subplots(figsize=(9.2,5.2)); ax.axis("off"); ax.set_xlim(0,12); ax.set_ylim(0,7)
box(ax,0.4,3,2.0,1.0,"AI agent(s)\n(GPT / Claude)",BLUE,fs=9.5)
# tower
ax.add_patch(FancyBboxPatch((3.3,0.6),5.4,5.8,boxstyle="round,pad=0.02,rounding_size=0.05",fc="#0f1620",ec=GREEN,lw=2,zorder=1))
ax.text(6.0,6.0,"CONTROL TOWER (system of record)",ha="center",color="white",fontsize=10.5,weight="bold")
box(ax,3.7,4.4,2.3,1.0,"Task board\nstate machine",GREEN,fs=9)
box(ax,6.2,4.4,2.1,1.0,"FLOW_GUARD\n(server verify)",RED,fs=9)
box(ax,3.7,2.9,2.3,1.0,"Calendar\n(time blocks)",GOLD,fs=9)
box(ax,6.2,2.9,2.1,1.0,"Memory\n(notes/threads)",PURPLE,fs=9)
box(ax,4.8,1.2,2.6,0.9,"claim queue (multi-agent)",GREY,fs=9)
box(ax,9.6,3,2.0,1.0,"Human owner\n(one board+cal)",INK,fs=9.5)
ax.add_patch(FancyArrowPatch((2.4,3.5),(3.3,3.5),arrowstyle="<->",color=INK,lw=1.6,mutation_scale=14))
ax.add_patch(FancyArrowPatch((8.7,3.5),(9.6,3.5),arrowstyle="->",color=INK,lw=1.6,mutation_scale=14))
ax.text(6.0,0.2,"register -> in-progress -> done, enforced; persisted; visible",ha="center",color=GREY,fontsize=9)
ax.set_title("An agent control tower: enforced board + calendar + memory + queue, over MCP",fontsize=11.5,weight="bold")
fig.tight_layout(); fig.savefig(FIGS/"fig8_architecture.png",bbox_inches="tight"); plt.close(fig); print("fig8_architecture.png")

# ---- fig9 trust gap ----
fig,ax=plt.subplots(figsize=(9,4.4)); ax.axis("off"); ax.set_xlim(0,12); ax.set_ylim(0,6)
box(ax,0.4,2.4,2.2,1.2,"AI agent",BLUE,fs=10)
ax.add_patch(FancyArrowPatch((2.6,3),(4.2,3),arrowstyle="->",color=INK,lw=2,mutation_scale=16))
box(ax,4.2,3.3,3.2,1.0,'"DONE" (claims 100%)',RED,fs=10)
box(ax,4.2,1.7,3.2,1.0,"reality: ~88% correct",GREEN,fs=10)
ax.text(5.8,5.0,"12% false 'done'",ha="center",color=RED,fontsize=11,weight="bold")
ax.add_patch(FancyArrowPatch((7.6,3),(9.0,3),arrowstyle="->",color=INK,lw=2,mutation_scale=16))
box(ax,9.0,2.4,2.6,1.2,"server verify\n(FLOW_GUARD)\nblocks the gap",PURPLE,fs=9)
ax.text(6,0.5,"the model cannot see its own 12% gap; only the system layer can",ha="center",color=GREY,fontsize=9.5)
ax.set_title("The principal-agent gap: self-report is not completion",fontsize=11.5,weight="bold")
fig.tight_layout(); fig.savefig(FIGS/"fig9_trustgap.png",bbox_inches="tight"); plt.close(fig); print("fig9_trustgap.png")
print("DONE diagrams")
