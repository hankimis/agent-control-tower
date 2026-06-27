"""Animated GIFs -> paper/figs/."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image

plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 118})
ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT/"paper"/"figs"
RED, GREEN, BLUE, GOLD, GREY, INK, PURPLE = "#c0392b","#2a7f3f","#2e6fb0","#c9962a","#8a8f98","#222831","#7a4fb0"
def to_pil(fig): fig.canvas.draw(); im=Image.fromarray(np.asarray(fig.canvas.buffer_rgba())).convert("RGB"); plt.close(fig); return im
def save(frames,name,dur): frames[0].save(FIGS/name,save_all=True,append_images=frames[1:],duration=dur,loop=0,optimize=True); print(name)
def ease(t): return 1-(1-t)**3

# gif1: the illusion reveal (actual grows to 88 while claim shows 100)
frames=[]; N=16
for k in range(N+1):
    t=ease(k/N); fig,ax=plt.subplots(figsize=(6.4,4.4))
    ax.bar([0],[100],0.5,color=RED); ax.bar([1],[88*t],0.5,color=GREEN)
    ax.text(0,101,"claimed 100",ha="center",fontsize=10,color=RED,weight="bold")
    if k==N:
        ax.text(1,89.5,"actual 88",ha="center",fontsize=10,color=GREEN,weight="bold")
        ax.annotate("12% false 'done'",(0.5,94),ha="center",color=RED,fontsize=11,weight="bold")
    ax.set_xticks([0,1]); ax.set_xticklabels(["self-report","verified"],fontsize=11)
    ax.set_ylim(0,112); ax.set_ylabel("% complete"); ax.set_title("The completion illusion",fontsize=12.5,weight="bold")
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    ax.grid(axis="y",alpha=0.2); fig.tight_layout(); frames.append(to_pil(fig))
save(frames,"gif1_illusion.gif",[80]*N+[2400])

# gif2: FLOW_GUARD state machine
def fg_frame(stage):
    fig,ax=plt.subplots(figsize=(7.2,3.2)); ax.axis("off"); ax.set_xlim(0,12); ax.set_ylim(0,4)
    def b(x,txt,c): ax.add_patch(FancyBboxPatch((x,1.3),2.4,1.4,boxstyle="round,pad=0.02,rounding_size=0.06",fc=c,ec="white",lw=1.5)); ax.text(x+1.2,2.0,txt,ha="center",va="center",color="white",fontsize=11,weight="bold")
    b(0.6,"TODO",GREY); b(4.6,"IN_PROGRESS",BLUE); b(8.8,"DONE",GREEN)
    if stage==0:  # illegal jump blocked
        ax.add_patch(FancyArrowPatch((3.0,3.1),(8.8,3.1),arrowstyle="->",color=RED,lw=2.4,mutation_scale=16,connectionstyle="arc3,rad=-0.3"))
        ax.text(6,3.6,"TODO -> DONE  ✗ BLOCKED (flow-guard)",ha="center",color=RED,fontsize=11,weight="bold")
    elif stage==1:
        ax.add_patch(FancyArrowPatch((3.0,2.0),(4.6,2.0),arrowstyle="->",color=INK,lw=2.4,mutation_scale=16)); ax.text(3.8,2.5,"claim",ha="center",fontsize=9.5,color=INK)
    else:
        ax.add_patch(FancyArrowPatch((3.0,2.0),(4.6,2.0),arrowstyle="->",color=INK,lw=2,mutation_scale=14))
        ax.add_patch(FancyArrowPatch((7.0,2.0),(8.8,2.0),arrowstyle="->",color=GREEN,lw=2.4,mutation_scale=16)); ax.text(8,2.5,"verified done ✓",ha="center",fontsize=9.5,color=GREEN,weight="bold")
    ax.set_title("Server-enforced workflow: you cannot skip to 'done'",fontsize=12,weight="bold")
    fig.tight_layout(); return to_pil(fig)
save([fg_frame(0),fg_frame(1),fg_frame(2)],"gif2_flowguard.gif",[1500,1100,1900])

# gif3: ladder climb
levels=[("L0 Chat",GREY),("L1 Visible board",BLUE),("L2 Enforced",GREEN),("L3 Verified",PURPLE),("L4 Multi-agent",GOLD),("L5 Accountable",INK)]
frames=[]
for top in range(len(levels)):
    fig,ax=plt.subplots(figsize=(6.2,4.6)); ax.axis("off"); ax.set_xlim(0,8); ax.set_ylim(0,6.4)
    for i,(t,c) in enumerate(levels):
        on = i<=top
        ax.add_patch(FancyBboxPatch((1+i*0.25,0.4+i*0.9),4.6,0.72,boxstyle="round,pad=0.02,rounding_size=0.04",
                     fc=(c if on else "#e6e9ee"),ec="white",lw=1.4))
        ax.text(1.25+i*0.25,0.4+i*0.9+0.36,t,color=("white" if on else "#b3b9c2"),fontsize=10,weight="bold",va="center")
    ax.text(4,6.1,"Climbing the control-tower ladder",ha="center",fontsize=12,weight="bold")
    fig.tight_layout(); frames.append(to_pil(fig))
save(frames,"gif3_ladder.gif",[700]*5+[2200])

# gif4: trust vs verify blink
def tv(verify):
    fig,ax=plt.subplots(figsize=(6.2,3.4)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,4)
    if not verify:
        ax.add_patch(FancyBboxPatch((2.5,1.2),5,1.6,boxstyle="round,pad=0.02,rounding_size=0.06",fc=RED,ec="white"))
        ax.text(5,2.0,"TRUST the self-report\n'I completed all of it'",ha="center",va="center",color="white",fontsize=12,weight="bold")
    else:
        ax.add_patch(FancyBboxPatch((2.5,1.2),5,1.6,boxstyle="round,pad=0.02,rounding_size=0.06",fc=GREEN,ec="white"))
        ax.text(5,2.0,"VERIFY at the system layer\n12% of 'done' was false",ha="center",va="center",color="white",fontsize=12,weight="bold")
    fig.tight_layout(); return to_pil(fig)
save([tv(False),tv(True)],"gif4_trust.gif",[1600,1600])
print("DONE gifs")
