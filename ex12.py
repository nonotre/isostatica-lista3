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

# exercicio 12: origem no pe do pilar (prolongado), x para a direita, y para cima
A = (4, 0)   # apoio fixo (2o genero)
B = (0, 3)   # no rigido com biela horizontal (1o genero)
C = (0, 7)   # topo do pilar, luva (engaste deslizante vertical)
D = (4, 7)   # apoio movel (1o genero)
q, P = 5, 20  # kN/m na viga CD, kN horizontal em B (para a direita)
L = D[0] - C[0]

# viga CD isolada: a luva nao transmite forca vertical
VD = F(q * L)                      # soma de forcas verticais na viga
HC = F(0)                          # soma de forcas horizontais na viga (movel nao tem H)
# soma de momentos em D na viga (anti-horario positivo): MC + q*L*(L/2) = 0
MC_viga = -F(q * L * L, 2)         # momento que o pilar aplica na viga (horario)
# estrutura inteira
VA = q * L - VD
# soma de momentos em A: carga q*L em (2,7), HB e P em (0,3), VD em (4,7)
def mz(p, f, o):
    return (p[0] - o[0]) * f[1] - (p[1] - o[1]) * f[0]
# 0 = mz(carga) + mz(P) + mz(HB) -> HB * (-(3-0)) ...
m_carga = mz((F(2), F(7)), (0, -q * L), A)
m_P = mz(B, (P, 0), A)
HB = (m_carga + m_P) / (B[1] - A[1])   # mz(HB) = -(yB - yA) * HB
HA = -P - HB

print("VD =", VD, float(VD))
print("HC (luva) =", HC, " MC (luva, sobre a viga) =", MC_viga, float(MC_viga))
print("VA =", VA, float(VA))
print("HB =", HB, float(HB))
print("HA =", HA, float(HA))

# conferencia global
fx = HA + HB + P
fy = VA + VD - q * L
for o, n in [(A, "A"), (B, "B"), (D, "D"), ((0, 0), "O")]:
    m = (mz(A, (HA, VA), o) + mz(B, (HB, 0), o) + mz(B, (P, 0), o)
         + mz(D, (0, VD), o) + mz((2, 7), (0, -q * L), o))
    print(f"soma de momentos em {n} = {m}")
print("soma Fx =", fx, " soma Fy =", fy)

# barra AB (percurso A -> B), t = (-0,8; 0,6), n (esquerda do percurso) = (-0,6; -0,8)
t = (F(-4, 5), F(3, 5))
n = (-t[1], t[0])
NAB = -(HA * t[0] + VA * t[1])
VAB = HA * n[0] + VA * n[1]
print("barra AB: N =", NAB, float(NAB), " V =", VAB, float(VAB), " M(B) =", VAB * 5)
# pilar BC (percurso B -> C): forcas abaixo da secao
Fbx, Fby = HA + HB + P, VA
print("pilar BC: soma das forcas abaixo da secao =", Fbx, Fby)
MBC = VAB * 5
print("pilar BC: N = 0, V = 0, M =", MBC)
# viga CD (percurso C -> D)
for x in [0, 1, 2, 3, 4]:
    print(f"viga x={x}: V = {-q * x}, M = {float(-MC_viga - F(q, 2) * x * x):.3f}")

L_AB = 5


def Mviga(x):
    return float(-MC_viga) - q * x ** 2 / 2


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("−" if v < -1e-6 else "") + s


# ---------- figura 1: estrutura e reacoes ----------
cor_c, cor_r = "#1f5fbf", "#c0392b"


def estrutura(ax, fina=False):
    lw = 1.6 if fina else 3
    cor = "#888" if fina else "black"
    ax.plot([A[0], B[0], C[0]], [A[1], B[1], C[1] - 0.06], color=cor, lw=lw, solid_capstyle="round")
    ax.plot([C[0] + 0.1, D[0]], [C[1], D[1]], color=cor, lw=lw, solid_capstyle="round")
    # luva: dois tracos verticais
    for xx in (-0.13, 0.13):
        ax.plot([xx, xx], [6.75, 7.2], color=cor, lw=1.2)


def apoio(ax, p, fixo):
    x, y = p
    ax.add_patch(Circle((x, y - 0.1), 0.1, fill=True, fc="white", ec="black", lw=1.3, zorder=5))
    ax.add_patch(Polygon([[x, y - 0.2], [x - 0.28, y - 0.62], [x + 0.28, y - 0.62]], closed=True, fill=False, lw=1.4))
    base = y - 0.62 if fixo else y - 0.74
    if not fixo:
        ax.plot([x - 0.42, x + 0.42], [y - 0.62, y - 0.62], color="black", lw=1.4)
    ax.plot([x - 0.45, x + 0.45], [base, base], color="black", lw=1.4)
    for i in np.linspace(x - 0.4, x + 0.4, 7):
        ax.plot([i, i - 0.12], [base, base - 0.15], color="black", lw=0.8)


