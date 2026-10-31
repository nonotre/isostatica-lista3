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

# exercicio 05: origem em A, X para a direita, Y para cima (m)
A = (0, 0)
C = (0, F(5, 2))
E = (0, 4)
D = (4, F(5, 2))
B = (4, 0)
qh = 40  # kN/m horizontal para a direita no pilar AE
qv = 20  # kN/m vertical para baixo na viga CD
L = 4
hC = F(5, 2)
hE = 4

# resultantes
Rh = qh * hE          # 160 kN em y = 2
Rv = qv * L           # 80 kN em x = 2

# reacoes: VA e VB verticais (apoios moveis), HD horizontal (biela em D)
HD = -Rh                                       # soma Fx = 0
# soma de momentos em A, anti-horario positivo: VB*4 - Rv*2 - Rh*2 + (-yD*HD) = 0
VB = (Rv * 2 + Rh * F(hE, 2) + D[1] * HD) / L
VA = Rv - VB

print("HD =", HD, "(negativo: para a esquerda)")
print("VA =", VA, float(VA))
print("VB =", VB, float(VB))
print("conferencia Fx:", Rh + HD, " Fy:", VA + VB - Rv)
mom = VB * 4 - Rv * 2 - Rh * 2 - D[1] * HD
print("conferencia M_A:", mom)


# esforcos por barra (s = distancia a partir do inicio do percurso)
def AC(s):  # A -> C, s = y
    return dict(N=-float(VA), V=-qh * s, M=-qh * s ** 2 / 2)


def CE(s):  # C -> E, y = 2,5 + s
    r = hE - float(hC) - s
    return dict(N=0.0, V=qh * r, M=-qh * r ** 2 / 2)


def CD(s):  # C -> D, s = x
    mh = qh * (hE ** 2 / 2 - float(hC) * hE)  # momento horario da carga do pilar em torno de C
    return dict(N=float(HD), V=float(VA) - qv * s, M=float(VA) * s + mh - qv * s ** 2 / 2)


def DB(s):  # D -> B
    return dict(N=-float(VB), V=0.0, M=0.0)


for nome, f, comp in [("AC", AC, 2.5), ("CE", CE, 1.5), ("CD", CD, 4), ("DB", DB, 2.5)]:
    for s in sorted(set([0, comp / 2, comp] + ([2, 3] if nome == "CD" else []))):
        v = f(s)
        print(f"{nome} s={s:4}  N={v['N']:8.2f}  V={v['V']:8.2f}  M={v['M']:8.2f}")

# equilibrio de momentos no no C (momento que cada barra aplica no no, anti-horario positivo)
print("no C: M_AC(topo) =", AC(2.5)["M"], " M_CE(base) =", CE(0)["M"], " M_CD(C) =", CD(0)["M"])
print("     soma |M_CE| + |M_CD| =", abs(CE(0)["M"]) + abs(CD(0)["M"]))


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("−" if v < -1e-6 else "") + s


# barras: (inicio, fim, funcao, lado da fibra tracejada)
barras = [
    ((0, 0), (0, 2.5), AC, (1, 0)),
    ((0, 2.5), (0, 4), CE, (1, 0)),
    ((0, 2.5), (4, 2.5), CD, (0, -1)),
    ((4, 2.5), (4, 0), DB, (-1, 0)),
]
BIELA = ((4, 2.5), (5.3, 2.5))


def desenhar_portico(ax, cor="black", lw=3, biela=True):
    for p, q, _, _ in barras:
        ax.plot([p[0], q[0]], [p[1], q[1]], color=cor, lw=lw, solid_capstyle="round", zorder=3)
    if biela:
        ax.plot([BIELA[0][0], BIELA[1][0]], [2.5, 2.5], color=cor, lw=1.2, zorder=3)
        ax.add_patch(Circle(BIELA[1], 0.07, fc="white", ec=cor, lw=1.2, zorder=4))
        ax.add_patch(Circle((4.07, 2.5), 0.07, fc="white", ec=cor, lw=1.2, zorder=4))
        xw = BIELA[1][0] + 0.07
        ax.plot([xw, xw], [2.15, 2.85], color=cor, lw=1.4)
        for yy in np.linspace(2.2, 2.85, 7):
            ax.plot([xw, xw + 0.12], [yy, yy - 0.08], color=cor, lw=0.8)
    for x in (0, 4):
        ax.add_patch(Circle((x, -0.07), 0.07, fc="white", ec=cor, lw=1.2, zorder=4))
        ax.add_patch(Polygon([[x, -0.14], [x - 0.22, -0.45], [x + 0.22, -0.45]], closed=True, fill=False, lw=1.2, ec=cor))
        ax.plot([x - 0.35, x + 0.35], [-0.45, -0.45], color=cor, lw=1.2)
        ax.plot([x - 0.35, x + 0.35], [-0.55, -0.55], color=cor, lw=1.2)
        for i in np.linspace(x - 0.3, x + 0.35, 7):
            ax.plot([i, i - 0.1], [-0.55, -0.67], color=cor, lw=0.7)


