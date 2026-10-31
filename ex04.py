from fractions import Fraction as F
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Polygon

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "figuras")
os.makedirs(SAIDA, exist_ok=True)

# exercicio 04: portico em L engastado na base
# A (0,4) ponta livre, B (2,4) inicio da carga, C (6,4) no, D (6,2) forca de 20 kN, E (6,0) engaste
A, B, C, D, E = (0, 4), (2, 4), (6, 4), (6, 2), (6, 0)
P1, q, P2 = 15, 10, 20  # kN para baixo em A, kN/m de B a C, kN para a esquerda em D

# reacoes no engaste (forcas para cima e para a direita positivas, momento anti-horario positivo)
R = q * (C[0] - B[0])              # resultante da distribuida
xR = F(B[0] + C[0], 2)             # posicao da resultante
HE = F(P2)                          # sum Fx: HE - 20 = 0
VE = F(P1 + R)                      # sum Fy: VE - 15 - 40 = 0
# sum M_E = 0: ME + momentos das cargas em torno de E = 0
mom_cargas = P1 * (E[0] - A[0]) + R * (E[0] - xR) + P2 * (D[1] - E[1])  # todos anti-horarios
ME = -mom_cargas

print("HE =", HE, "kN (para a direita)")
print("VE =", VE, "kN (para cima)")
print("ME =", ME, "kN.m (negativo = horario)")

# conferencia global de momentos em torno de A
# HE para a direita aplicado 4 m abaixo de A gira anti-horario: +HE*4
# a forca de 20 kN para a esquerda 2 m abaixo de A gira horario: -20*2
somaA = VE * 6 + HE * 4 - R * (xR - 0) - P2 * 2 + ME
print("conferencia sum M_A =", somaA)


# esforcos na barra AC (x de A para C)
def V_viga(x):
    return -P1 - q * max(0, x - 2)


def M_viga(x):
    return -P1 * x - q * max(0, x - 2) ** 2 / 2


def N_viga(x):
    return 0.0


# esforcos no pilar CE (s de C para E, para baixo)
def N_pilar(s):
    return -float(VE)


def V_pilar(s):
    return 0.0 if s < 2 else -P2


def M_pilar(s):
    return float(M_viga(6)) - P2 * max(0, s - 2)


eps = 1e-9
print("barra AC")
for x in [0, 2, 4, 6]:
    print(f"  x={x}  N={N_viga(x):7.2f}  V-={V_viga(x - eps):7.2f}  V+={V_viga(x + eps):7.2f}  M={M_viga(x):8.2f}")
print("barra CE")
for s in [0, 2, 4]:
    print(f"  s={s}  N={N_pilar(s):7.2f}  V-={V_pilar(s - eps):7.2f}  V+={V_pilar(s + eps):7.2f}  M={M_pilar(s):8.2f}")
print("no C: M viga =", M_viga(6), " M pilar =", M_pilar(0))


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("−" if v < -1e-6 else "") + s


AZUL, VERM = "#1f5fbf", "#c0392b"


def estrutura(ax, lw=3, cor="black"):
    ax.plot([A[0], C[0], E[0]], [A[1], C[1], E[1]], color=cor, lw=lw, solid_capstyle="round", zorder=3)
    ax.plot([E[0] - 0.45, E[0] + 0.45], [0, 0], color=cor, lw=1.5)
    for i in np.linspace(E[0] - 0.4, E[0] + 0.45, 7):
        ax.plot([i, i - 0.13], [0, -0.16], color=cor, lw=0.8)


# ---------- figura 1: estrutura e reacoes ----------
fig, ax = plt.subplots(figsize=(9, 7))
ax.set_aspect("equal")
ax.axis("off")
ax.set_xlim(-1.2, 9.6)
ax.set_ylim(-1.9, 6.3)
estrutura(ax)
for p, n, dx, dy in [(A, "A", -0.1, -0.45), (B, "B", -0.1, -0.45), (C, "C", 0.15, -0.45),
                     (D, "D", -0.45, 0.1), (E, "E", -0.5, 0.15)]:
    ax.text(p[0] + dx, p[1] + dy, n, fontsize=13)