fig, ax = plt.subplots(figsize=(8, 8.4))
ax.set_aspect("equal")
ax.set_xlim(-3.2, 6.8)
ax.set_ylim(-1.9, 9.2)
ax.axis("off")
estrutura(ax)
apoio(ax, A, True)
apoio(ax, D, False)
# biela horizontal em B
ax.plot([-1.0, B[0]], [B[1], B[1]], color="black", lw=1)
ax.add_patch(Circle((-1.0, B[1]), 0.08, fc="white", ec="black", lw=1.2, zorder=5))
ax.plot([-1.08, -1.08], [B[1] - 0.45, B[1] + 0.45], color="black", lw=1.4)
for i in np.linspace(B[1] - 0.4, B[1] + 0.4, 7):
    ax.plot([-1.08, -1.23], [i, i - 0.1], color="black", lw=0.8)
for p, nome, dx, dy in [(A, "A", 0.2, 0.05), (B, "B", 0.2, -0.45), (C, "C", -0.55, -0.35), (D, "D", 0.2, 0.15)]:
    ax.text(p[0] + dx, p[1] + dy, nome, fontsize=13)
# carga distribuida
ax.plot([0, 4], [7.9, 7.9], color=cor_c, lw=1)
for x in np.linspace(0, 4, 11):
    ax.annotate("", (x, 7.08), xytext=(x, 7.9), arrowprops=dict(arrowstyle="->", color=cor_c, lw=1))
