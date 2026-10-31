from fractions import Fraction as F
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Circle

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "figuras")
os.makedirs(SAIDA, exist_ok=True)

# exercicio 11: portico triarticulado, origem em A, x para a direita, y para cima
A = (0, 0)
B = (4, 3)
C = (6, 3)
E = (8, 3)
D = (6, 8)
g = 10  # peso proprio, kN/m de comprimento real

LAB = F(5)
PAB = g * LAB          # 50 kN em (2; 1,5)
PBE = g * F(4)         # 40 kN em x = 6
PCD = g * F(5)         # 50 kN em x = 6
PBCDE = PBE + PCD      # 90 kN em x = 6

# chapa BCDE, momentos em B (anti-horario positivo): VE * 4 - 90 * 2 = 0
VE = PBCDE * (6 - 4) / F(8 - 4)
# global vertical
VA = PAB + PBCDE - VE
# chapa AB, momentos em B: 3 HA - 4 VA + 50 * 2 = 0
HA = (4 * VA - PAB * 2) / F(3)
HE = -HA
# forca da rotula sobre a chapa BCDE (sobre AB e o oposto)
Bx = -HE
By = PBCDE - VE

print("HA =", HA, float(HA))
print("VA =", VA, float(VA))
print("HE =", HE, float(HE))
print("VE =", VE, float(VE))
print("rotula B, sobre BCDE: Bx =", Bx, float(Bx), " By =", By, float(By))

# conferencias globais
print("soma Fx =", HA + HE)
print("soma Fy =", VA + VE - PAB - PBCDE)
print("soma M_A =", VE * 8 - HE * 3 - PAB * 2 - PBCDE * 6)

# barra AB: t = (0,8; 0,6), n = (-0,6; 0,8), s de A para B
c, sn = F(4, 5), F(3, 5)
qt = -g * sn   # componente da carga ao longo de t (para A): -6
qn = -g * c    # componente perpendicular (sentido -n): -8
Rt = HA * c + VA * sn
Rn = -HA * sn + VA * c
print("AB: Rt =", Rt, float(Rt), " Rn =", Rn, float(Rn), " qt =", qt, " qn =", qn)


def N_AB(s):
    return -(float(Rt) + float(qt) * s)


def V_AB(s):
    return float(Rn) + float(qn) * s


def M_AB(s):
    return float(Rn) * s + float(qn) * s * s / 2


# viga BE: u = x - 4, de B para E
def N_BE(u):
    return -float(Bx)


def V_BE(u):
    v = float(By) - g * u
    if u > 2:
        v -= float(PCD)
    return v


def M_BE(u):
    m = float(By) * u - g * u * u / 2
    if u > 2:
        m -= float(PCD) * (u - 2)
    return m


# pilar CD: w = y - 3, de C para D
def N_CD(w):
    return -g * (5 - w)


def zero(w):
    return 0.0


eps = 1e-9
print("\nbarra AB (s de A para B, L = 5)")
for s in [0, 2.5, 5]:
    print(f"  s={s:4}  N={N_AB(s):9.3f}  V={V_AB(s):9.3f}  M={M_AB(s):9.3f}")
print("barra BE (u de B para E)")
for u in [0, 2, 4]:
    print(f"  u={u}  N={N_BE(u):9.3f}  V-={V_BE(u - eps):9.3f}  V+={V_BE(u + eps):9.3f}  M={M_BE(u):9.3f}")
print("pilar CD (w de C para D)")
for w in [0, 5]:
    print(f"  w={w}  N={N_CD(w):9.3f}  V=0  M=0")
print("no C: M em BC =", M_BE(2 - eps), " M em CE =", M_BE(2 + eps), " M em CD = 0")


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("−" if v < -1e-6 else "") + s


cor_c = "#1f5fbf"
cor_r = "#c0392b"


def apoio_fixo(ax, x, y):
    ax.add_patch(Polygon([[x, y], [x - 0.3, y - 0.5], [x + 0.3, y - 0.5]], closed=True, fill=False, lw=1.5))
    ax.plot([x - 0.45, x + 0.45], [y - 0.5, y - 0.5], color="black", lw=1.5)
    for i in np.linspace(x - 0.4, x + 0.4, 6):
        ax.plot([i, i - 0.12], [y - 0.5, y - 0.65], color="black", lw=0.8)