# carga distribuida
ax.plot([2, 6], [5.0, 5.0], color=AZUL, lw=1)
for x in np.linspace(2, 6, 9):
    ax.annotate("", (x, 4.05), xytext=(x, 5.0), arrowprops=dict(arrowstyle="->", color=AZUL, lw=1))
ax.text(3.5, 5.15, "10 kN/m", color=AZUL, fontsize=12)
# 15 kN
ax.annotate("", (0, 4.05), xytext=(0, 5.6), arrowprops=dict(arrowstyle="-|>", color=AZUL, lw=2.2))
ax.text(0.15, 5.3, "15 kN", color=AZUL, fontsize=12)
# 20 kN para a esquerda em D
ax.annotate("", (6.05, 2), xytext=(7.6, 2), arrowprops=dict(arrowstyle="-|>", color=AZUL, lw=2.2))
ax.text(6.6, 2.15, "20 kN", color=AZUL, fontsize=12)
# reacoes
ax.annotate("", (6, -0.25), xytext=(6, -1.5), arrowprops=dict(arrowstyle="-|>", color=VERM, lw=2.2))
ax.text(6.15, -1.35, "V$_E$ = 55 kN", color=VERM, fontsize=11)
ax.annotate("", (5.95, 0.35), xytext=(4.6, 0.35), arrowprops=dict(arrowstyle="-|>", color=VERM, lw=2.2))
ax.text(4.0, 0.5, "H$_E$ = 20 kN", color=VERM, fontsize=11)
ax.add_patch(Arc((6, 0), 1.6, 1.6, theta1=-30, theta2=80, color=VERM, lw=1.8))
ang = np.radians(-30)
ax.annotate("", (6 + 0.8 * np.cos(ang), 0.8 * np.sin(ang)),
            xytext=(6 + 0.8 * np.cos(ang + 0.35), 0.8 * np.sin(ang + 0.35)),
            arrowprops=dict(arrowstyle="-|>", color=VERM, lw=1.8))
ax.text(6.95, 0.55, "M$_E$ = 210 kN.m\n(horário)", color=VERM, fontsize=11)
# cotas
for a, b in [(0, 2), (2, 6)]:
    ax.annotate("", (a, -1.75), xytext=(b, -1.75), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((a + b) / 2, -1.7, f"{b - a} m", ha="center", va="bottom", fontsize=10)
for a, b in [(0, 2), (2, 4)]:
    ax.annotate("", (9.0, a), xytext=(9.0, b), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(9.1, (a + b) / 2, f"{b - a} m", va="center", fontsize=10)
for y in [0, 2, 4]:
    ax.plot([6.3 if y != 2 else 7.8, 9.2], [y, y], color="#999", lw=0.5)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex04-estrutura.png"), dpi=160)
plt.close(fig)


# ---------- figura 2: N, V, M sobre o portico ----------
def desenha(ax, p0, p1, f, comp, n, k, cor, cortes):
    """desenha f(s) sobre a barra p0->p1, deslocado k*f na direcao n"""
    p0, p1, n = np.array(p0, float), np.array(p1, float), np.array(n, float)
    t = (p1 - p0) / comp
    for a, b in zip(cortes[:-1], cortes[1:]):
        ss = np.linspace(a + eps, b - eps, 120)
        base = np.array([p0 + t * s for s in ss])
        vals = np.array([f(s) for s in ss])
        pts = base + np.outer(vals * k, n)
        ax.plot(pts[:, 0], pts[:, 1], color=cor, lw=2, zorder=4)
        poly = np.vstack([base, pts[::-1]])
        ax.add_patch(Polygon(poly, closed=True, color=cor, alpha=0.18, lw=0))
        for s in [a + eps, b - eps]:
            q0 = p0 + t * s
            ax.plot([q0[0], q0[0] + k * f(s) * n[0]], [q0[1], q0[1] + k * f(s) * n[1]], color=cor, lw=1.4)


def txt(ax, x, y, s, cor="black", ha="center", va="center", size=11):
    ax.text(x, y, s, color=cor, ha=ha, va=va, fontsize=size, fontweight="bold")


def quadro(ax, titulo):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.0, 9.2)
    ax.set_ylim(-0.8, 5.4)
    ax.set_title(titulo, loc="left", fontsize=12, fontweight="bold")
    estrutura(ax, lw=2.2, cor="#333")
    for p, nme, dx, dy in [(A, "A", -0.35, -0.35), (B, "B", -0.1, -0.45), (C, "C", 0.15, -0.45),
                           (D, "D", 0.15, 0.0), (E, "E", -0.5, 0.15)]:
        ax.text(p[0] + dx, p[1] + dy, nme, fontsize=11, color="#333")


fig = plt.figure(figsize=(14, 13))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.15])
aN, aV = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
aM = fig.add_subplot(gs[1, :])

