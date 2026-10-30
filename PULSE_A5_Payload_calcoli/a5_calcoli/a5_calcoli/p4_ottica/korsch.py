# Tracciamento dei raggi di un Korsch (TMA in asse) "srotolato": primario, secondario, terziario.
# Lo specchio piano di rinvio non cambia le aberrazioni e si aggiunge solo nel disegno.
import numpy as np

def intersect(p, d, z0, c, k):
    """p, d: (N,3). Intersezione con la superficie conica di vertice z0 (radice vicina al vertice)."""
    t0 = (z0 - p[:,2])/d[:,2]                      # prima al piano del vertice
    p = p + t0[:,None]*d
    x, y, z = p[:,0], p[:,1], p[:,2]-z0
    dx, dy, dz = d[:,0], d[:,1], d[:,2]
    A = c*(dx*dx + dy*dy + (1+k)*dz*dz)
    B = 2*(c*(x*dx + y*dy + (1+k)*z*dz) - dz)
    C = c*(x*x + y*y + (1+k)*z*z) - 2*z
    disc = np.sqrt(np.maximum(B*B - 4*A*C, 0))
    q = -0.5*(B + np.sign(B)*disc)
    t = C/q
    p2 = p + t[:,None]*d
    t = t + t0
    n = np.stack([c*p2[:,0], c*p2[:,1], c*(1+k)*(p2[:,2]-z0) - 1], axis=1)
    n /= np.linalg.norm(n, axis=1)[:,None]
    return p2, n, t

def reflect(d, n):
    return d - 2*np.sum(d*n, axis=1)[:,None]*n

def trace(sys, fx, fy, pupil):
    """sys: dict con c1,k1,c2,k2,c3,k3,d1,z3. Primario a z=0 (pupilla d'ingresso), secondario a z=-d1,
    terziario a z=z3 (>0, dietro il primario). fx, fy campo in gradi. pupil: (N,2) in mm."""
    N = len(pupil)
    ax, ay = np.radians(fx), np.radians(fy)
    d = np.tile(np.array([np.tan(ax), np.tan(ay), 1.0]), (N,1)); d /= np.linalg.norm(d, axis=1)[:,None]
    p = np.zeros((N,3)); p[:,0], p[:,1] = pupil[:,0], pupil[:,1]
    p = p - 2000*d                                   # partenza 2 m prima, fronte d'onda piano
    L = np.zeros(N)
    # cammino dal piano perpendicolare a d passante per l'origine
    L += np.sum(p*d, axis=1)                         # cammino misurato dal piano d'onda per l'origine
    hits = []
    for (z0, c, k) in [(0.0, sys['c1'], sys['k1']), (-sys['d1'], sys['c2'], sys['k2']), (sys['z3'], sys['c3'], sys['k3'])]:
        q, n, t = intersect(p, d, z0, c, k)
        L += t
        d = reflect(d, n); p = q; hits.append(q.copy())
    return p, d, L, hits

def efl_abs(sys):
    pu = np.array([[0.0, 0.5]])
    p, d, L, _ = trace(sys, 0, 0, pu)
    return abs(0.5/(d[0,1]/abs(d[0,2])))

def pupil_grid(D, eps, n=24):
    g = np.linspace(-D/2, D/2, n)
    X, Y = np.meshgrid(g, g); r = np.hypot(X, Y)
    m = (r <= D/2) & (r >= eps*D/2)
    return np.stack([X[m], Y[m]], axis=1)

def image_on_plane(p, d, zi):
    t = (zi - p[:,2])/d[:,2]
    return p + t[:,None]*d

def wfe_rms(sys, fx, fy, zi, pupil, lam=550e-6):
    """Errore d'onda RMS (mm) rispetto al miglior punto Q sul piano zi (posizione laterale libera)."""
    p, d, L, _ = trace(sys, fx, fy, pupil)
    P = image_on_plane(p, d, zi)
    Q0 = P[:, :2].mean(axis=0)
    best = None
    # OPD verso Q: L + |p - Q| (Fermat), ottimizzo Q laterale con 2 passi di Gauss-Newton
    Q = Q0.copy()
    for _ in range(4):
        def opd(Q):
            r = np.sqrt((p[:,0]-Q[0])**2 + (p[:,1]-Q[1])**2 + (p[:,2]-zi)**2)
            w = L + r; return w - w.mean()
        w = opd(Q); eps = 1e-4
        J = np.stack([(opd(Q+[eps,0])-w)/eps, (opd(Q+[0,eps])-w)/eps], axis=1)
        dq, *_ = np.linalg.lstsq(J, -w, rcond=None); Q = Q + dq
    w = opd(Q)
    spot = P[:, :2] - P[:, :2].mean(axis=0)
    return np.sqrt(np.mean(w**2)), np.sqrt(np.mean(np.sum(spot**2, axis=1))), Q
