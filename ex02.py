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

# exercicio 02: x em metros a partir do engaste A
xA, xP1, xB, xP2, xC, xD, xE, xF = 0, 2, 4, 6, 8, 10, 14, 16
q = 20          # kN/m nos dois trechos carregados
P1, P2 = 10, 10  # kN para baixo em x = 2 e x = 6
q1a, q1b = 2, 6    # primeira distribuida
q2a, q2b = 10, 16  # segunda distribuida

# trecho BC (entre as duas rotulas): momentos em B
R_BC = q * (xC - xB if q1b > xC else q1b - xB)  # parte da 1a distribuida dentro de BC
xr_BC = (xB + q1b) / F(2)
VC = (R_BC * (xr_BC - xB) + P2 * (xP2 - xB)) / (xC - xB)
VB = R_BC + P2 - VC
# trecho AB (engastado): recebe VB para baixo em B
R_AB = q * (xB - q1a)
xr_AB = (q1a + xB) / F(2)
VA = P1 + R_AB + VB
MA = P1 * (xP1 - xA) + R_AB * (xr_AB - xA) + VB * (xB - xA)  # anti-horario
# trecho CF: recebe VC para baixo em C. momentos em D (anti-horario positivo)
R_CF = q * (q2b - q2a)
xr_CF = (q2a + q2b) / F(2)
VE = (R_CF * (xr_CF - xD) - VC * (xD - xC)) / (xE - xD)
VD = R_CF + VC - VE

for nome, v in [("VA", VA), ("MA", MA), ("VB", VB), ("VC", VC), ("VD", VD), ("VE", VE)]:
    print(f"{nome} = {v} = {float(v):.4f}")
cargas = P1 + P2 + q * (q1b - q1a) + R_CF
print("soma reacoes =", VA + VD + VE, " soma cargas =", cargas)
mom = (MA + VD * xD + VE * xE - P1 * xP1 - P2 * xP2
       - q * (q1b - q1a) * F(q1a + q1b, 2) - R_CF * xr_CF)
print("soma de momentos em A (deve ser 0) =", mom)


def V(x):
    v = float(VA)
    if x > xP1:
        v -= P1
    v -= q * (min(x, q1b) - q1a) if x > q1a else 0
    if x > xP2:
        v -= P2
    if x > xD:
        v += float(VD)
    if x > q2a:
        v -= q * (min(x, q2b) - q2a)
    if x > xE:
        v += float(VE)
    return v


def M(x):
    m = -float(MA) + float(VA) * x
    if x > xP1:
        m -= P1 * (x - xP1)
    if x > q1a:
        c = min(x, q1b) - q1a
        m -= q * c * (x - (q1a + c / 2))
    if x > xP2:
        m -= P2 * (x - xP2)
    if x > xD:
        m += float(VD) * (x - xD)
    if x > q2a:
        c = min(x, q2b) - q2a
        m -= q * c * (x - (q2a + c / 2))
    if x > xE:
        m += float(VE) * (x - xE)
    return m


eps = 1e-9
pontos = [xA, xP1, xB, xP2, xC, xD, xE, xF]
for x in pontos:
    print(f"x={x:>2}  V-={V(x - eps):8.3f}  V+={V(x + eps):8.3f}  M={M(x):8.3f}")

# zeros e extremos
u1 = float(VB) / q
print("BC: V=0 em x =", xB + u1, " M =", M(xB + u1))
u2 = V(xD + eps) / q
print("DE: V=0 em x =", xD + u2, " M =", M(xD + u2))
a, b, c = q / 2, -V(xD + eps), -M(xD)
d = (b * b - 4 * a * c) ** 0.5
z1, z2 = xD + (-b - d) / (2 * a), xD + (-b + d) / (2 * a)
print("DE: M=0 em x =", z1, z2)


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("-" if v < -1e-6 else "") + s


rot = ["A", "", "B", "", "C", "D", "E", ""]


def eixo(ax, titulo, unidade):
    ax.axhline(0, color="black", lw=1.2)
    ax.set_xlim(-0.8, 16.8)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.set_yticks([])
    ax.set_xticks(pontos)
    ax.set_xticklabels(rot)
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


azul, cor_r = "#1f5fbf", "#c0392b"


def movel(ax, x, y=0):
    ax.add_patch(Polygon([[x, y], [x - 0.3, y - 0.5], [x + 0.3, y - 0.5]], closed=True, fill=False, lw=1.5))
    ax.plot([x - 0.45, x + 0.45], [y - 0.5, y - 0.5], color="black", lw=1.5)
    base = y - 0.62
    ax.plot([x - 0.45, x + 0.45], [base, base], color="black", lw=1.5)
    for i in np.linspace(x - 0.4, x + 0.4, 6):
        ax.plot([i, i - 0.12], [base, base - 0.15], color="black", lw=0.8)


