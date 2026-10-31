from fractions import Fraction as F
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "figuras")
os.makedirs(SAIDA, exist_ok=True)

# exercicio 14: origem em B, x para a direita, y para cima
A = np.array([0.0, 3.0])
B = np.array([0.0, 0.0])
C = np.array([4.0, 3.0])
q = F(12)  # kN/m de comprimento real da barra (peso proprio, vertical)
LAB, LBC = F(3), F(5)
cos, sen = F(4, 5), F(3, 5)  # angulo de BC com a horizontal

PAB = q * LAB  # 36 kN em x = 0
PBC = q * LBC  # 60 kN em x = 2
xPAB, xPBC = F(0), F(2)

# equilibrio global: HA (biela horizontal), VA (biela vertical em A), VC (biela vertical em C)
HA = F(0)
VC = (PAB * (xPAB - 0) + PBC * (xPBC - 0)) / 4  # momentos em A (x = 0)
VA = PAB + PBC - VC
print("HA =", HA, " VA =", VA, float(VA), " VC =", VC, float(VC))
print("conferencia SFy:", VA + VC - PAB - PBC, " SM_C:", VA * 4 - PAB * 4 - PBC * 2)

# barra AB, percorrida de A para B, s = distancia a A
def NAB(s):
    return VA - q * s

# barra BC, percorrida de B para C, s = distancia a B
qpar, qperp = q * sen, q * cos  # 7,2 e 9,6 kN/m
FB = VA - PAB  # forca vertical que AB transmite a BC em B (para cima)
print("forca em B (AB -> BC):", FB, " qpar =", float(qpar), " qperp =", float(qperp))


def NBC(s):
    return -(FB - q * s) * sen


def VBC(s):
    return (FB - q * s) * cos


def MBC(s):
    return FB * cos * s - q * s * cos * s / 2


for s in [F(0), F(3, 2), F(3)]:
    print(f"AB s={float(s):4.2f}  N={float(NAB(s)):7.2f}  V=0  M=0")
for s in [F(0), F(5, 4), F(5, 2), F(15, 4), F(5)]:
    print(f"BC s={float(s):4.2f}  N={float(NBC(s)):7.2f}  V={float(VBC(s)):7.2f}  M={float(MBC(s)):7.2f}")
print("MB (por BC) =", MBC(0), " MC =", MBC(LBC), " Mmax =", MBC(F(5, 2)))


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("−" if v < -1e-6 else "") + s


cor_c, cor_r = "#1f5fbf", "#c0392b"


def biela(ax, p, d, parede):
    """biela de p ate p+d com apoio articulado na ponta"""
    e = p + d
    ax.plot([p[0], e[0]], [p[1], e[1]], color="black", lw=1.2)
    ax.add_patch(Circle(e, 0.07, fc="white", ec="black", lw=1.2, zorder=5))
    if parede == "teto":
        ax.plot([e[0] - 0.35, e[0] + 0.35], [e[1] + 0.07, e[1] + 0.07], color="black", lw=1.5)
        for i in np.linspace(e[0] - 0.3, e[0] + 0.35, 7):
            ax.plot([i, i - 0.1], [e[1] + 0.2, e[1] + 0.07], color="black", lw=0.8)
    else:
        ax.plot([e[0] - 0.07, e[0] - 0.07], [e[1] - 0.35, e[1] + 0.35], color="black", lw=1.5)
        for i in np.linspace(e[1] - 0.3, e[1] + 0.35, 7):
            ax.plot([e[0] - 0.2, e[0] - 0.07], [i - 0.1, i], color="black", lw=0.8)


def chapa(ax, lw=3, cor="black"):
    ax.plot([A[0], B[0], C[0]], [A[1], B[1], C[1]], color=cor, lw=lw, solid_joinstyle="miter", zorder=3)


def vinculos(ax):
    biela(ax, A, np.array([0, 0.7]), "teto")
    biela(ax, A, np.array([-0.9, 0]), "parede")
    biela(ax, C, np.array([0, 0.7]), "teto")
    for p in (A, C):
        ax.add_patch(Circle(p, 0.07, fc="white", ec="black", lw=1.2, zorder=6))


# ---------- figura 1: estrutura e reacoes ----------
fig, ax = plt.subplots(figsize=(9, 6.2))
ax.set_aspect("equal")
ax.axis("off")
chapa(ax)
vinculos(ax)
ax.text(A[0] + 0.12, A[1] - 0.3, "A", fontsize=13)
ax.text(B[0] - 0.3, B[1] - 0.05, "B", fontsize=13)
ax.text(C[0] + 0.15, C[1] - 0.25, "C", fontsize=13)