# ---------- figura 1: estrutura, cargas e reacoes ----------
fig, ax = plt.subplots(figsize=(9, 7.2))
ax.set_aspect("equal")
ax.axis("off")
desenhar_portico(ax)
azul = "#1f5fbf"
# carga horizontal no pilar
ax.plot([-0.9, -0.9], [0, 4], color=azul, lw=1)
for y in np.linspace(0, 4, 17):
    ax.annotate("", (-0.04, y), xytext=(-0.9, y), arrowprops=dict(arrowstyle="->", color=azul, lw=1))
ax.text(-1.0, 1.25, "40 kN/m", color=azul, fontsize=12, ha="right")
# carga vertical na viga
ax.plot([0, 4], [3.3, 3.3], color=azul, lw=1)
for x in np.linspace(0.05, 4, 15):
    ax.annotate("", (x, 2.56), xytext=(x, 3.3), arrowprops=dict(arrowstyle="->", color=azul, lw=1))
ax.text(2, 3.4, "20 kN/m", color=azul, fontsize=12, ha="center")
# nomes
for (x, y), n, dx, dy in [(A, "A", 0.15, 0.1), (C, "C", 0.12, -0.3), (E, "E", 0.12, -0.15),
                          (D, "D", -0.35, -0.3), (B, "B", -0.35, 0.1)]:
    ax.text(float(x) + dx, float(y) + dy, n, fontsize=13, fontweight="bold")
# reacoes
verm = "#c0392b"
for x, v in [(0, VA), (4, VB)]:
    ax.annotate("", (x, -0.75), xytext=(x, -1.7), arrowprops=dict(arrowstyle="-|>", color=verm, lw=2.2))
    ax.text(x + 0.12, -1.45, f"{fmt(float(v))} kN", color=verm, fontsize=12)