def engaste(ax, x, y=0):
    ax.plot([x, x], [y - 0.7, y + 0.7], color="black", lw=2)
    for j in np.linspace(y - 0.65, y + 0.65, 8):
        ax.plot([x, x - 0.18], [j, j - 0.15], color="black", lw=0.8)


def distribuida(ax, a, b, texto, y0=0.05, h=1.1, n=None):
    n = n or int((b - a) * 2) + 1
    ax.plot([a, b], [y0 + h - 0.05, y0 + h - 0.05], color=azul, lw=1)
    for x in np.linspace(a, b, n):
        ax.annotate("", (x, y0), xytext=(x, y0 + h - 0.05), arrowprops=dict(arrowstyle="->", color=azul, lw=1))
    ax.text((a + b) / 2, y0 + h + 0.1, texto, color=azul, fontsize=11, ha="center")


def forca(ax, x, texto, cor=azul, y0=0.05, h=2.2, para_baixo=True, lado=1):
    if para_baixo:
        ax.annotate("", (x, y0), xytext=(x, y0 + h), arrowprops=dict(arrowstyle="-|>", color=cor, lw=2.2))
    else:
        ax.annotate("", (x, y0), xytext=(x, y0 - h), arrowprops=dict(arrowstyle="-|>", color=cor, lw=2.2))
    ty = y0 + h - 0.3 if para_baixo else y0 - h + 0.1
    ax.text(x + 0.15 * lado, ty, texto, color=cor, fontsize=10, ha="left" if lado > 0 else "right")


def rotula(ax, x, y=0):
    ax.add_patch(Circle((x, y), 0.13, fill=True, fc="white", ec="black", lw=1.5, zorder=5))


# ---------- figura 1: estrutura e reacoes ----------
fig, ax = plt.subplots(figsize=(12, 4))
ax.set_xlim(-1.6, 17)
ax.set_ylim(-2.8, 3.2)
ax.axis("off")
ax.plot([xA, xF], [0, 0], color="black", lw=3)
engaste(ax, xA)
movel(ax, xD)
movel(ax, xE)
rotula(ax, xB)
rotula(ax, xC)
for x, n in [(xA, "A"), (xB, "B"), (xC, "C"), (xD, "D"), (xE, "E")]:
    ax.text(x + (0.18 if n in "ABC" else 0.4), 0.22 if n in "BC" else -0.45, n, fontsize=12)
distribuida(ax, q1a, q1b, "20 kN/m")
distribuida(ax, q2a, q2b, "20 kN/m")
forca(ax, xP1, "10 kN", lado=-1)
forca(ax, xP2, "10 kN")
# reacoes
forca(ax, xA + 0.35, "85 kN", cor=cor_r, y0=-0.75, h=1.3, para_baixo=False)
forca(ax, xD, f"{fmt(float(VD))} kN", cor=cor_r, y0=-0.85, h=1.2, para_baixo=False)
forca(ax, xE, f"{fmt(float(VE))} kN", cor=cor_r, y0=-0.85, h=1.2, para_baixo=False)
ax.add_patch(Arc((xA, 0), 1.6, 1.6, theta1=100, theta2=260, color=cor_r, lw=1.8))
ax.annotate("", (xA + 0.05, -0.8), xytext=(xA - 0.2, -0.77),
            arrowprops=dict(arrowstyle="-|>", color=cor_r, lw=1.6))