# peso proprio: setas verticais ao longo das barras
for y in np.linspace(0.3, 2.7, 6):
    ax.annotate("", (-0.05, y - 0.25), xytext=(-0.05, y + 0.1),
                arrowprops=dict(arrowstyle="->", color=cor_c, lw=1))
for t in np.linspace(0.08, 0.88, 9):
    p = B + t * (C - B)
    ax.annotate("", (p[0], p[1] + 0.05), xytext=(p[0], p[1] + 0.55),
                arrowprops=dict(arrowstyle="->", color=cor_c, lw=1))
ax.text(1.0, 2.75, "peso próprio 12 kN/m\n(por metro de barra)", color=cor_c, fontsize=10, ha="center")
# resultantes
ax.annotate("", (2, 1.5), xytext=(2, 2.35), arrowprops=dict(arrowstyle="-|>", color=cor_c, lw=2, ls="--"))
ax.text(2.1, 2.05, "60 kN", color=cor_c, fontsize=10)
ax.annotate("", (0.35, 0.9), xytext=(0.35, 1.7), arrowprops=dict(arrowstyle="-|>", color=cor_c, lw=2, ls="--"))
ax.text(0.42, 1.25, "36 kN\n(sobre AB)", color=cor_c, fontsize=9)

# reacoes nas bielas
ax.annotate("", (A[0] + 0.25, A[1] + 1.35), xytext=(A[0] + 0.25, A[1] + 0.25),
            arrowprops=dict(arrowstyle="-|>", color=cor_r, lw=2))
ax.text(A[0] + 0.35, A[1] + 1.0, f"V$_A$ = {fmt(float(VA))} kN", color=cor_r, fontsize=11)
ax.text(A[0] - 1.6, A[1] + 0.2, "H$_A$ = 0", color=cor_r, fontsize=11)
ax.annotate("", (C[0] - 0.25, C[1] + 1.35), xytext=(C[0] - 0.25, C[1] + 0.25),
            arrowprops=dict(arrowstyle="-|>", color=cor_r, lw=2))
ax.text(C[0] - 1.8, C[1] + 1.0, f"V$_C$ = {fmt(float(VC))} kN", color=cor_r, fontsize=11)

