from fractions import Fraction as F
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Polygon, Circle

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "figuras")
os.makedirs(SAIDA, exist_ok=True)

# exercicio 03: x em metros a partir do engaste A
xA, xP, xQ, xB, xC, xE = 0, 2, 4, 6, 10, 12
q, P = 10, 10  # kN/m (de xQ ate xC), kN em xP

# trecho BC (de B a E): soma de momentos em B
VC = F(q * (xC - xB) * (xC - xB), 2) / (xC - xB)
VB = q * (xC - xB) - VC  # forca que AB faz em BC (para cima)
# trecho AB: forcas verticais e momentos em A (anti-horario positivo)
VA = P + q * (xB - xQ) + VB
MA = P * xP + q * (xB - xQ) * F(xQ + xB, 2) + VB * xB  # anti-horario

print("VA =", VA, float(VA))
print("MA =", MA, float(MA), "(anti-horario)")
print("VB =", VB, float(VB))
print("VC =", VC, float(VC))
print("conferencia SFy:", VA + VC - P - q * (xC - xQ))
print("conferencia SM_A:", MA + VC * xC - P * xP - q * (xC - xQ) * F(xQ + xC, 2))


def V(x):
    v = float(VA)
    if x > xP:
        v -= P
    if x > xQ:
        v -= q * (min(x, xC) - xQ)
    if x > xC:
        v += float(VC)
    return v


def M(x):
    m = -float(MA) + float(VA) * x
    if x > xP:
        m -= P * (x - xP)
    if x > xQ:
        a = min(x, xC) - xQ
        m -= q * a * (x - xQ - a / 2)
    if x > xC:
        m += float(VC) * (x - xC)
    return m


eps = 1e-9
pontos = [xA, xP, xQ, xB, 8, xC, xE]
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
    ax.set_xticklabels(["A", "", "", "B", "", "C", ""])
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


azul = "#1f5fbf"
cor_r = "#c0392b"


def engaste(ax, x):
    ax.plot([x, x], [-0.7, 0.7], color="black", lw=2)
    for y in np.linspace(-0.65, 0.65, 8):
        ax.plot([x, x - 0.18], [y, y - 0.15], color="black", lw=0.8)


def movel(ax, x):
    ax.add_patch(Polygon([[x, 0], [x - 0.3, -0.5], [x + 0.3, -0.5]], closed=True, fill=False, lw=1.5))
    ax.plot([x - 0.45, x + 0.45], [-0.62, -0.62], color="black", lw=1.5)
    for i in np.linspace(x - 0.4, x + 0.4, 6):
        ax.plot([i, i - 0.12], [-0.62, -0.77], color="black", lw=0.8)


def distribuida(ax, a, b, y0=0.05, h=1.0, n=None):
    n = n or int(round((b - a) * 2)) + 1
    ax.plot([a, b], [y0 + h, y0 + h], color=azul, lw=1)
    for x in np.linspace(a, b, n):
        ax.annotate("", (x, y0), xytext=(x, y0 + h), arrowprops=dict(arrowstyle="->", color=azul, lw=1))


def seta(ax, x, y0, y1, cor, texto, dx=0.15, lw=2.2):
    ax.annotate("", (x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="-|>", color=cor, lw=lw))
    ax.text(x + dx, (y0 + y1) / 2, texto, color=cor, fontsize=10, va="center")


def momento_anti(ax, x, texto):
    ax.add_patch(Arc((x, 0), 1.3, 1.3, theta1=100, theta2=260, color=cor_r, lw=1.8))
    ax.annotate("", (x + 0.05, -0.65), xytext=(x - 0.12, -0.64),
                arrowprops=dict(arrowstyle="-|>", color=cor_r, lw=1.8))
    ax.text(x - 1.55, 0.75, texto, color=cor_r, fontsize=10)


# ---------- figura 1: estrutura e reacoes ----------
fig, ax = plt.subplots(figsize=(11, 3.8))
ax.set_xlim(-2, 13)
ax.set_ylim(-2.7, 3.0)
ax.axis("off")
ax.plot([xA, xE], [0, 0], color="black", lw=3)
engaste(ax, xA)
movel(ax, xC)
ax.add_patch(Circle((xB, 0), 0.13, fc="white", ec="black", lw=1.5, zorder=5))
for x, n in [(xA, "A"), (xB, "B"), (xC, "C")]:
    ax.text(x + (0.15 if x != xC else 0.5), 0.25 if x != xC else -0.45, n, fontsize=12, ha="left")