ax.text(1.3, 8.0, "5 kN/m", color=cor_c, fontsize=12)
# forca de 20 kN
ax.annotate("", (1.6, B[1] + 0.05), xytext=(0.1, B[1] + 0.05), arrowprops=dict(arrowstyle="-|>", color=cor_c, lw=2.2))
ax.text(0.35, B[1] + 0.25, "20 kN", color=cor_c, fontsize=12)
# reacoes
ax.annotate("", (D[0], D[1] - 0.8), xytext=(D[0], D[1] - 2.0), arrowprops=dict(arrowstyle="-|>", color=cor_r, lw=2))
ax.text(D[0] + 0.15, D[1] - 1.8, "V$_D$ = 20 kN", color=cor_r, fontsize=11)
ax.annotate("", (-1.6, B[1] - 0.75), xytext=(-0.3, B[1] - 0.75), arrowprops=dict(arrowstyle="-|>", color=cor_r, lw=2))
ax.text(-3.1, B[1] - 1.3, "H$_B$ = 6,67 kN", color=cor_r, fontsize=11)
ax.annotate("", (A[0] + 0.5, A[1] - 0.95), xytext=(A[0] + 1.9, A[1] - 0.95), arrowprops=dict(arrowstyle="-|>", color=cor_r, lw=2))
ax.text(A[0] + 0.4, A[1] - 1.55, "H$_A$ = 13,33 kN", color=cor_r, fontsize=11)
ax.text(A[0] - 2.4, A[1] - 0.9, "V$_A$ = 0", color=cor_r, fontsize=11)
# cotas
ax.annotate("", (5.9, 0), xytext=(5.9, 3), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(6.0, 1.5, "3 m", va="center", fontsize=10)
ax.annotate("", (5.9, 3), xytext=(5.9, 7), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(6.0, 5, "4 m", va="center", fontsize=10)
for yy in (0, 3, 7):
    ax.plot([4.3 if yy != 3 else 0.2, 6.0], [yy, yy], color="#999", lw=0.5, ls=":")
ax.annotate("", (0, -1.7), xytext=(4, -1.7), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(2, -1.65, "4 m", ha="center", va="bottom", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex12-estrutura.png"), dpi=160)
plt.close(fig)


# ---------- figura 2: N, V, M sobre o portico ----------
def desenhar_barra(ax, p0, p1, f, escala, lado, cor, n=60):
    """lado = +1 desenha valor positivo a esquerda do percurso p0 -> p1, -1 a direita"""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    comp = np.linalg.norm(p1 - p0)
    tt = (p1 - p0) / comp
    nn = np.array([-tt[1], tt[0]])
    s = np.linspace(0, comp, n)
    vals = np.array([f(si) for si in s])
    base = p0[None, :] + s[:, None] * tt[None, :]
    curva = base + (lado * escala * vals)[:, None] * nn[None, :]
    poly = np.vstack([base, curva[::-1]])
    ax.add_patch(Polygon(poly, closed=True, fc=cor, alpha=0.2, ec="none"))
    ax.plot(curva[:, 0], curva[:, 1], color=cor, lw=2)
    ax.plot([base[0, 0], curva[0, 0]], [base[0, 1], curva[0, 1]], color=cor, lw=2)
    ax.plot([base[-1, 0], curva[-1, 0]], [base[-1, 1], curva[-1, 1]], color=cor, lw=2)
    return tt, nn


def ponto(p0, p1, s, off, lado):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    tt = (p1 - p0) / np.linalg.norm(p1 - p0)
    nn = np.array([-tt[1], tt[0]])
    return p0 + s * tt + lado * off * nn


def preparar(ax, titulo):
    ax.set_aspect("equal")
    ax.set_xlim(-2.6, 6.2)
    ax.set_ylim(-1.0, 9.0)
    ax.axis("off")
    estrutura(ax, fina=True)
    for p, nome, dx, dy in [(A, "A", 0.15, -0.4), (B, "B", -0.45, -0.1), (C, "C", -0.5, 0.15), (D, "D", 0.15, 0.15)]:
        ax.text(p[0] + dx, p[1] + dy, nome, fontsize=12, color="#444")
    ax.set_title(titulo, fontsize=13, fontweight="bold")


fig, (aN, aV, aM) = plt.subplots(1, 3, figsize=(16, 7.4))
fN = float(NAB)
fV = float(VAB)
esc = 0.07
escV = 0.06
escM = 0.025

preparar(aN, "Esforço normal N (kN)")
cor = "#7d3c98"
desenhar_barra(aN, A, B, lambda s: fN, esc, +1, cor)
p = ponto(A, B, 2.5, esc * abs(fN) + 0.25, -1)
aN.text(p[0] + 0.2, p[1] + 0.1, f"{fmt(fN)}\n(compressão)", fontsize=11, color=cor, fontweight="bold", ha="left", va="bottom")
aN.text(-0.25, 5, "N = 0", fontsize=11, color=cor, fontweight="bold", rotation=90, va="center", ha="right")
aN.text(2, 7.25, "N = 0", fontsize=11, color=cor, fontweight="bold", ha="center")
aN.text(-1.0, 0.0, "percursos:\nA → B, B → C, C → D", fontsize=9.5, color="#444", va="top")

preparar(aV, "Esforço cortante V (kN)")
cor = "#2471a3"
desenhar_barra(aV, A, B, lambda s: fV, escV, +1, cor)
p = ponto(A, B, 2.5, escV * fV + 0.25, +1)
aV.text(p[0], p[1], f"+{fmt(fV)}", fontsize=11, color=cor, fontweight="bold", ha="right", va="top")
desenhar_barra(aV, C, D, lambda s: -q * s, escV, +1, cor)
aV.text(2.0, 6.85, "(−)", fontsize=11, color=cor, fontweight="bold", ha="center", va="top")
aV.text(1.9, 1.5, "(+)", fontsize=11, color=cor, fontweight="bold")
aV.text(4.12, 7 - escV * 20 / 2, "−20", fontsize=11, color=cor, fontweight="bold", ha="left", va="center")
aV.text(0.15, 7.15, "0", fontsize=11, color=cor, fontweight="bold")
aV.text(-0.25, 5, "V = 0", fontsize=11, color=cor, fontweight="bold", rotation=90, va="center", ha="right")
aV.text(-1.0, 0.0, "V > 0: resultante antes da\nseção aponta para a esquerda\ndo sentido de percurso", fontsize=9.5, color="#444", va="top")

preparar(aM, "Momento fletor M (kN.m), lado tracionado")
cor = "#b03a2e"
# M positivo traciona o lado direito do percurso (interno ao portico)
desenhar_barra(aM, A, B, lambda s: fV * s, escM, -1, cor)
desenhar_barra(aM, B, C, lambda s: float(MBC), escM, -1, cor)
desenhar_barra(aM, C, D, lambda s: Mviga(s), escM, -1, cor)
d = escM * 40
aM.text(d + 0.08, 4.8, "40\n(constante)", fontsize=11, color=cor, fontweight="bold", va="center")
aM.annotate("40", (0.03, 7 - d), xytext=(-1.1, 5.5), fontsize=11, color=cor, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=cor, lw=1))
p = ponto(C, D, 2, escM * Mviga(2) + 0.08, -1)
aM.text(p[0], p[1], "30", fontsize=11, color=cor, fontweight="bold", va="top", ha="center")
aM.text(4.15, 6.55, "0", fontsize=11, color=cor, fontweight="bold")
aM.text(A[0] + 0.15, A[1] + 0.05, "0", fontsize=11, color=cor, fontweight="bold")
p = ponto(A, B, 2.5, escM * fV * 2.5 + 0.1, -1)
aM.text(p[0], p[1], "20", fontsize=11, color=cor, fontweight="bold", va="top")
p = ponto(A, B, 5, escM * 40 + 0.1, -1)
aM.text(p[0] + 0.1, p[1], "40", fontsize=11, color=cor, fontweight="bold", va="bottom")
aM.text(-1.0, 0.0, "tração no lado interno\ndo pórtico em todas as barras", fontsize=9.5, color="#444", va="top")

fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex12-diagramas.png"), dpi=150)
plt.close(fig)
print("figuras salvas em", SAIDA)