# cotas
ax.annotate("", (0, -0.6), xytext=(4, -0.6), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(2, -0.55, "4 m", ha="center", va="bottom", fontsize=10)
ax.annotate("", (4.6, 0), xytext=(4.6, 3), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(4.65, 1.5, "3 m", va="center", fontsize=10)
ax.text(2.25, 1.0, "BC = 5 m", fontsize=9, rotation=36.87, ha="center")
ax.set_xlim(-1.9, 5.2)
ax.set_ylim(-0.9, 4.6)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex14-estrutura.png"), dpi=160)
plt.close(fig)


# ---------- figura 2: N, V, M sobre a geometria ----------
def desenhar(ax, P0, P1, f, L, esc, cor, lado=1.0):
    """f(s) desenhado perpendicular a barra P0->P1, lado=+1 usa a normal a esquerda do percurso"""
    t = (P1 - P0) / np.linalg.norm(P1 - P0)
    n = np.array([-t[1], t[0]]) * lado
    ss = np.linspace(0, float(L), 200)
    vals = np.array([float(f(F(s).limit_denominator(10000))) for s in ss])
    base = np.array([P0 + s * t for s in ss])
    curva = base + np.outer(vals * esc, n)
    poly = np.vstack([base, curva[::-1]])
    ax.fill(poly[:, 0], poly[:, 1], color=cor, alpha=0.2, lw=0)
    ax.plot(curva[:, 0], curva[:, 1], color=cor, lw=2)
    ax.plot([base[0, 0], curva[0, 0]], [base[0, 1], curva[0, 1]], color=cor, lw=2)
    ax.plot([base[-1, 0], curva[-1, 0]], [base[-1, 1], curva[-1, 1]], color=cor, lw=2)
    return t, n


def ponto(P0, P1, s, v, esc, lado=1.0, extra=0.0):
    t = (P1 - P0) / np.linalg.norm(P1 - P0)
    n = np.array([-t[1], t[0]]) * lado
    return P0 + s * t + n * (v * esc + np.sign(v if v != 0 else 1) * extra)


fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
for ax, tit in zip(axs, ["Esforço normal N (kN)", "Esforço cortante V (kN)", "Momento fletor M (kN.m)"]):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(tit, fontsize=15, fontweight="bold")
    chapa(ax, lw=1.6, cor="#444")
    ax.text(A[0] + 0.15, A[1] + 0.15, "A", fontsize=12)
    ax.text(B[0] + 0.15, B[1] - 0.3, "B", fontsize=12)
    ax.text(C[0] + 0.15, C[1] + 0.1, "C", fontsize=12)
    ax.set_xlim(-2.4, 5.4)
    ax.set_ylim(-1.6, 4.2)

kw = dict(fontsize=13, fontweight="bold", ha="center", va="center")

# N
aN = axs[0]
cN = "#7d3c98"
eN = 0.022
desenhar(aN, A, B, NAB, LAB, eN, cN, lado=-1.0)  # para o lado de -x
desenhar(aN, B, C, NBC, LBC, eN, cN, lado=1.0)
aN.text(-float(NAB(0)) * eN - 0.3, 3.0, "66", **kw, color=cN)
aN.text(-float(NAB(3)) * eN - 0.3, 0.0, "30", **kw, color=cN)
aN.text(-0.75, 1.5, "+", fontsize=18, color=cN, ha="center", va="center")
p = ponto(B, C, 0, float(NBC(0)), eN); aN.text(p[0] + 0.1, p[1] - 0.3, "−18", **kw, color=cN)
p = ponto(B, C, 5, float(NBC(5)), eN); aN.text(p[0] - 0.2, p[1] + 0.2, "18", **kw, color=cN)
p = ponto(B, C, 2.5, 0, eN); aN.text(p[0] + 0.2, p[1] - 0.25, "0", **kw, color=cN)
p = ponto(B, C, 1.2, -0.3, 1); aN.text(p[0], p[1], "−", fontsize=18, color=cN, ha="center", va="center")
p = ponto(B, C, 3.8, 0.35, 1); aN.text(p[0], p[1], "+", fontsize=18, color=cN, ha="center", va="center")

# V
aV = axs[1]
cV = "#2471a3"
eV = 0.03
desenhar(aV, B, C, VBC, LBC, eV, cV, lado=1.0)
p = ponto(B, C, 0, float(VBC(0)), eV); aV.text(p[0] - 0.2, p[1] + 0.15, "24", **kw, color=cV)
p = ponto(B, C, 5, float(VBC(5)), eV); aV.text(p[0] + 0.25, p[1] - 0.15, "−24", **kw, color=cV)
p = ponto(B, C, 2.5, 0, eV); aV.text(p[0] + 0.2, p[1] - 0.25, "0", **kw, color=cV)
p = ponto(B, C, 1.1, 0.35, 1); aV.text(p[0], p[1], "+", fontsize=18, color=cV, ha="center", va="center")
p = ponto(B, C, 3.9, -0.35, 1); aV.text(p[0], p[1], "−", fontsize=18, color=cV, ha="center", va="center")
aV.text(-0.25, 1.5, "V = 0", fontsize=10, color=cV, ha="right", va="center", fontweight="bold")

# M: positivo traciona a fibra de baixo de BC, desenhado embaixo (lado oposto a normal)
aM = axs[2]
cM = "#b03a2e"
eM = 0.03
desenhar(aM, B, C, MBC, LBC, eM, cM, lado=-1.0)
p = ponto(B, C, 2.5, float(MBC(F(5, 2))) + 30, eM, lado=-1.0); aM.text(p[0], p[1], "30\n(meio de BC)", **kw, color=cM)
p = ponto(B, C, 1.25, float(MBC(F(5, 4))) + 18, eM, lado=-1.0); aM.text(p[0], p[1], "22,5", **kw, color=cM)
p = ponto(B, C, 3.75, float(MBC(F(15, 4))) + 14, eM, lado=-1.0); aM.text(p[0], p[1], "22,5", **kw, color=cM)
aM.text(B[0] + 0.45, B[1] + 0.05, "0", **kw, color=cM)
aM.text(C[0] + 0.05, C[1] - 0.35, "0", **kw, color=cM)
aM.text(-0.25, 1.5, "M = 0", fontsize=10, color=cM, ha="right", va="center", fontweight="bold")
aM.text(1.4, -1.45, "desenhado do lado tracionado (embaixo de BC)", fontsize=9, ha="center")

fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex14-diagramas.png"), dpi=160)
plt.close(fig)
print("figuras salvas em", SAIDA)
