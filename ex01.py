from fractions import Fraction as F
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch, Polygon, Circle

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "figuras")
os.makedirs(SAIDA, exist_ok=True)

# exercicio 01: x em metros a partir de A
xA, xM, xB, xC, xP, xD, xE = 0, 2, 5, 7, 8, 10, 12
q, P, M0 = 10, 20, 36  # kN/m, kN, kN.m (horario)

# trecho CD: soma de momentos em C
VD = (q * (xE - xC) * (xE - xC) / F(2) + P * (xP - xC)) / (xD - xC)
VC = q * (xE - xC) + P - VD
# trecho AC: soma de momentos em A (anti-horario positivo)
VB = (q * (xC - xB) * F(xB + xC, 2) + VC * xC + M0) / (xB - xA)
VA = q * (xC - xB) + VC - VB

print("VA =", VA, float(VA))
print("VB =", VB, float(VB))
print("VC =", VC, float(VC))
print("VD =", VD, float(VD))


def carga(x, a):
    return q * max(0, x - a)


def V(x):
    v = float(VA)
    if x > xB:
        v += float(VB) - q * (x - xB)
    if x > xP:
        v -= P
    if x > xD:
        v += float(VD)
    return v


def M(x):
    m = float(VA) * x
    if x > xM:
        m += M0
    if x > xB:
        m += float(VB) * (x - xB) - q * (x - xB) ** 2 / 2
    if x > xP:
        m -= P * (x - xP)
    if x > xD:
        m += float(VD) * (x - xD)
    return m


eps = 1e-9
pontos = [xA, xM, xB, xC, xP, xD, xE]
for x in pontos:
    print(f"x={x:>2}  V-={V(x - eps):8.3f}  V+={V(x + eps):8.3f}  M-={M(x - eps):8.3f}  M+={M(x + eps):8.3f}")


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("-" if v < -1e-6 else "") + s


def eixo(ax, titulo, unidade):
    ax.axhline(0, color="black", lw=1.2)
    ax.set_xlim(-0.8, 12.8)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.set_yticks([])
    ax.set_xticks(pontos)
    ax.set_xticklabels(["A", "", "B", "C", "", "D", ""])
    ax.set_title(f"{titulo} ({unidade})", loc="left", fontsize=12, fontweight="bold")
    for x in pontos:
        ax.axvline(x, color="#bbb", lw=0.6, ls=":", zorder=0)


def preencher(ax, xs, ys, cor):
    ax.plot(xs, ys, color=cor, lw=2)
    ax.fill_between(xs, ys, 0, color=cor, alpha=0.18)


def rotulo(ax, x, y, texto, dy, cor="black", ha="center"):
    ax.annotate(texto, (x, y), xytext=(0, dy), textcoords="offset points", ha=ha,
                va="bottom" if dy > 0 else "top", fontsize=10, color=cor, fontweight="bold")


def segmento(f, a, b, n=200):
    xs = np.linspace(a + eps, b - eps, n)
    return xs, np.array([f(x) for x in xs])


# ---------- figura 1: estrutura e reacoes ----------
fig, ax = plt.subplots(figsize=(11, 3.6))
ax.set_xlim(-1, 13)
ax.set_ylim(-2.6, 3.2)
ax.axis("off")
ax.plot([xA, xE], [0, 0], color="black", lw=3)


def apoio(x, fixo):
    ax.add_patch(Polygon([[x, 0], [x - 0.3, -0.5], [x + 0.3, -0.5]], closed=True, fill=False, lw=1.5))
    base = -0.5 if fixo else -0.62
    ax.plot([x - 0.45, x + 0.45], [base, base], color="black", lw=1.5)
    for i in np.linspace(x - 0.4, x + 0.4, 6):
        ax.plot([i, i - 0.12], [base, base - 0.15], color="black", lw=0.8)


apoio(xA, True)
apoio(xB, False)
apoio(xD, False)
ax.add_patch(Circle((xC, 0), 0.12, fill=True, fc="white", ec="black", lw=1.5, zorder=5))
for x, n in [(xA, "A"), (xB, "B"), (xC, "C"), (xD, "D")]:
    ax.text(x + 0.15, 0.25, n, fontsize=12)

# carga distribuida
ax.plot([xB, xE], [1.1, 1.1], color="#1f5fbf", lw=1)
for x in np.linspace(xB, xE, 15):
    ax.annotate("", (x, 0.05), xytext=(x, 1.1), arrowprops=dict(arrowstyle="->", color="#1f5fbf", lw=1))