def estrutura(ax, lw=3, cor="black"):
    ax.plot([A[0], B[0]], [A[1], B[1]], color=cor, lw=lw, solid_capstyle="round")
    ax.plot([B[0], E[0]], [B[1], E[1]], color=cor, lw=lw, solid_capstyle="round")
    ax.plot([C[0], D[0]], [C[1], D[1]], color=cor, lw=lw, solid_capstyle="round")
    ax.add_patch(Circle(B, 0.13, fc="white", ec=cor, lw=1.5, zorder=5))


def seta(ax, p, q, cor, lw=2, estilo="-|>"):
    ax.annotate("", q, xytext=p, arrowprops=dict(arrowstyle=estilo, color=cor, lw=lw))


# ---------- figura 1: estrutura, cargas e reacoes ----------
fig, ax = plt.subplots(figsize=(9, 8))
ax.set_aspect("equal")
ax.axis("off")
estrutura(ax)
apoio_fixo(ax, *A)
apoio_fixo(ax, *E)
for p, n, dx, dy in [(A, "A", -0.5, 0.1), (B, "B", -0.15, -0.55), (C, "C", 0.15, 0.2), (D, "D", 0.15, -0.1), (E, "E", 0.1, 0.2)]:
    ax.text(p[0] + dx, p[1] + dy, n, fontsize=13)
# peso proprio: setas verticais ao longo das barras
for t in np.linspace(0.08, 0.92, 7):
    x, y = 4 * t, 3 * t
    seta(ax, (x, y + 0.7), (x, y + 0.05), cor_c, lw=1)
ax.text(0.4, 2.3, "10 kN/m\n(peso próprio,\npor m de barra)", color=cor_c, fontsize=10)
for x in np.linspace(4.2, 7.8, 9):
    seta(ax, (x, 3.7), (x, 3.05), cor_c, lw=1)
ax.text(6.9, 3.85, "10 kN/m", color=cor_c, fontsize=10)
for y in np.linspace(3.8, 7.6, 5):
    seta(ax, (6.45, y + 0.5), (6.45, y), cor_c, lw=1)
