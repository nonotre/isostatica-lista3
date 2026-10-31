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

# exercicio 07: origem no canto A, x para a direita, y para cima (m)
T, A, B, C, D, E = (0, 4), (0, 0), (2, 0), (4, 0), (4, -2), (8, 0)
q = F(10)    # kN/m horizontal para a direita no pilar AT
P = F(10)    # kN para baixo em B
H = F(5)     # kN para a esquerda em D
M0 = F(80)   # kN.m anti-horario em D

# cargas como (ponto de aplicacao, Fx, Fy)
Q = q * 4    # resultante da distribuida, no meio do pilar
forcas = [((0, 2), Q, 0), (B, 0, -P), (D, -H, 0)]
binarios = [M0]  # anti-horario positivo


def momento(ponto, fx, fy, ref):
    rx, ry = ponto[0] - ref[0], ponto[1] - ref[1]
    return rx * fy - ry * fx  # anti-horario positivo


HE = -sum(f[1] for f in forcas)
VE = -sum(f[2] for f in forcas)
ME = -(sum(momento(p, fx, fy, E) for p, fx, fy in forcas) + sum(binarios))
print("HE =", HE, "(positivo para a direita)")
print("VE =", VE, "(positivo para cima)")
print("ME =", ME, "(positivo anti-horario)")

# conferencia: momentos em A com as reacoes
soma = sum(momento(p, fx, fy, A) for p, fx, fy in forcas) + sum(binarios) + momento(E, HE, VE, A) + ME
print("conferencia sum M_A =", soma)


# esforcos por barra, s medido a partir do inicio do percurso
def pilar(s):  # T -> A, s de 0 a 4 (de cima para baixo)
    return 0.0, 10 * s, 5 * s ** 2  # N, V, M


def pendural(t):  # D -> C, t de 0 a 2 (de baixo para cima)
    return 0.0, 5.0, -80 + 5 * t


def viga(x):  # A -> E, x de 0 a 8
    n = -40.0 if x < 4 else -35.0
    v = 0.0 if x < 2 else -10.0
    m = 80.0
    if x > 2:
        m -= 10 * (x - 2)
    if x > 4:
        m -= 70
    return n, v, m


eps = 1e-9
print("\npilar T->A")
for s in [0, 2, 4]:
    print(f"  s={s}  N={pilar(s)[0]:7.2f}  V={pilar(s)[1]:7.2f}  M={pilar(s)[2]:7.2f}")
print("pendural D->C")
for t in [0, 2]:
    print(f"  t={t}  N={pendural(t)[0]:7.2f}  V={pendural(t)[1]:7.2f}  M={pendural(t)[2]:7.2f}")
print("viga A->E")
for x in [0, 2, 4, 8]:
    a, b = viga(max(x - eps, 0)), viga(min(x + eps, 8))
    print(f"  x={x}  N-={a[0]:7.2f} N+={b[0]:7.2f}  V-={a[1]:7.2f} V+={b[1]:7.2f}  M-={a[2]:7.2f} M+={b[2]:7.2f}")
# equilibrio dos nos
print("\nno A: M pilar =", pilar(4)[2], " M viga =", viga(0)[2])
print("no C: M viga esq =", viga(4 - eps)[2], " M viga dir =", viga(4 + eps)[2], " M pendural =", pendural(2)[2])


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("−" if v < -1e-6 else "") + s


# ---------- desenho ----------
def base_portico(ax, lw=3):
    ax.plot([T[0], A[0], E[0]], [T[1], A[1], E[1]], color="black", lw=lw, solid_capstyle="butt", zorder=4)
    ax.plot([C[0], D[0]], [C[1], D[1]], color="black", lw=lw, zorder=4)
    # engaste em E
    ax.plot([E[0], E[0]], [-0.45, 0.45], color="black", lw=2, zorder=4)
    for y in np.linspace(-0.4, 0.4, 7):
        ax.plot([E[0], E[0] + 0.18], [y, y + 0.14], color="black", lw=0.8)


def nomes(ax, deslocs=None):
    d = {"T": (0.12, 0.05), "A": (-0.3, -0.35), "B": (0.05, 0.12), "C": (0.1, 0.12),
         "D": (0.12, -0.25), "E": (0.25, 0.5)}
    if deslocs:
        d.update(deslocs)
    for nome, p in zip("TABCDE", [T, A, B, C, D, E]):
        ax.text(p[0] + d[nome][0], p[1] + d[nome][1], nome, fontsize=12, fontweight="bold", zorder=6)


azul, verm = "#1f5fbf", "#c0392b"

