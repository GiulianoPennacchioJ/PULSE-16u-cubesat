"""PULSE · A5.3 c) parte 2 — Casi di sensibilità della simulazione 1-asse:
inerzia nota al controllore, banda intermedia, quota minima 294,7 km.
Uso: python sensibilita.py   (richiede sim1asse.py nella stessa cartella)
"""
from sim1asse import caso

CASI = [
    ('F2 inerzia vera 1,14, controllore 1,14, banda 0,3, MEMS', dict(nome='F2', coppia_rampa=None, t_aggancio=None, I=1.14, banda=0.3, fc=10, giroscopio='MEMS', ihat=1.14)),
    ('F2 inerzia vera 1,14, controllore 0,69, banda 0,5, MEMS', dict(nome='F2', coppia_rampa=None, t_aggancio=None, I=1.14, banda=0.5, fc=10, giroscopio='MEMS')),
    ('F2 inerzia vera 0,64, banda 1,0, MEMS, quota 294,7 km', dict(nome='F2', coppia_rampa=None, t_aggancio=None, I=0.64, banda=1.0, fc=10, giroscopio='MEMS', a=6672.85)),
    ('F2 inerzia vera 1,14, banda 1,0, MEMS, quota 294,7 km', dict(nome='F2', coppia_rampa=None, t_aggancio=None, I=1.14, banda=1.0, fc=10, giroscopio='MEMS', a=6672.85)),
    ('F1 3e-3, inerzia vera 1,14, controllore 1,14, banda 1,0, MEMS', dict(nome='F1', coppia_rampa=3e-3, t_aggancio=-2.0, I=1.14, banda=1.0, fc=10, giroscopio='MEMS', ihat=1.14)),
    ('F1 7e-3, inerzia vera 1,14, controllore 1,14, banda 1,0, MEMS', dict(nome='F1', coppia_rampa=7e-3, t_aggancio=-2.0, I=1.14, banda=1.0, fc=10, giroscopio='MEMS', ihat=1.14)),
]

if __name__ == '__main__':
    with open('risultati/sensibilita.txt', 'w', encoding='utf-8') as f:
        for nome, kw in CASI:
            r, _, _ = caso(**kw)
            riga = nome + ' -> ' + ', '.join(f'{k}={v:.4g}' if isinstance(v, float) else f'{k}={v}' for k, v in r.items())
            print(riga); f.write(riga + '\n')
