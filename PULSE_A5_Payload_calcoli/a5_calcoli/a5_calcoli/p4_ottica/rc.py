# Tracciamento dei raggi sequenziale per specchi e lenti (superfici coniche), con dispersione della silice fusa.
# Usato per il telescopio Ritchey-Chretien + correttore a lenti di PULSE (A5.P4).
import numpy as np

def n_silice(lam_um):
    l2 = lam_um**2
    return np.sqrt(1 + 0.6961663*l2/(l2 - 0.0684043**2) + 0.4079426*l2/(l2 - 0.1162414**2) + 0.8974794*l2/(l2 - 9.896161**2))

def _hit(p, d, z0, c, k):
    t0 = (z0 - p[:,2])/d[:,2]; p = p + t0[:,None]*d
    x, y, z = p[:,0], p[:,1], p[:,2] - z0
    dx, dy, dz = d[:,0], d[:,1], d[:,2]
    A = c*(dx*dx + dy*dy + (1+k)*dz*dz)
    B = 2*(c*(x*dx + y*dy + (1+k)*z*dz) - dz)
    C = c*(x*x + y*y + (1+k)*z*z) - 2*z
    disc = np.sqrt(np.maximum(B*B - 4*A*C, 0))
    q = -0.5*(B + np.sign(B)*disc); t = C/q
    p2 = p + t[:,None]*d
    n = np.stack([c*p2[:,0], c*p2[:,1], c*(1+k)*(p2[:,2] - z0) - 1], axis=1)
    n /= np.linalg.norm(n, axis=1)[:,None]
    return p2, n, t + t0

def trace(surf, fx, fy, pupil, lam):
    """surf: lista di dict(z, c, k, tipo 'M' (specchio) o 'L' (diottro), mezzo dopo: 'aria'/'silice').
    Pupilla d'ingresso sul piano z=0 (primario). Ritorna punto e direzione finali, cammino ottico, punti sulle superfici."""
    N = len(pupil)
    d = np.tile(np.array([np.tan(np.radians(fx)), np.tan(np.radians(fy)), 1.0]), (N,1)); d /= np.linalg.norm(d, axis=1)[:,None]
    p = np.zeros((N,3)); p[:,:2] = pupil; p = p - 2000*d
    L = np.sum(p*d, axis=1)                              # cammino misurato dal piano d'onda per l'origine
    n1 = 1.0; hits = []
    for s in surf:
        off = np.array([s.get('dx', 0.0), s.get('dy', 0.0), 0.0])   # decentramento (tolleranze)
        q, nrm, t = _hit(p - off, d, s['z'], s['c'], s.get('k', 0.0)); q = q + off
        L = L + n1*t
        cosi = -np.sum(d*nrm, axis=1)
        flip = cosi < 0; nrm[flip] *= -1; cosi[flip] *= -1
        if s['tipo'] == 'M':
            d = d + 2*cosi[:,None]*nrm
        else:
            n2 = n_silice(lam) if s['mezzo'] == 'silice' else 1.0
            eta = n1/n2; k2 = 1 - eta**2*(1 - cosi**2)
            d = eta*d + (eta*cosi - np.sqrt(np.maximum(k2, 0)))[:,None]*nrm
            n1 = n2
        p = q; hits.append(q.copy())
    return p, d, L, hits

def pupil_grid(D, eps, n):
    g = np.linspace(-D/2, D/2, n); X, Y = np.meshgrid(g, g); r = np.hypot(X, Y)
    m = (r <= D/2) & (r >= eps*D/2); return np.stack([X[m], Y[m]], axis=1)

def efl(surf, lam=0.6):
    p, d, L, _ = trace(surf, 0, 0, np.array([[0.0, 0.5]]), lam)
    return abs(0.5/(d[0,1]/abs(d[0,2])))

def wfe(surf, fx, fy, zi, pupil, lam, Q=None, vettore=False):
    """Errore d'onda RMS (mm) verso il miglior punto Q sul piano z=zi; se Q e' dato, verso quel punto."""
    p, d, L, _ = trace(surf, fx, fy, pupil, lam)
    def opd(Q):
        r = np.sqrt((p[:,0]-Q[0])**2 + (p[:,1]-Q[1])**2 + (p[:,2]-zi)**2)
        w = L + np.sign(d[:,2])*0 + r; return w - w.mean()
    t = (zi - p[:,2])/d[:,2]; P = p + t[:,None]*d
    if Q is None:
        Q = P[:,:2].mean(axis=0)
        for _ in range(3):
            w = opd(Q); e = 1e-4
            J = np.stack([(opd(Q + [e, 0]) - w)/e, (opd(Q + [0, e]) - w)/e], axis=1)
            Q = Q + np.linalg.lstsq(J, -w, rcond=None)[0]
    w = opd(Q)
    if vettore: return w/np.sqrt(len(w)), Q, P
    return np.sqrt(np.mean(w**2)), Q, P