# N: positivo do lado esquerdo do percurso (viga: em cima, pilar: a direita)
quadro(aN, "Esforço normal N (kN)")
kN_ = 1.6 / 55
desenha(aN, A, C, N_viga, 6, (0, 1), kN_, "#7d3c98", [0, 6])
desenha(aN, C, E, N_pilar, 4, (1, 0), kN_, "#7d3c98", [0, 4])
txt(aN, 3, 4.35, "N = 0 em AC")
txt(aN, 4.3, 3.75, "−55", "#7d3c98", ha="right")
txt(aN, 4.3, 0.25, "−55", "#7d3c98", ha="right")
txt(aN, 5.2, 2.0, "(−)\ncompressão", "#7d3c98", ha="center", size=10)

# V: positivo do lado esquerdo do percurso (viga: em cima, pilar: a direita)
quadro(aV, "Esforço cortante V (kN)")
kV = 1.8 / 55
desenha(aV, A, C, V_viga, 6, (0, 1), kV, "#2471a3", [0, 6])
desenha(aV, C, E, V_pilar, 4, (1, 0), kV, "#2471a3", [0, 2, 4])
txt(aV, 0.0, 4 + kV * -15 - 0.25, "−15", "#2471a3", ha="left")
txt(aV, 2.0, 4 + kV * -15 - 0.3, "−15", "#2471a3")
txt(aV, 6.15, 4 + kV * -55 + 0.25, "−55", "#2471a3", ha="left")
txt(aV, 3.6, 3.15, "(−)", "#2471a3")
txt(aV, 6.4, 3.0, "V = 0 em CD", "#2471a3", ha="left", size=10)
txt(aV, 6 + kV * -20 - 0.1, 1.7, "−20", "#2471a3", ha="right")
txt(aV, 6 + kV * -20 - 0.1, 0.25, "−20", "#2471a3", ha="right")
txt(aV, 4.6, 1.0, "(−)", "#2471a3")

# M: desenhado do lado tracionado. positivo traciona a fibra interna (viga: embaixo, pilar: esquerda)
quadro(aM, "Momento fletor M (kN.m), lado tracionado")
aM.set_xlim(-1.0, 9.6)
aM.set_ylim(-0.8, 6.6)
kM = 1.9 / 210
desenha(aM, A, C, M_viga, 6, (0, -1), kM, "#b03a2e", [0, 6])
desenha(aM, C, E, M_pilar, 4, (-1, 0), kM, "#b03a2e", [0, 4])
txt(aM, -0.25, 4.25, "0", "#b03a2e")
txt(aM, 2.0, 4 + 30 * kM + 0.3, "−30", "#b03a2e")
txt(aM, 4.0, 4 + 80 * kM + 0.3, "−80", "#b03a2e")
txt(aM, 5.7, 4 + 170 * kM + 0.3, "−170", "#b03a2e", ha="right")
txt(aM, 6 + 170 * kM + 0.15, 3.75, "−170", "#b03a2e", ha="left")
txt(aM, 6 + 170 * kM + 0.15, 2.0, "−170", "#b03a2e", ha="left")
txt(aM, 6 + 210 * kM + 0.15, 0.3, "−210", "#b03a2e", ha="left")
txt(aM, 3.0, 4.35, "tração em cima", "#b03a2e", size=9)
txt(aM, 8.0, 1.2, "tração\nface externa", "#b03a2e", ha="left", size=9)

fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex04-diagramas.png"), dpi=140)
plt.close(fig)
print("figuras salvas em", SAIDA)