distribuida(ax, xQ, xC)
ax.text(7, 1.2, "10 kN/m", color=azul, fontsize=11, ha="center")
seta(ax, xP, 2.3, 0.05, azul, "10 kN")
# reacoes
seta(ax, xA + 0.35, -1.9, -0.15, cor_r, "50 kN", dx=0.1)
momento_anti(ax, xA, "240 kN.m")
ax.text(-1.95, -0.25, "H$_A$ = 0", color=cor_r, fontsize=10)
seta(ax, xC, -1.95, -0.8, cor_r, "20 kN")
for a, b in zip([0, 2, 4, 6, 10], [2, 4, 6, 10, 12]):
    ax.annotate("", (a, -2.4), xytext=(b, -2.4), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((a + b) / 2, -2.35, f"{b - a} m", ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex03-estrutura.png"), dpi=160)
plt.close(fig)

# ---------- figura 2: partes separadas na rotula ----------
fig, ax = plt.subplots(figsize=(11, 3.4))
ax.set_xlim(-2, 14.5)
ax.set_ylim(-2.3, 2.8)
ax.axis("off")
d = 1.5  # deslocamento da parte BC para a direita
ax.plot([xA, xB], [0, 0], color="black", lw=3)
ax.plot([xB + d, xE + d], [0, 0], color="black", lw=3)
engaste(ax, xA)
movel(ax, xC + d)
ax.text(xA + 0.15, 0.25, "A", fontsize=12)
ax.text(xB - 0.1, 0.25, "B", fontsize=12, ha="right")
ax.text(xB + d + 0.1, 0.25, "B", fontsize=12)
ax.text(xC + d + 0.5, -0.45, "C", fontsize=12)
distribuida(ax, xQ, xB, n=5)
distribuida(ax, xB + d, xC + d, n=9)
ax.text(5, 1.2, "10 kN/m", color=azul, fontsize=10, ha="center")
ax.text(8 + d, 1.2, "10 kN/m", color=azul, fontsize=10, ha="center")
seta(ax, xP, 2.3, 0.05, azul, "10 kN")
seta(ax, xA + 0.35, -1.8, -0.15, cor_r, "50 kN", dx=0.1)
momento_anti(ax, xA, "240 kN.m")
seta(ax, xC + d, -1.85, -0.8, cor_r, "20 kN")
verde = "#1e8449"
seta(ax, xB, 0.0, -1.5, verde, "20 kN", dx=0.12)
seta(ax, xB + d, -1.5, -0.05, verde, "20 kN", dx=0.12)
ax.text(xA + 3, -2.2, "parte AB", ha="center", fontsize=11)
ax.text(9 + d, -2.2, "parte BC", ha="center", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex03-partes.png"), dpi=160)
plt.close(fig)

# ---------- figura 3: N, V, M ----------
fig, (aN, aV, aM) = plt.subplots(3, 1, figsize=(11, 9), sharex=True, gridspec_kw={"height_ratios": [1, 3, 3.4]})

eixo(aN, "Esforço normal N", "kN")
aN.set_ylim(-1, 1)
aN.plot([xA, xE], [0, 0], color="#555", lw=3)
aN.text(6, 0.25, "N = 0 em toda a viga (não há força horizontal)", ha="center", fontsize=11)

eixo(aV, "Esforço cortante V", "kN")
cor = "#2471a3"
for a, b in [(xA, xP), (xP, xC)]:
    xs, ys = segmento(V, a, b)
    preencher(aV, xs, ys, cor)
for x in [xA, xP, xC]:
    aV.plot([x, x], [V(x - eps) if x > 0 else 0, V(x + eps)], color=cor, lw=2)
aV.plot([xC, xE], [0, 0], color=cor, lw=2)
rotulo(aV, xA + 0.1, 50, "50", 4, ha="left")
rotulo(aV, xP - 0.05, 50, "50", 4, ha="right")
rotulo(aV, xP + 0.1, 40, "40", 4, ha="left")
rotulo(aV, xQ, 40, "40", 4)
rotulo(aV, xB, 20, "20", 4)
rotulo(aV, 8.15, 0, "0 em x = 8", 6, ha="left")
rotulo(aV, xC - 0.05, -20, "-20", -6, ha="right")
rotulo(aV, 11, 0, "0", 4)
aV.set_ylim(-35, 65)

eixo(aM, "Momento fletor M", "kN.m, positivo desenhado embaixo")
cor = "#b03a2e"
for a, b in [(xA, xP), (xP, xQ), (xQ, xB), (xB, xC)]:
    xs, ys = segmento(M, a, b)
    preencher(aM, xs, ys, cor)
aM.plot([xA, xA], [0, M(eps)], color=cor, lw=2)
aM.plot([xC, xE], [0, 0], color=cor, lw=2)
rotulo(aM, xA + 0.1, M(eps), "-240", 4, ha="left")
rotulo(aM, xP + 0.1, M(xP), "-140", 4, ha="left")
rotulo(aM, xQ + 0.1, M(xQ), "-60", 4, ha="left")
rotulo(aM, xB, 0, "0 (rótula)", 4)
rotulo(aM, 8, M(8), "20 (máx.)", -6)
rotulo(aM, xC, 0, "0", 4)
rotulo(aM, 11, 0, "0", 4)
aM.set_ylim(55, -280)
aM.set_xlabel("x (m)")
aM.set_xticklabels(["A\n0", "\n2", "\n4", "B\n6", "\n8", "C\n10", "\n12"])

fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex03-diagramas.png"), dpi=160)
plt.close(fig)
print("figuras salvas em", SAIDA)