ax.text(6, 1.25, "10 kN/m", color="#1f5fbf", fontsize=11)
# forca concentrada
ax.annotate("", (xP, 0.05), xytext=(xP, 2.3), arrowprops=dict(arrowstyle="-|>", color="#1f5fbf", lw=2.2))
ax.text(xP + 0.15, 2.0, "20 kN", color="#1f5fbf", fontsize=11)
# momento horario
ax.add_patch(Arc((xM, 0), 1.2, 1.2, theta1=-60, theta2=180, color="#1f5fbf", lw=1.6))
ax.annotate("", (xM + 0.32, -0.52), xytext=(xM + 0.5, -0.36),
            arrowprops=dict(arrowstyle="-|>", color="#1f5fbf", lw=1.6))
ax.text(xM - 0.5, 0.8, "36 kN.m", color="#1f5fbf", fontsize=11)

# reacoes
cor_r = "#c0392b"
ax.annotate("", (xA, -0.75), xytext=(xA, -1.9), arrowprops=dict(arrowstyle="<|-", color=cor_r, lw=2))
ax.text(xA + 0.15, -1.6, "19,87 kN", color=cor_r, fontsize=10)
for x, v in [(xB, VB), (xD, VD)]:
    ax.annotate("", (x, -0.75), xytext=(x, -1.9), arrowprops=dict(arrowstyle="-|>", color=cor_r, lw=2))
    ax.text(x + 0.15, -1.6, f"{fmt(float(v))} kN", color=cor_r, fontsize=10)
ax.text(xA - 0.95, -1.15, "H$_A$ = 0", color=cor_r, fontsize=10)

# cotas
for a, b in zip(pontos[:-1], pontos[1:]):
    ax.annotate("", (a, -2.3), xytext=(b, -2.3), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((a + b) / 2, -2.25, f"{b - a} m", ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex01-estrutura.png"), dpi=160)
plt.close(fig)

# ---------- figura 2: N, V, M ----------
fig, (aN, aV, aM) = plt.subplots(3, 1, figsize=(11, 9), sharex=True, gridspec_kw={"height_ratios": [1, 3, 3]})

eixo(aN, "Esforço normal N", "kN")
aN.set_ylim(-1, 1)
aN.plot([xA, xE], [0, 0], color="#555", lw=3)
aN.text(6, 0.25, "N = 0 em toda a viga (não há força horizontal)", ha="center", fontsize=11)

eixo(aV, "Esforço cortante V", "kN")
cor = "#2471a3"
for a, b in [(xA, xB), (xB, xP), (xP, xD), (xD, xE)]:
    xs, ys = segmento(V, a, b)
    preencher(aV, xs, ys, cor)
# saltos verticais
for x in [xA, xB, xP, xD, xE]:
    aV.plot([x, x], [V(x - eps) if x > 0 else 0, V(x + eps) if x < xE else 0], color=cor, lw=2)
rotulo(aV, 2.5, V(1), "-19,87", -6)
rotulo(aV, xB + 0.05, V(xB + eps), "41,67", 4, ha="left")
rotulo(aV, xC, V(xC), "21,67", 4)
rotulo(aV, xP - 0.05, V(xP - eps), "11,67", 4, ha="right")
rotulo(aV, xP + 0.1, V(xP + eps), "-8,33", -6, ha="left")
rotulo(aV, xD - 0.05, V(xD - eps), "-28,33", -6, ha="right")
rotulo(aV, xD + 0.1, V(xD + eps), "20", 4, ha="left")
aV.set_ylim(-40, 55)

# momento: positivo para baixo (lado tracionado)
eixo(aM, "Momento fletor M", "kN.m, positivo desenhado embaixo")
cor = "#b03a2e"
for a, b in [(xA, xM), (xM, xB), (xB, xP), (xP, xD), (xD, xE)]:
    xs, ys = segmento(M, a, b)
    preencher(aM, xs, ys, cor)
aM.plot([xM, xM], [M(xM - eps), M(xM + eps)], color=cor, lw=2)
rotulo(aM, xM - 0.05, M(xM - eps), "-39,73", 4, ha="right")
rotulo(aM, xM + 0.1, M(xM + eps), "-3,73", 4, ha="left")
rotulo(aM, xB, M(xB), "-63,33", 4)
rotulo(aM, xC, 0, "0 (rótula)", 4)
rotulo(aM, xP, M(xP), "16,67", -6)
rotulo(aM, 9.1, 0, "0 em x = 9,17", 4, ha="right")
rotulo(aM, xD, M(xD), "-20", 4)
rotulo(aM, xE, 0, "0", 4)
aM.set_ylim(35, -80)
aM.set_xlabel("x (m)")
aM.set_xticklabels(["A\n0", "\n2", "B\n5", "C\n7", "\n8", "D\n10", "\n12"])

fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex01-diagramas.png"), dpi=160)
plt.close(fig)
print("figuras salvas em", SAIDA)
