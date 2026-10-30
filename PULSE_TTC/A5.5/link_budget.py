"""A5.5.4 - Link budget banda S e UHF per PULSE (Fase A, primo ordine).
Fonti: ISIS TXS2 (31 dBm tipico, 33 max; OQPSK; conv K7 r1/2 + RS(255,223), Eb/N0 2,4 dB a BER 1e-5,
perdita di implementazione 2 dB; Rs 0,15625-5 Msym/s; 13 W in trasmissione), ISIS S-band patch
(6,5 dBic, HPBW 100°), KSAT S-band 3,7 m (G/T 12,6 dB/K, EIRP 44,8 dBW) dalla wiki NTNU,
ISIS VHF/UHF (27 dBm, 9600 bit/s, 400,15-402 MHz). Valori senza fonte = ipotesi TBC."""
import numpy as np, re, datetime as dt
Re=6378.137; h=302.0; a=Re+h; mu=398600.4418; c=299792458.0; k=-228.6
w=np.sqrt(mu/a**3)
db=lambda x:10*np.log10(x)
def rng(el): e=np.radians(el); return np.sqrt(a**2-(Re*np.cos(e))**2)-Re*np.sin(e)
def nadir(el): e=np.radians(el); return np.degrees(np.arcsin(Re*np.cos(e)/a))
def fspl(d_km,f): return 20*np.log10(4*np.pi*d_km*1e3*f/c)
n_patch=np.log(0.5)/np.log(np.cos(np.radians(50)))   # cos^n con HPBW 100°
def g_patch(theta,G0=6.5): return G0+10*n_patch*np.log10(np.maximum(np.cos(np.radians(theta)),1e-6))
MARG=3.0
def riga(nome,val,unit=''): print(f'  {nome:42s}{val:9.1f} {unit}')

def budget_S_down(el,Pt_dBm=31,verbose=False):
    f=2245e6; d=rng(el); th=nadir(el)
    Pt=Pt_dBm-30; Ltx=1.0; Gt=g_patch(th); Lfs=fspl(d,f); Latm=0.5; Lpol=0.5; GT=12.6
    CN0=Pt-Ltx+Gt-Lfs-Latm-Lpol+GT-k
    if verbose:
        print(f'\n[S discesa] elevazione {el}°, distanza {d:.0f} km, angolo dal nadir {th:.1f}°')
        for n,v,u in (('Potenza trasmessa (31 dBm)',Pt,'dBW'),('Perdite cavo/diplexer (TBC)',-Ltx,'dB'),
                      (f'Guadagno patch a {th:.0f}° (modello cos^n)',Gt,'dBic'),('Perdita di spazio libero',-Lfs,'dB'),
                      ('Atmosfera (TBC)',-Latm,'dB'),('Polarizzazione (TBC)',-Lpol,'dB'),
                      ('G/T stazione (KSAT 3,7 m)',GT,'dB/K'),('Costante di Boltzmann',-k,'dB'),('C/N0',CN0,'dB-Hz')): riga(n,v,u)
    return CN0
def max_rate(CN0,EbN0=2.4,impl=2.0,marg=MARG): return 10**((CN0-EbN0-impl-marg)/10)
RS=np.array([0.15625,0.3125,0.625,1.25,2.5,5.0])*1e6
INFO=2*RS*0.430502   # OQPSK, rendimento codice+trama dal datasheet
def best_info(CN0):
    ok=INFO[INFO<=max_rate(CN0)]; return ok.max() if len(ok) else 0.0
def margin_at(CN0,Rb,EbN0=2.4,impl=2.0): return CN0-db(Rb)-EbN0-impl

print('=== 1) Banda S, discesa ===')
for el in (10,30,90):
    CN0=budget_S_down(el,verbose=(el==10))
    Rmax=max_rate(CN0); Rb=best_info(CN0)
    print(f'  elev {el:2d}°: C/N0 {CN0:5.1f} dB-Hz -> velocità max con 3 dB di margine {Rmax/1e6:5.2f} Mbit/s; '
          f'passo del TXS2 utilizzabile {Rb/1e6:.3f} Mbit/s (margine {margin_at(CN0,Rb):.1f} dB)')
for p in (33,):
    CN0=budget_S_down(10,Pt_dBm=p); print(f'  con {p} dBm a 10°: max {max_rate(CN0)/1e6:.2f} Mbit/s, passo {best_info(CN0)/1e6:.3f}')

# elevazione minima per ogni passo di velocità
print('\n  Elevazione minima per ogni velocità del TXS2 (3 dB di margine):')
els=np.linspace(10,90,801)
for R in INFO:
    ok=[e for e in els if max_rate(budget_S_down(e))>=R]
    print(f'    {R/1e6:6.3f} Mbit/s utili: da {ok[0]:.1f}°' if ok else f'    {R/1e6:6.3f} Mbit/s: mai')

# ---- capacità giornaliera dai contatti GMAT
from pathlib import Path
D=str(Path(__file__).resolve().parents[2]/'PULSE_GMAT'/'Output_PULSE')+'/'
fmt='%d %b %Y %H:%M:%S.%f'
dur=[]
for s in ('PULSE','PULSE2','PULSE3','PULSE4'):
    for L in open(D+f'{s}_contatti_stazioni.txt'):
        p=re.match(r'(\d\d \w{3} \d{4} [\d:.]+)\s+(\d\d \w{3} \d{4} [\d:.]+)\s+([\d.]+)',L.strip())
        if p: dur.append(float(p.group(3)))