# figura 1: estrutura com cargas e reacoes
fig, ax = plt.subplots(figsize=(9.5, 6.4))
ax.set_aspect("equal")
ax.axis("off")
base_portico(ax)
nomes(ax)
# distribuida no pilar
ax.plot([-1.1, -1.1], [0, 4], color=azul, lw=1)
for y in np.linspace(0, 4, 9):
    ax.annotate("", (-0.05, y), xytext=(-1.1, y), arrowprops=dict(arrowstyle="->", color=azul, lw=1))
ax.text(-1.25, 2.1, "10 kN/m", color=azul, fontsize=11, ha="right")
# 10 kN em B
ax.annotate("", (B[0], 0.05), xytext=(B[0], 1.5), arrowprops=dict(arrowstyle="-|>", color=azul, lw=2.2))
ax.text(B[0] + 0.12, 1.2, "10 kN", color=azul, fontsize=11)
# 5 kN em D
ax.annotate("", (D[0] - 1.3, D[1]), xytext=(D[0] - 0.05, D[1]), arrowprops=dict(arrowstyle="-|>", color=azul, lw=2.2))
ax.text(D[0] - 1.25, D[1] + 0.12, "5 kN", color=azul, fontsize=11)
# 80 kN.m anti-horario em D
ax.add_patch(Arc(D, 0.8, 0.8, theta1=180, theta2=40, color=azul, lw=1.8))
ax.annotate("", (D[0] + 0.30, D[1] + 0.28), xytext=(D[0] + 0.38, D[1] + 0.1),
            arrowprops=dict(arrowstyle="-|>", color=azul, lw=1.8))
ax.text(D[0] + 0.5, D[1] - 0.15, "80 kN.m", color=azul, fontsize=11)
# reacoes em E
ax.annotate("", (E[0] + 0.3, -0.85), xytext=(E[0] + 1.6, -0.85), arrowprops=dict(arrowstyle="-|>", color=verm, lw=2))
ax.text(E[0] + 0.5, -1.2, "H$_E$ = 35 kN", color=verm, fontsize=10)
ax.annotate("", (E[0] + 0.55, 0.0), xytext=(E[0] + 0.55, -0.7), arrowprops=dict(arrowstyle="-|>", color=verm, lw=2))
ax.text(E[0] + 0.65, -0.55, "V$_E$ = 10 kN", color=verm, fontsize=10)
ax.add_patch(Arc(E, 1.6, 1.6, theta1=-30, theta2=80, color=verm, lw=1.8))
ax.annotate("", (E[0] + 0.69, -0.4), xytext=(E[0] + 0.76, -0.25), arrowprops=dict(arrowstyle="-|>", color=verm, lw=1.8))
ax.text(E[0] + 0.45, 0.85, "M$_E$ = 50 kN.m (horário)", color=verm, fontsize=10)
# cotas
for a, b, txt in [(0, 2, "2 m"), (2, 4, "2 m"), (4, 8, "4 m")]:
    ax.annotate("", (a, -2.7), xytext=(b, -2.7), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((a + b) / 2, -2.65, txt, ha="center", va="bottom", fontsize=9)
for a, b, txt in [(0, 4, "4 m"), (-2, 0, "2 m")]:
    ax.annotate("", (10.6, a), xytext=(10.6, b), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(10.7, (a + b) / 2, txt, va="center", fontsize=9)
ax.set_xlim(-2.6, 11.2)
ax.set_ylim(-3.0, 4.5)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex07-estrutura.png"), dpi=160)
plt.close(fig)


# figura 2: N, V e M sobre o portico
# cada barra: inicio, fim, funcao (N,V,M) do comprimento percorrido
barras = [
    ("pilar", T, A, pilar, [(0, 4)]),
    ("viga", A, E, viga, [(0, 2), (2, 4), (4, 8)]),
    ("pendural", D, C, pendural, [(0, 2)]),
]


def desenha(ax, idx, escala, cor, lado_m=False):
    for nome, p0, p1, f, trechos in barras:
        p0, p1 = np.array(p0, float), np.array(p1, float)
        L = np.linalg.norm(p1 - p0)
        d = (p1 - p0) / L
        nl = np.array([-d[1], d[0]])  # normal esquerda do percurso
        n = -nl if lado_m else nl     # M positivo vai para a normal direita (fibra de baixo)
        for a, b in trechos:
            ss = np.linspace(a + eps, b - eps, 120)
            vals = np.array([f(s)[idx] for s in ss])
            eixo_pts = p0 + np.outer(ss, d)
            curva = eixo_pts + np.outer(vals * escala, n)
            poly = np.vstack([eixo_pts[0], curva, eixo_pts[-1]])
            ax.add_patch(Polygon(poly, closed=True, fc=cor, alpha=0.2, ec="none"))
            ax.plot(np.r_[eixo_pts[0, 0], curva[:, 0], eixo_pts[-1, 0]],
                    np.r_[eixo_pts[0, 1], curva[:, 1], eixo_pts[-1, 1]], color=cor, lw=1.8)


def txt(ax, x, y, s, cor="black", ha="center", va="center", size=10):
    ax.text(x, y, s, color=cor, ha=ha, va=va, fontsize=size, fontweight="bold", zorder=7)


def painel(titulo):
    fig, ax = plt.subplots(figsize=(10, 6.6))
    ax.set_aspect("equal")
    ax.axis("off")
    base_portico(ax, lw=2.4)
    ax.set_title(titulo, fontsize=13, fontweight="bold", loc="left")
    ax.set_xlim(-2.4, 9.2)
    ax.set_ylim(-2.7, 4.4)
    return fig, ax


def salvar(fig, nome):
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, nome), dpi=160)
    plt.close(fig)