ax.text(6.65, 6.0, "10 kN/m\n(ao longo\ndo pilar)", color=cor_c, fontsize=10)
# reacoes
seta(ax, (-1.6, -0.3), (-0.35, -0.3), cor_r)
ax.text(-2.2, -0.15, f"{fmt(float(HA))} kN", color=cor_r, fontsize=10)
seta(ax, (0, -2.0), (0, -0.75), cor_r)
ax.text(0.15, -1.7, f"{fmt(float(VA))} kN", color=cor_r, fontsize=10)
seta(ax, (9.6, 2.7), (8.35, 2.7), cor_r)
ax.text(8.6, 2.85, f"{fmt(float(-HE))} kN", color=cor_r, fontsize=10)
seta(ax, (8, 1.0), (8, 2.25), cor_r)
ax.text(8.15, 1.2, f"{fmt(float(VE))} kN", color=cor_r, fontsize=10)
# cotas
for a, b in [(0, 4), (4, 6), (6, 8)]:
    ax.annotate("", (a, -2.5), xytext=(b, -2.5), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((a + b) / 2, -2.45, f"{b - a} m", ha="center", va="bottom", fontsize=9)
for a, b in [(0, 3), (3, 8)]:
    ax.annotate("", (10.3, a), xytext=(10.3, b), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(10.4, (a + b) / 2, f"{b - a} m", va="center", fontsize=9)
ax.set_xlim(-2.6, 11)
ax.set_ylim(-2.8, 8.6)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex11-estrutura.png"), dpi=150)
plt.close(fig)

# ---------- figura 2: chapas separadas (forcas na rotula) ----------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1, 1.1]})
for a in (a1, a2):
    a.set_aspect("equal")
    a.axis("off")
a1.plot([0, 4], [0, 3], color="black", lw=3)
a1.add_patch(Circle((4, 3), 0.12, fc="white", ec="black", lw=1.5, zorder=5))
a1.text(-0.45, 0.05, "A", fontsize=12)
a1.text(3.55, 2.35, "B", fontsize=12)
seta(a1, (2, 1.5), (2, 0.2), cor_c)
a1.text(2.15, 0.45, "50 kN", color=cor_c, fontsize=10)
seta(a1, (-1.4, -0.3), (-0.1, -0.3), cor_r)
a1.text(-1.5, -0.15, f"{fmt(float(HA))}", color=cor_r, fontsize=10)
seta(a1, (0, -1.4), (0, -0.1), cor_r)
a1.text(0.12, -1.2, f"{fmt(float(VA))}", color=cor_r, fontsize=10)
seta(a1, (4.1, 3.3), (2.8, 3.3), cor_r)
a1.text(2.5, 3.45, f"{fmt(float(Bx))}", color=cor_r, fontsize=10)
seta(a1, (4.3, 4.4), (4.3, 3.15), cor_r)
a1.text(4.45, 4.0, f"{fmt(float(By))}", color=cor_r, fontsize=10)
a1.set_title("Chapa AB (kN)", fontsize=12, fontweight="bold")
a1.set_xlim(-2, 5.5)
a1.set_ylim(-1.8, 5)

a2.plot([4, 8], [3, 3], color="black", lw=3)
a2.plot([6, 6], [3, 8], color="black", lw=3)
a2.add_patch(Circle((4, 3), 0.12, fc="white", ec="black", lw=1.5, zorder=5))
a2.text(3.6, 3.25, "B", fontsize=12)
a2.text(6.1, 3.15, "C", fontsize=12)
a2.text(8.05, 3.25, "E", fontsize=12)
a2.text(6.1, 7.9, "D", fontsize=12)
seta(a2, (5.0, 4.6), (5.0, 3.1), cor_c)
a2.text(4.4, 4.75, "40 kN\n(BE, em x = 6)", color=cor_c, fontsize=9)
seta(a2, (6.6, 5.5), (6.6, 4.0), cor_c)
a2.text(6.75, 4.6, "50 kN\n(CD, em x = 6)", color=cor_c, fontsize=9)
seta(a2, (2.6, 2.7), (3.9, 2.7), cor_r)
a2.text(2.3, 2.25, f"{fmt(float(Bx))}", color=cor_r, fontsize=10)
seta(a2, (4, 1.5), (4, 2.85), cor_r)
a2.text(4.12, 1.7, f"{fmt(float(By))}", color=cor_r, fontsize=10)
seta(a2, (9.4, 2.7), (8.1, 2.7), cor_r)
a2.text(8.4, 2.25, f"{fmt(float(-HE))}", color=cor_r, fontsize=10)
seta(a2, (8, 1.5), (8, 2.85), cor_r)
a2.text(8.12, 1.7, f"{fmt(float(VE))}", color=cor_r, fontsize=10)
a2.text(4.8, 1.0, "(peso total de BCDE: 90 kN em x = 6)", fontsize=9, color=cor_c)
a2.set_title("Chapa BCDE (kN)", fontsize=12, fontweight="bold")
a2.set_xlim(2, 10)
a2.set_ylim(0.6, 8.6)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex11-chapas.png"), dpi=150)
plt.close(fig)


# ---------- figura 3: diagramas sobre o portico ----------
def barra(ax, p0, p1, f, L, escala, sinal_lado, cor, n=120, cortes=()):
    """desenha f(s) perpendicular a barra p0->p1; lado positivo = sinal_lado * n (n = esquerda do percurso)"""
    p0 = np.array(p0, float)
    p1 = np.array(p1, float)
    t = (p1 - p0) / L
    nrm = np.array([-t[1], t[0]]) * sinal_lado
    pedacos = [0] + list(cortes) + [L]
    for a, b in zip(pedacos[:-1], pedacos[1:]):
        ss = np.linspace(a + eps, b - eps, n)
        vals = np.array([f(s) for s in ss])
        pts = p0 + np.outer(ss, t) + np.outer(vals * escala, nrm)
        base = p0 + np.outer(ss, t)
        ax.plot(pts[:, 0], pts[:, 1], color=cor, lw=1.8)
        poly = np.vstack([base, pts[::-1]])
        ax.add_patch(Polygon(poly, closed=True, fc=cor, alpha=0.18, ec="none"))
        for s, v in [(a, vals[0]), (b, vals[-1])]:
            q0 = p0 + s * t
            ax.plot([q0[0], q0[0] + v * escala * nrm[0]], [q0[1], q0[1] + v * escala * nrm[1]], color=cor, lw=1.8)
    return t, nrm


def ponto(p0, t, nrm, s, v, escala):
    q = np.array(p0, float) + s * t + v * escala * nrm
    return q


def txt(ax, xy, texto, cor="black", ha="center", va="center"):
    ax.text(xy[0], xy[1], texto, fontsize=10, fontweight="bold", color=cor, ha=ha, va=va,
            bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.5))


def base_ax(ax, titulo):
    ax.set_aspect("equal")
    ax.axis("off")
    estrutura(ax, lw=2.2, cor="#333")
    for p, n, dx, dy in [(A, "A", -0.45, -0.1), (B, "B", -0.1, 0.25), (C, "C", 0.12, -0.45), (D, "D", 0.15, 0.1), (E, "E", 0.15, -0.35)]:
        ax.text(p[0] + dx, p[1] + dy, n, fontsize=11, color="#333")
    ax.set_title(titulo, fontsize=12, fontweight="bold")
    ax.set_xlim(-1.8, 10)
    ax.set_ylim(-1.8, 9)


figN, aN = plt.subplots(figsize=(9, 7))
figV, aV = plt.subplots(figsize=(9, 7))
figM, aM = plt.subplots(figsize=(9, 7))

# N: positivo (tracao) para o lado +n, negativo para -n
base_ax(aN, "Esforço normal N (kN)")
cN = "#7d3c98"
eN = 1.2 / 131.67
t, nr = barra(aN, A, B, N_AB, 5, eN, -1, cN)
txt(aN, ponto(A, t, nr, 0, N_AB(0), eN) + [-0.3, 0.3], "−131,67", cN)
txt(aN, ponto(A, t, nr, 5, N_AB(5), eN) + [-0.2, 0.35], "−101,67", cN)
t, nr = barra(aN, B, E, N_BE, 4, eN, 1, cN)
txt(aN, ponto(B, t, nr, 1.0, N_BE(1), eN) + [0, -0.3], "−93,33", cN)
txt(aN, ponto(B, t, nr, 3.2, N_BE(3), eN) + [0, -0.3], "−93,33", cN)
t, nr = barra(aN, C, D, N_CD, 5, eN, 1, cN)
txt(aN, ponto(C, t, nr, 0.4, N_CD(0.4), eN) + [0.55, 0], "−50", cN)
txt(aN, (6.35, 7.8), "0", cN)
txt(aN, (2.0, -1.2), "compressão (−) em todas as barras", cN)

# V: positivo para o lado +n
base_ax(aV, "Esforço cortante V (kN)")
cV = "#2471a3"
eV = 1.2 / 45
t, nr = barra(aV, A, B, V_AB, 5, eV, 1, cV)
txt(aV, ponto(A, t, nr, 0, V_AB(0), eV) + [-0.3, 0.25], "+20", cV)
txt(aV, ponto(A, t, nr, 2.5, 0, eV) + [-0.35, 0.3], "0", cV)
txt(aV, ponto(A, t, nr, 5, V_AB(5), eV) + [0.35, -0.25], "−20", cV)
t, nr = barra(aV, B, E, V_BE, 4, eV, 1, cV, cortes=(2,))
txt(aV, ponto(B, t, nr, 0, V_BE(eps), eV) + [0.1, 0.3], "+45", cV)
txt(aV, ponto(B, t, nr, 2, V_BE(2 - eps), eV) + [0.45, 0.3], "+25", cV)
txt(aV, ponto(B, t, nr, 2, V_BE(2 + eps), eV) + [0.45, -0.25], "−25", cV)
txt(aV, ponto(B, t, nr, 4, V_BE(4 - eps), eV) + [0.1, -0.3], "−45", cV)
txt(aV, (6.5, 6.0), "V = 0 no pilar", cV, ha="left")

# M: positivo traciona o lado -n, desenhado do lado tracionado
base_ax(aM, "Momento fletor M (kN.m), lado tracionado")
cM = "#b03a2e"
eM = 1.8 / 70
t, nr = barra(aM, A, B, M_AB, 5, eM, -1, cM)
txt(aM, ponto(A, t, nr, 2.5, M_AB(2.5), eM) + [0.3, -0.35], "25", cM)
txt(aM, (A[0] + 0.35, A[1] - 0.3), "0", cM)
t, nr = barra(aM, B, E, M_BE, 4, eM, -1, cM, cortes=(2,))
txt(aM, ponto(B, t, nr, 2, M_BE(2), eM) + [0, -0.3], "70", cM)
txt(aM, (B[0] - 0.2, B[1] + 0.45), "0 (rótula)", cM, ha="right")
txt(aM, (E[0] + 0.2, E[1] + 0.3), "0", cM, ha="left")
txt(aM, (6.5, 6.0), "M = 0 no pilar", cM, ha="left")

for f, nome in [(figN, "N"), (figV, "V"), (figM, "M")]:
    f.tight_layout()
    f.savefig(os.path.join(SAIDA, f"ex11-diagrama-{nome}.png"), dpi=150)
    plt.close(f)
print("figuras salvas em", SAIDA)