ax.annotate("", (4.15, 2.85), xytext=(5.35, 2.85), arrowprops=dict(arrowstyle="-|>", color=verm, lw=2.2))
ax.text(4.2, 2.95, "160 kN", color=verm, fontsize=12)
ax.text(4.5, 2.2, "biela", fontsize=10, ha="center")
# cotas
ax.annotate("", (0, -2.1), xytext=(4, -2.1), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(2, -2.05, "4 m", ha="center", va="bottom", fontsize=11)
for a, b, t in [(0, 2.5, "2,50 m"), (2.5, 4, "1,50 m")]:
    ax.annotate("", (6.2, a), xytext=(6.2, b), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(6.3, (a + b) / 2, t, va="center", fontsize=11)
ax.set_xlim(-2.4, 7.2)
ax.set_ylim(-2.4, 4.3)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex05-estrutura.png"), dpi=160)
plt.close(fig)


# ---------- diagramas sobre o portico ----------
def diagrama(ax, chave, escala, cor, sinal_lado):
    """sinal_lado = +1: valor positivo desenhado do lado da fibra tracejada (usado para M)
    sinal_lado = -1: positivo do lado oposto (N e V)"""
    for p, q, f, nd in barras:
        p, q, nd = np.array(p, float), np.array(q, float), np.array(nd, float)
        comp = np.linalg.norm(q - p)
        t = (q - p) / comp
        ss = np.linspace(0, comp, 200)
        vals = np.array([f(s)[chave] for s in ss])
        if np.allclose(vals, 0):
            continue
        base = p[None, :] + ss[:, None] * t[None, :]
        curva = base + (sinal_lado * escala * vals)[:, None] * nd[None, :]
        poly = np.vstack([base, curva[::-1]])
        ax.add_patch(Polygon(poly, closed=True, fc=cor, alpha=0.2, ec="none"))
        ax.plot(curva[:, 0], curva[:, 1], color=cor, lw=2)
        ax.plot([base[0, 0], curva[0, 0]], [base[0, 1], curva[0, 1]], color=cor, lw=2)
        ax.plot([base[-1, 0], curva[-1, 0]], [base[-1, 1], curva[-1, 1]], color=cor, lw=2)


def ponto(ax, chave, f, s, p, q, nd, escala, sinal_lado, texto=None, desloc=(0, 0), ha="center", va="center",
          cor="black"):
    p, q, nd = np.array(p, float), np.array(q, float), np.array(nd, float)
    t = (q - p) / np.linalg.norm(q - p)
    v = f(s)[chave]
    xy = p + s * t + sinal_lado * escala * v * nd
    ax.text(xy[0] + desloc[0], xy[1] + desloc[1], texto if texto else fmt(v), ha=ha, va=va,
            fontsize=11, fontweight="bold", color=cor)


def base_fig(titulo):
    fig, ax = plt.subplots(figsize=(8.6, 6.6))
    ax.set_aspect("equal")
    ax.axis("off")
    desenhar_portico(ax, cor="#444", lw=2.2)
    ax.set_title(titulo, loc="left", fontsize=13, fontweight="bold")
    return fig, ax


b_AC, b_CE, b_CD, b_DB = barras

# N
fig, ax = base_fig("Esforço normal N (kN), tração positiva")
eN = 0.003
cN = "#7d3c98"
diagrama(ax, "N", eN, cN, -1)
ax.text(0.45, 1.25, "−60", fontsize=12, fontweight="bold", ha="left", color=cN)
ax.text(0.45, 0.95, "(−)", fontsize=11, ha="left", color=cN)
ax.text(2, 1.75, "−160", fontsize=12, fontweight="bold", ha="center", color=cN)
ax.text(2, 2.15, "(−)", fontsize=11, ha="center", color=cN)
ax.text(3.75, 1.25, "−20", fontsize=12, fontweight="bold", ha="right", color=cN)
ax.text(3.75, 0.95, "(−)", fontsize=11, ha="right", color=cN)
ax.text(0.15, 3.25, "N = 0", fontsize=11, ha="left")
ax.text(4.25, 2.75, "−160 (biela)", fontsize=11, fontweight="bold", ha="left", color=cN)
ax.set_xlim(-1.6, 6.6)
ax.set_ylim(-0.9, 4.4)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex05-N.png"), dpi=160)
plt.close(fig)

# V
fig, ax = base_fig("Esforço cortante V (kN)")
eV = 0.009
cV = "#2471a3"
diagrama(ax, "V", eV, cV, -1)
ponto(ax, "V", AC, 0, *b_AC[:2], b_AC[3], eV, -1, "0", desloc=(0.15, 0.1), ha="left")
ponto(ax, "V", AC, 2.5, *b_AC[:2], b_AC[3], eV, -1, desloc=(0.1, -0.15), ha="left")
ponto(ax, "V", CE, 0, *b_CE[:2], b_CE[3], eV, -1, desloc=(-0.1, 0.12), ha="right")
ponto(ax, "V", CE, 1.5, *b_CE[:2], b_CE[3], eV, -1, "0", desloc=(-0.1, 0.0), ha="right")
ponto(ax, "V", CD, 0, *b_CD[:2], b_CD[3], eV, -1, desloc=(0.12, 0.12), ha="left")
ponto(ax, "V", CD, 3, *b_CD[:2], b_CD[3], eV, -1, "0 (x = 3)", desloc=(0, 0.2), ha="center")
ponto(ax, "V", CD, 4, *b_CD[:2], b_CD[3], eV, -1, desloc=(-0.1, -0.15), ha="right")
ax.text(1.0, 1.4, "(−)", fontsize=12, color=cV, ha="center")
ax.text(-0.25, 3.2, "(+)", fontsize=12, color=cV, ha="right")
ax.text(1.0, 2.95, "(+)", fontsize=12, color=cV, ha="center")
ax.text(3.6, 2.3, "(−)", fontsize=12, color=cV, ha="center")
ax.text(4.15, 1.25, "V = 0", fontsize=11, ha="left")
ax.text(4.25, 2.75, "biela: V = 0", fontsize=10, ha="left")
ax.set_xlim(-1.6, 6.6)
ax.set_ylim(-0.9, 4.4)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex05-V.png"), dpi=160)
plt.close(fig)

# M (lado tracionado)
fig, ax = base_fig("Momento fletor M (kN.m), desenhado do lado tracionado")
eM = 0.009
cM = "#b03a2e"
diagrama(ax, "M", eM, cM, +1)
ponto(ax, "M", AC, 0, *b_AC[:2], b_AC[3], eM, 1, "0", desloc=(-0.12, 0.1), ha="right")
ponto(ax, "M", AC, 2.5, *b_AC[:2], b_AC[3], eM, 1, desloc=(-0.08, -0.1), ha="right", va="top")
ponto(ax, "M", CE, 0, *b_CE[:2], b_CE[3], eM, 1, desloc=(-0.05, 0.2), ha="right", va="bottom")
ponto(ax, "M", CE, 1.5, *b_CE[:2], b_CE[3], eM, 1, "0", desloc=(-0.12, 0), ha="right")
ponto(ax, "M", CD, 0, *b_CD[:2], b_CD[3], eM, 1, desloc=(0.1, 0.05), ha="left", va="bottom")
ponto(ax, "M", CD, 2, *b_CD[:2], b_CD[3], eM, 1, "0 (x = 2)", desloc=(0, 0.12), va="bottom")
ponto(ax, "M", CD, 3, *b_CD[:2], b_CD[3], eM, 1, "10 (x = 3)", desloc=(0, -0.12), va="top")
ponto(ax, "M", CD, 4, *b_CD[:2], b_CD[3], eM, 1, "0", desloc=(-0.1, 0.12), ha="right", va="bottom")
ax.text(4.15, 1.25, "M = 0", fontsize=11, ha="left")
ax.text(-0.5, 0.15, "tração\nà esquerda", fontsize=10, ha="right", color=cM)
ax.set_xlim(-2.0, 6.2)
ax.set_ylim(-0.9, 4.4)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex05-M.png"), dpi=160)
plt.close(fig)
print("figuras salvas em", SAIDA)