ax.text(xA - 1.5, 0.9, "M$_A$ = 280 kN.m", color=cor_r, fontsize=10)
ax.text(xA - 1.5, -2.0, "H$_A$ = 0", color=cor_r, fontsize=10)
for a, b in zip(pontos[:-1], pontos[1:]):
    ax.annotate("", (a, -2.5), xytext=(b, -2.5), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((a + b) / 2, -2.45, f"{b - a} m", ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex02-estrutura.png"), dpi=160)
plt.close(fig)

# ---------- figura 2: partes separadas nas rotulas ----------
fig, axs = plt.subplots(1, 3, figsize=(13, 3.6), gridspec_kw={"width_ratios": [4.6, 4.6, 8]})
for a in axs:
    a.axis("off")
    a.set_ylim(-2.2, 3.0)
cor_i = "#7d3c98"
# AB
a = axs[0]
a.set_xlim(-1.6, 5.4)
a.plot([0, 4], [0, 0], color="black", lw=3)
engaste(a, 0)
distribuida(a, 2, 4, "20 kN/m", n=5)
forca(a, 2, "10 kN", lado=-1)
forca(a, 4, "35 kN", cor=cor_i, h=1.6)
forca(a, 0.35, "85 kN", cor=cor_r, y0=-0.75, h=1.3, para_baixo=False)
a.text(-1.5, 0.9, "M$_A$ = 280", color=cor_r, fontsize=10)
a.set_title("Trecho AB (engastado)", fontsize=11)
# BC
a = axs[1]
a.set_xlim(3.4, 8.8)
a.plot([4, 8], [0, 0], color="black", lw=3)
rotula(a, 4)
rotula(a, 8)
distribuida(a, 4, 6, "20 kN/m", n=5)
forca(a, 6, "10 kN")
forca(a, 4, "35 kN", cor=cor_i, y0=-0.2, h=1.5, para_baixo=False)
forca(a, 8, "15 kN", cor=cor_i, y0=-0.2, h=1.5, para_baixo=False, lado=-1)
a.set_title("Trecho BC (entre rótulas), resolvido primeiro", fontsize=11)
# CF
a = axs[2]
a.set_xlim(7.4, 16.6)
a.plot([8, 16], [0, 0], color="black", lw=3)
rotula(a, 8)
movel(a, 10)
movel(a, 14)
distribuida(a, 10, 16, "20 kN/m")
forca(a, 8, "15 kN", cor=cor_i, h=1.6)
forca(a, 10, "52,50 kN", cor=cor_r, y0=-0.85, h=1.2, para_baixo=False)
forca(a, 14, "82,50 kN", cor=cor_r, y0=-0.85, h=1.2, para_baixo=False)
a.set_title("Trecho CE com balanço", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex02-partes.png"), dpi=160)
plt.close(fig)

# ---------- figura 3: N, V, M ----------
fig, (aN, aV, aM) = plt.subplots(3, 1, figsize=(12, 9.5), sharex=True, gridspec_kw={"height_ratios": [1, 3, 3]})

eixo(aN, "Esforço normal N", "kN")
aN.set_ylim(-1, 1)
aN.plot([xA, xF], [0, 0], color="#555", lw=3)
aN.text(8, 0.25, "N = 0 em toda a viga (não há força horizontal)", ha="center", fontsize=11)

eixo(aV, "Esforço cortante V", "kN")
cor = "#2471a3"
for a, b in [(xA, xP1), (xP1, xP2), (xP2, xD), (xD, xE), (xE, xF)]:
    xs, ys = segmento(V, a, b)
    preencher(aV, xs, ys, cor)
for x in [xA, xP1, xP2, xD, xE]:
    aV.plot([x, x], [V(x - eps) if x > 0 else 0, V(x + eps)], color=cor, lw=2)
rotulo(aV, 1, 85, "85", 4)
rotulo(aV, xP1 + 0.1, V(xP1 + eps), "75", 4, ha="left")
rotulo(aV, xB + 0.1, V(xB), "35 (B)", 4, ha="left")
rotulo(aV, 5.45, 0, "0 em x = 5,75", -6, ha="right")
rotulo(aV, xP2 - 0.1, V(xP2 - eps), "-5", -4, ha="right")
rotulo(aV, xP2 + 0.1, V(xP2 + eps), "-15", -6, ha="left")
rotulo(aV, xC, -15, "-15 (C)", -6)
rotulo(aV, xD - 0.1, V(xD - eps), "-15", -6, ha="right")
rotulo(aV, xD + 0.1, V(xD + eps), "37,50", 4, ha="left")
rotulo(aV, 11.78, 0, "0 em x = 11,88", -6, ha="right")
rotulo(aV, xE - 0.1, V(xE - eps), "-42,50", -6, ha="right")
rotulo(aV, xE + 0.1, V(xE + eps), "40", 4, ha="left")
rotulo(aV, xF, 0, "0", 4)
aV.set_ylim(-60, 105)

eixo(aM, "Momento fletor M", "kN.m, positivo desenhado embaixo")
cor = "#b03a2e"
for a, b in [(xA, xP1), (xP1, xB), (xB, xP2), (xP2, xD), (xD, xE), (xE, xF)]:
    xs, ys = segmento(M, a, b)
    preencher(aM, xs, ys, cor)
aM.plot([0, 0], [0, M(eps)], color=cor, lw=2)
rotulo(aM, xA + 0.1, M(eps), "-280", 4, ha="left")
rotulo(aM, xP1, M(xP1), "-110", 4)
rotulo(aM, xB, 0, "0 (rótula)", 4)
rotulo(aM, 5.6, M(5.75), "30,63 (x = 5,75)", -6, ha="right")
rotulo(aM, xP2 + 0.2, M(xP2), "30", -6, ha="left")
rotulo(aM, xC, 0, "0 (rótula)", 4)
rotulo(aM, xD, M(xD), "-30", 4)
rotulo(aM, z1 - 0.05, 0, "0 (11,16)", 4, ha="right")
rotulo(aM, 11.875, M(11.875), "5,16", -6)
rotulo(aM, z2 + 0.05, 0, "0 (12,59)", 4, ha="left")
rotulo(aM, xE, M(xE), "-40", 4)
rotulo(aM, xF, 0, "0", 4)
aM.set_ylim(60, -330)
aM.set_xlabel("x (m)")
aM.set_xticklabels(["A\n0", "\n2", "B\n4", "\n6", "C\n8", "D\n10", "E\n14", "\n16"])

fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex02-diagramas.png"), dpi=160)
plt.close(fig)
print("figuras salvas em", SAIDA)
