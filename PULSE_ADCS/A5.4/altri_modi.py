"""
PULSE · Fase A · A5.4.4 — Puntamento fuori dalle riprese (spinta, contatti, safe)
================================================================================

1) Spinta: quanto costa in ΔV un errore di puntamento della spinta θ
   (perdita = 1 − cos θ sulla componente utile; la componente fuori dal piano,
   fissa nel riferimento orbitale, si media su orbite intere).
2) Contatti con le stazioni (D-016): angolo dal nadir sotto cui il satellite vede
   la stazione in funzione dell'elevazione, e quota del tempo di contatto che resta
   se l'antenna è fissa a nadir con un fascio utile di ±X° (nessuna manovra, come
   EarthNext) invece di inseguire la stazione. Le durate dei contatti vengono da
   GMAT (PULSE3_contatti_stazioni.txt, elevazione minima 10°); l'elevazione
   massima di ogni passaggio si ricava dalla durata (Terra non rotante).
3) Safe mode: perdita di potenza dei pannelli in funzione dell'errore di
   puntamento al Sole (cos θ).
Uso: python altri_modi.py > risultati/altri_modi.txt
"""
import os
import re

import numpy as np

RE, H = 6378.137, 302.0
T_ORB = 5434.0                              # periodo (s), disturbi.py di A5.3
W = 2 * np.pi / T_ORB
DV_VITA = 28 + 2 + 194                      # m/s spinti in vita (D-022, senza margine)
GMAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'PULSE_GMAT',
                    'Output_PULSE', 'PULSE3_contatti_stazioni.txt')


def nadir_da_elev(el):
    return np.degrees(np.arcsin(RE / (RE + H) * np.cos(np.radians(el))))


def lam_da_elev(el):
    return np.radians(90 - el - nadir_da_elev(el))


def elev_da_nadir(eta):
    # sin(eta) = RE/(RE+H) cos(el)
    return np.degrees(np.arccos(np.sin(np.radians(eta)) * (RE + H) / RE))


def durata_sopra(lam_x, lam_min):
    if lam_min >= lam_x:
        return 0.0
    return 2 / W * np.arccos(np.cos(lam_x) / np.cos(lam_min))


def leggi_contatti(path):
    stazioni = {}
    corrente = None
    for riga in open(path, encoding='utf-8', errors='ignore'):
        m = re.match(r'Observer:\s*(\S+)', riga)
        if m:
            corrente = m.group(1); stazioni[corrente] = []; continue
        m = re.match(r'\s*\d{2} \w{3} \d{4} [\d:.]+\s+\d{2} \w{3} \d{4} [\d:.]+\s+([\d.]+)', riga)
        if m and corrente:
            stazioni[corrente].append(float(m.group(1)))
    return stazioni


def main():
    print('1) Spinta: perdita di ΔV per errore di puntamento della spinta')
    for th in (1, 2, 5, 10, 20):
        p = 1 - np.cos(np.radians(th))
        fuori = np.sin(np.radians(th)) * DV_VITA
        print(f'  θ = {th:2d}°: perdita {p*100:.3f}% -> {p*DV_VITA:.2f} m/s su {DV_VITA} m/s in vita '
              f'(margine D-022: 45 m/s); componente fuori piano {fuori:.1f} m/s, media su orbite intere')

    print('\n2) Contatti: angolo dal nadir della stazione in funzione dell\'elevazione')
    for el in (10, 15, 20, 30, 45, 90):
        print(f'  elevazione {el:2d}° -> {nadir_da_elev(el):5.1f}° dal nadir')
    lam10 = lam_da_elev(10)
    print(f'  durata massima teorica sopra 10° (passaggio allo zenit, Terra ferma): {2*lam10/W:.0f} s')
    st = leggi_contatti(GMAT)
    print('  Quota del tempo di contatto (sopra 10°) che resta con antenna fissa a nadir e fascio utile ±X°:')
    for nome, dur in st.items():
        dur = np.array(dur)
        tot = dur.sum()
        righe = []
        for X in (50, 60, 65, 70):
            el_x = elev_da_nadir(X)
            lam_x = lam_da_elev(el_x)
            resto = 0.0
            for d in dur:
                c = np.clip(np.cos(lam10) / np.cos(min(W * d / 2, lam10 * 0.999999)), -1, 1)
                lam_min = np.arccos(c)
                resto += durata_sopra(lam_x, lam_min)
            righe.append(f'±{X}° (elev ≥ {el_x:4.1f}°): {resto/tot*100:4.0f}%')
        print(f'   {nome:<10} ({len(dur)} contatti, {tot/3600:.1f} h): ' + '; '.join(righe))

    print('\n3) Safe mode: potenza dei pannelli rispetto al puntamento perfetto al Sole')
    for th in (5, 10, 15, 20, 30):
        print(f'  errore {th:2d}° -> {np.cos(np.radians(th))*100:.1f}%')


if __name__ == '__main__':
    main()