giorni=30.0*4
lam10=np.arccos(Re/a*np.cos(np.radians(10)))-np.radians(10)
def el_from_lam(lam): return np.degrees(np.arctan2(np.cos(lam)-Re/a,np.sin(lam)))
# tabella velocità in funzione dell'elevazione (precalcolo)
eg=np.linspace(0,90,901); Rg=np.array([best_info(budget_S_down(max(e,0.01))) for e in eg])
ACQ=30.0  # s persi per agganciare il segnale a ogni contatto (TBC)
fix=best_info(budget_S_down(10))
cap_fix=0;cap_acm=0;t_tot=0
for d in dur:
    th=min(w*d/2,lam10*0.999999)
    lmin=np.arccos(np.clip(np.cos(lam10)/np.cos(th),-1,1))
    t=np.linspace(-d/2,d/2,max(int(d),2))
    lam=np.arccos(np.clip(np.cos(lmin)*np.cos(w*t),-1,1))
    el=el_from_lam(lam); R=np.interp(el,eg,Rg)
    usable=np.abs(t)<=max(d/2-ACQ/2,0)   # tolgo ACQ s (metà a inizio, metà a fine: semplificazione)
    dt_=t[1]-t[0] if len(t)>1 else 0
    cap_acm+=np.sum(R[usable])*dt_; cap_fix+=fix*np.sum(usable)*dt_; t_tot+=d
print(f'\n=== 2) Capacità di scarico in banda S per satellite (GMAT gen 2026, {len(dur)/giorni:.1f} contatti/giorno, {t_tot/giorni/60:.1f} min/giorno, {ACQ:.0f} s di aggancio per contatto) ===')
print(f'  velocità fissa dimensionata a 10° ({fix/1e6:.3f} Mbit/s): {cap_fix/giorni/8/1e6:7.0f} MB/giorno')
print(f'  velocità variabile per elevazione (passi del TXS2):  {cap_acm/giorni/8/1e6:7.0f} MB/giorno')

print('\n=== 3) Banda S, salita (ricevitore a bordo) ===')
f=2067e6; d=rng(10); th=nadir(10)
EIRP=44.8; Grx=g_patch(th); Tsys=600.0; Lrx=1.0
GT=Grx-Lrx-db(Tsys); CN0=EIRP-fspl(d,f)-0.5-0.5+GT-k
for nm,v,u in (('EIRP stazione (KSAT)',EIRP,'dBW'),('Perdita di spazio libero',-fspl(d,f),'dB'),('Atmosfera + polarizzazione (TBC)',-1.0,'dB'),
               (f'G/T bordo (patch {Grx:.1f} dBic, Tsys {Tsys:.0f} K TBC)',GT,'dB/K'),('C/N0',CN0,'dB-Hz')): riga(nm,v,u)
Rup=max_rate(CN0,EbN0=9.6,impl=2.0)
print(f'  a 10°, BPSK senza codifica (Eb/N0 9,6 dB a 1e-5): max {Rup/1e3:.0f} kbit/s con 3 dB di margine')
for R in (64e3,128e3,256e3): print(f'    {R/1e3:.0f} kbit/s: margine {margin_at(CN0,R,EbN0=9.6):.1f} dB')

print('\n=== 4) UHF (400,15-401 MHz, operazioni spaziali; 435-438 MHz è banda amatoriale) ===')
f=401e6; d=rng(10)
Pt=27-30; Gt=-3.0; Lpol=3.0; Ltx=1.0; Latm=0.5
G_yagi=14.0; T_gs=1000.0; GT_gs=G_yagi-db(T_gs)
CN0=Pt-Ltx+Gt-fspl(d,f)-Latm-Lpol+GT_gs-k
for nm,v,u in (('Potenza (27 dBm, ISIS)',Pt,'dBW'),('Cavo (TBC)',-Ltx,'dB'),('Dipolo a 70° dal nadir (TBC)',Gt,'dBi'),
               ('Perdita di spazio libero',-fspl(d,f),'dB'),('Atmosfera (TBC)',-Latm,'dB'),('Polarizzazione lineare/circolare',-Lpol,'dB'),
               (f'G/T stazione (yagi {G_yagi:.0f} dBic, Tsys {T_gs:.0f} K, stima)',GT_gs,'dB/K'),('C/N0',CN0,'dB-Hz')): riga(nm,v,u)
for R in (9600,4800,1200): print(f'  {R} bit/s, BPSK senza codifica: margine {margin_at(CN0,R,EbN0=9.6):.1f} dB (serve ≥ 3)')
print(f'  capacità a 9600 bit/s: {9600*t_tot/giorni*0.8/8/1e6:.1f} MB/giorno (80% del tempo, TBC)')

print('\n=== 5) Energia delle radio TT&C (D-084, ingresso per A5.6) ===')
tc=t_tot/giorni/3600            # ore di contatto al giorno
rx_s=1.3                        # ore/giorno di sola ricezione S attorno ai contatti (finestre ~2,5 h, TBC)
E_tx=15.0*tc; E_rx=4.0*rx_s; E_vhf=0.48*24
print(f'  XLink-S con TX e RX (< 15 W) x {tc*60:.1f} min/giorno = {E_tx:.1f} Wh/giorno')
print(f'  XLink-S solo RX (< 4 W) x {rx_s:.1f} h/giorno = {E_rx:.1f} Wh/giorno')
print(f'  ricevitore VHF sempre acceso (0,48 W) = {E_vhf:.1f} Wh/giorno')
print(f'  totale ~{E_tx+E_rx+E_vhf:.0f} Wh/giorno (confronto: ricevitore S acceso sempre = {4*24:.0f} Wh/giorno solo di ricezione)')