def seta(ax, alvo, pos, s, cor, ha="center"):
    ax.annotate(s, alvo, xytext=pos, color=cor, ha=ha, va="center", fontsize=11, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=cor, lw=0.8), zorder=7)


# N
fig, ax = painel("Esforço normal N (kN), tração positiva")
cn = "#7d3c98"
desenha(ax, 0, 0.02, cn)
nomes(ax, {"A": (-0.35, 0.15), "B": (0.05, 0.15), "C": (0.1, 0.15), "E": (0.25, 0.3)})
txt(ax, 3.0, -0.45, "−40 (−)", cn, size=11)
txt(ax, 6.0, -0.38, "−35 (−)", cn, size=11)
txt(ax, -0.3, 2.0, "N = 0", cn, ha="right", size=11)
txt(ax, 3.85, -1.3, "N = 0", cn, ha="right", size=11)
txt(ax, 0.1, -1.35, "(−) compressão", cn, ha="left", size=10)
salvar(fig, "ex07-diagrama-N.png")

# V
fig, ax = painel("Esforço cortante V (kN)")
cv = "#2471a3"
desenha(ax, 1, 0.03, cv)
nomes(ax, {"A": (-0.4, -0.35), "T": (-0.4, 0.05), "B": (0.05, 0.15), "C": (0.1, 0.15), "E": (0.25, 0.3)})
txt(ax, 0.12, 4.0, "0", cv, ha="left", size=11)
txt(ax, 1.3, 0.25, "40", cv, ha="left", size=11)
txt(ax, 0.45, 1.6, "(+)", cv, size=11)
txt(ax, 1.0, -0.3, "0", cv, size=11)
txt(ax, 3.0, -0.6, "−10 (−)", cv, size=11)
txt(ax, 6.0, -0.6, "−10 (−)", cv, size=11)
txt(ax, 3.75, -1.0, "+5 (+)", cv, ha="right", size=11)
txt(ax, 4.6, -1.5, "percurso e sentido positivo de V:\npilar T→A, + para a direita\nviga A→E, + para cima\npendural D→C, + para a esquerda",
    "black", ha="left", va="top", size=9.5)
salvar(fig, "ex07-diagrama-V.png")

# M (lado tracionado)
fig, ax = painel("Momento fletor M (kN.m), desenhado do lado tracionado")
cm = "#b03a2e"
desenha(ax, 2, 0.012, cm, lado_m=True)
nomes(ax, {"A": (0.12, 0.12), "T": (0.12, 0.05), "B": (0.05, 0.12), "C": (0.1, 0.12), "E": (0.25, 0.3)})
txt(ax, -0.12, 4.0, "0", cm, ha="right", size=11)
txt(ax, -1.0, 0.25, "80", cm, ha="right", size=11)
txt(ax, -0.15, -2.0 / 3 * 1.0 - 0.3, "80", cm, ha="right", size=11)
txt(ax, 2.0, -1.2, "60", cm, size=11)
seta(ax, (3.98, -0.72), (5.0, -1.0), "60", cm)
seta(ax, (3.16, 0.0), (2.6, 0.6), "70", cm)
seta(ax, (3.04, -2.0), (2.4, -2.3), "80", cm)
txt(ax, 4.1, 0.38, "10", cm, ha="left", size=11)
txt(ax, 7.85, 0.95, "50", cm, ha="right", size=11)
salvar(fig, "ex07-diagrama-M.png")
print("figuras salvas em", SAIDA)
