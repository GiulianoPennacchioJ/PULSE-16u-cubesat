"""Figura del report A5.5: margine del collegamento S in discesa a 4,3 Mbit/s in funzione dell'elevazione,
e volume giornaliero contro capacità di scarico."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('lb',Path(__file__).with_name('link_budget.py'))
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    lb=importlib.util.module_from_spec(spec); spec.loader.exec_module(lb)
plt.rcParams.update({'font.family':'Inter','font.size':9,'axes.spines.top':False,'axes.axisbelow':True,'axes.spines.right':False,
                     'axes.edgecolor':'#555','axes.labelcolor':'#222','xtick.color':'#444','ytick.color':'#444'})
INK='#1f3b57';ACC='#c0563a';GRID='#e3e3e3'
el=np.linspace(10,90,161)
m=[lb.margin_at(lb.budget_S_down(e),4.305e6)-0 for e in el]
fig,(a1,a2)=plt.subplots(1,2,figsize=(8.2,3.0),gridspec_kw={'width_ratios':[1.25,1]})
a1.plot(el,np.array(m),color=INK,lw=2)
a1.axhline(3,color=ACC,lw=1.2,ls='--'); a1.text(88,3.8,'margine richiesto 3 dB',ha='right',color=ACC,fontsize=8)
a1.annotate(f'{m[0]:.1f} dB a 10°'.replace('.',','),(10,m[0]),xytext=(22,m[0]-3),fontsize=8,color=INK,arrowprops=dict(arrowstyle='-',color='#888'))
a1.set_xlabel('Elevazione della stazione (°)'); a1.set_ylabel('Margine (dB)')
a1.set_title('Discesa S a 4,3 Mbit/s: margine del collegamento',fontsize=9,loc='left')
a1.grid(axis='y',color=GRID); a1.set_xlim(10,90); a1.set_ylim(0,32)
cases=['Routine','Primi 3 mesi','Picco','Picco senza\ncompressione']; vol=[46,144,194,610]
a2.barh(cases[::-1],vol[::-1],color=INK,height=0.55)
a2.axvline(2030,color=ACC,lw=1.2,ls='--'); a2.text(2000,3.45,'capacità S\n~2.030 MB/giorno',ha='right',va='top',color=ACC,fontsize=8)
for i,v in enumerate(vol[::-1]): a2.text(v+30,i,f'{v} MB',va='center',fontsize=8,color='#222')
a2.set_xlim(0,2200); a2.set_xlabel('MB al giorno per satellite')
a2.set_title('Volume da scaricare contro capacità',fontsize=9,loc='left'); a2.grid(axis='x',color=GRID)
fig.tight_layout(); fig.savefig(Path(__file__).with_name('risultati')/'figura_link.png',dpi=200)
print('ok')
