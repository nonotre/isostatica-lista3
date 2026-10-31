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

# exercicio 13: x em metros a partir da ponta esquerda A
xA, xB, xC, xD, xE, xF, xG = 0, 1, 2, 3, 4, 5, 6
P = 20      # forcas horizontais nas pontas da barra vertical (kN)
h = 1       # P em (2, +1) para a direita, Q em (2, -1) para a esquerda
q0 = 20     # carga triangular: 0 em x = 3 ate 20 kN/m em x = 6
L = xG - xD

# binario das duas forcas, horario
M0 = P * h + P * h


def q(x):
    return F(q0) * (x - xD) / L if x > xD else F(0)


def resultante(a, b):
    # resultante e momento em relacao a "a" da carga linear entre a e b (a >= 3)
    qa, qb = q(a), q(b)
    c = b - a
    R = (qa + qb) / 2 * c
    Ma = qa * c * c / 2 + (qb - qa) * c / 2 * (2 * c / F(3))
    return R, Ma


# trecho EG: soma de momentos na rotula E
R_EG, M_EG = resultante(F(xE), F(xG))
VF = M_EG / (xF - xE)
VE = R_EG - VF          # forca que a parte AE faz em EG (para cima positivo)
# parte AE: recebe -VE em E
R_DE, M_DE = resultante(F(xD), F(xE))
x_DE = xD + M_DE / R_DE
HB = P - P
# soma de momentos em B, anti-horario positivo, binario horario
VD = (R_DE * (x_DE - xB) + VE * (xE - xB) + M0) / (xD - xB)
VB = R_DE + VE - VD

for n, v in [("R_EG", R_EG), ("M_EG", M_EG), ("VF", VF), ("VE", VE), ("R_DE", R_DE),
             ("x_DE", x_DE), ("HB", HB), ("VD", VD), ("VB", VB), ("M0", M0)]:
    print(f"{n:5} = {str(v):>8} = {float(v):8.3f}")

# conferencia global
Rtot, _ = resultante(F(xD), F(xG))
print("soma Fy:", VB + VD + VF - Rtot)
print("soma M em B:", VD * 2 + VF * 4 - Rtot * (xD + F(2) - xB) - M0)


def V(x):
    v = 0.0
    if x > xB:
        v += float(VB)
    if x > xD:
        v += float(VD) - q0 * (x - xD) ** 2 / (2 * L)
    if x > xF:
        v += float(VF)
    return v


def M(x):
    m = 0.0
    if x > xB:
        m += float(VB) * (x - xB)
    if x > xC:
        m += M0
    if x > xD:
        m += float(VD) * (x - xD) - q0 * (x - xD) ** 3 / (6 * L)
    if x > xF:
        m += float(VF) * (x - xF)
    return m


eps = 1e-9
pontos = [xA, xB, xC, xD, xE, xF, xG]
for x in pontos:
    print(f"x={x}  V-={V(x - eps):8.3f}  V+={V(x + eps):8.3f}  M-={M(x - eps):8.3f}  M+={M(x + eps):8.3f}")
print("barra vertical: N = 0, V = 20, |M| em C = 20 (cada lado)")
print("no C: -M(C-) + M(C+) - 40 =", -M(xC - eps) + M(xC + eps) - 40)


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("−" if v < -1e-6 else "") + s


AZUL = "#1f5fbf"
VERM = "#c0392b"
ROXO = "#7d3c98"


def desenha_estrutura(ax, fino=False):
    lw = 1.6 if fino else 3
    cor = "#333" if fino else "black"
    ax.plot([xA, xG], [0, 0], color=cor, lw=lw, zorder=3)
    ax.plot([xC, xC], [-h, h], color=cor, lw=lw, zorder=3)
    ax.add_patch(Circle((xE, 0), 0.07, fc="white", ec=cor, lw=1.4, zorder=6))


def apoio(ax, x, fixo):
    ax.add_patch(Circle((x, -0.06), 0.06, fc="white", ec="black", lw=1.2, zorder=4))
    ax.add_patch(Polygon([[x, -0.12], [x - 0.18, -0.42], [x + 0.18, -0.42]], closed=True, fill=False, lw=1.4))
    base = -0.42 if fixo else -0.5
    if not fixo:
        ax.plot([x - 0.28, x + 0.28], [-0.42, -0.42], color="black", lw=1.4)
    ax.plot([x - 0.3, x + 0.3], [base, base], color="black", lw=1.4)
    for i in np.linspace(x - 0.27, x + 0.27, 7):
        ax.plot([i, i - 0.08], [base, base - 0.1], color="black", lw=0.8)


# ---------- figura 1: estrutura e reacoes ----------
fig, ax = plt.subplots(figsize=(11, 5))
ax.set_xlim(-0.8, 6.8)
ax.set_ylim(-2.1, 2.0)
ax.set_aspect("equal")
ax.axis("off")
desenha_estrutura(ax)
apoio(ax, xB, True)
apoio(ax, xD, False)
apoio(ax, xF, False)
for x, n, dx in [(xA, "A", -0.05), (xB, "B", 0.1), (xC, "C", 0.08), (xD, "D", -0.25), (xF, "F", 0.1),
                 (xG, "G", 0.05)]:
    ax.text(x + dx, 0.08, n, fontsize=12)
ax.text(xE + 0.05, -0.3, "E", fontsize=12)
ax.text(xC + 0.06, h - 0.05, "P", fontsize=12)
ax.text(xC - 0.08, -h, "Q", fontsize=12, ha="right", va="center")

# carga triangular
xs = np.linspace(xD, xG, 13)
ax.plot([xD, xG], [0.12, 0.12 + 0.8], color=AZUL, lw=1)
ax.plot([xD, xG], [0.12, 0.12], color=AZUL, lw=0.6)
for x in xs[1:]:
    top = 0.12 + 0.8 * (x - xD) / L
    ax.annotate("", (x, 0.04), xytext=(x, top), arrowprops=dict(arrowstyle="-|>", color=AZUL, lw=1))
ax.text(xG - 0.95, 1.05, "20 kN/m", color=AZUL, fontsize=11)
# forcas horizontais
ax.annotate("", (xC, h), xytext=(xC - 0.9, h), arrowprops=dict(arrowstyle="-|>", color=AZUL, lw=2.2))
ax.text(xC - 0.85, h + 0.1, "20 kN", color=AZUL, fontsize=11)
ax.annotate("", (xC + 0.9 - 0.9, -h), xytext=(xC + 0.9, -h), arrowprops=dict(arrowstyle="-|>", color=AZUL, lw=2.2))
ax.text(xC + 0.25, -h - 0.28, "20 kN", color=AZUL, fontsize=11)

# reacoes
ax.annotate("", (xB, -0.62), xytext=(xB, -1.4), arrowprops=dict(arrowstyle="<|-", color=VERM, lw=2))
ax.text(xB + 0.08, -1.35, "18,89 kN", color=VERM, fontsize=10)
for x, v in [(xD, VD), (xF, VF)]:
    ax.annotate("", (x, -0.62), xytext=(x, -1.4), arrowprops=dict(arrowstyle="-|>", color=VERM, lw=2))
    ax.text(x + 0.08, -1.35, f"{fmt(float(v))} kN", color=VERM, fontsize=10)
ax.text(xB - 0.95, -0.75, "H$_B$ = 0", color=VERM, fontsize=10)

for a, b in zip(pontos[:-1], pontos[1:]):
    ax.annotate("", (a, -1.85), xytext=(b, -1.85), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((a + b) / 2, -1.82, "1 m", ha="center", va="bottom", fontsize=9)
ax.annotate("", (-0.55, 0), xytext=(-0.55, h), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.annotate("", (-0.55, -h), xytext=(-0.55, 0), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(-0.62, 0.5, "1 m", rotation=90, ha="right", va="center", fontsize=9)
ax.text(-0.62, -0.5, "1 m", rotation=90, ha="right", va="center", fontsize=9)
ax.plot([-0.65, xC], [h, h], color="#aaa", lw=0.5, ls=":")
ax.plot([-0.65, xC], [-h, -h], color="#aaa", lw=0.5, ls=":")
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex13-estrutura.png"), dpi=160)
plt.close(fig)


# ---------- figura 2: N, V, M sobre a geometria ----------
def lab(ax, x, y, t, cor, ha="center", va="center"):
    ax.text(x, y, t, ha=ha, va=va, fontsize=10, color=cor, fontweight="bold",
            bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.5))


def painel(ax, titulo):
    ax.set_xlim(-0.6, 6.6)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titulo, loc="left", fontsize=12, fontweight="bold")
    desenha_estrutura(ax, fino=True)
    for x, n in [(xA, "A"), (xB, "B"), (xC, "C"), (xD, "D"), (xE, "E"), (xF, "F"), (xG, "G")]:
        ax.text(x, 0.06 if n not in "C" else -0.12, n, fontsize=9, color="#555",
                ha="center" if n != "C" else "left", va="bottom" if n != "C" else "top")
    ax.text(xC - 0.05, h, "P", fontsize=9, color="#555", ha="right", va="center")
    ax.text(xC - 0.05, -h, "Q", fontsize=9, color="#555", ha="right", va="center")


fig, (aN, aV, aM) = plt.subplots(3, 1, figsize=(11, 13))

painel(aN, "Esforço normal N (kN)")
lab(aN, 4.0, 0.7, "N = 0 na viga e na barra vertical", "black")
lab(aN, 4.0, 0.45, "(as duas forças de 20 kN se anulam no nó C, H$_B$ = 0)", "#444")

# cortante: viga com positivo para cima, escala s
painel(aV, "Esforço cortante V (kN)")
cor = "#2471a3"
s = 0.028
for a, b in [(xB, xD), (xD, xF), (xF, xG)]:
    xs = np.linspace(a + eps, b - eps, 200)
    ys = np.array([V(x) for x in xs]) * s
    aV.plot(xs, ys, color=cor, lw=2)
    aV.fill_between(xs, ys, 0, color=cor, alpha=0.18)
for x in [xB, xD, xF]:
    aV.plot([x, x], [V(x - eps) * s, V(x + eps) * s], color=cor, lw=2)
# barra vertical: V = +20 (sinal pela convencao do texto), desenhado a direita
w = 20 * s
aV.add_patch(Polygon([[xC, -h], [xC + w, -h], [xC + w, h], [xC, h]], closed=True, fc="none", ec=ROXO, lw=2,
                     hatch="///", alpha=0.8))
lab(aV, xC + w + 0.05, 0.55, "+20 (CP)", ROXO, ha="left")
lab(aV, xC + w + 0.05, -0.75, "+20 (QC)", ROXO, ha="left")
lab(aV, 1.5, V(1.5) * s - 0.15, "−18,89", cor)
lab(aV, xD + 0.05, V(xD + eps) * s + 0.12, "−1,11", cor, ha="left")
lab(aV, xE, V(xE) * s - 0.15, "−4,44", cor)
lab(aV, xF - 0.05, V(xF - eps) * s - 0.15, "−14,44", cor, ha="right")
lab(aV, xF + 0.05, V(xF + eps) * s + 0.13, "16,67", cor, ha="left")
lab(aV, xG, 0.12, "0", cor)
lab(aV, xA + 0.5, 0.12, "0", cor)
aV.text(-0.55, -1.35, "viga: V > 0 desenhado acima do eixo.  barra vertical percorrida de Q para P: V > 0 com a resultante abaixo da seção para a esquerda",
        fontsize=8.5, color="#444")

# momento: lado tracionado, positivo na viga embaixo
painel(aM, "Momento fletor M (kN.m), desenhado do lado tracionado")
cor = "#b03a2e"
s = 0.03
for a, b in [(xB, xC), (xC, xF), (xF, xG)]:
    xs = np.linspace(a + eps, b - eps, 300)
    ys = -np.array([M(x) for x in xs]) * s
    aM.plot(xs, ys, color=cor, lw=2)
    aM.fill_between(xs, ys, 0, color=cor, alpha=0.18)
aM.plot([xC, xC], [-M(xC - eps) * s, -M(xC + eps) * s], color=cor, lw=2)
# barra vertical: CQ tracionada a direita, CP tracionada a esquerda
w = 20 * s
aM.add_patch(Polygon([[xC, -h], [xC + w, 0], [xC, 0]], closed=True, fc="none", ec=ROXO, lw=2, hatch="///"))
aM.add_patch(Polygon([[xC, h], [xC - w, 0], [xC, 0]], closed=True, fc="none", ec=ROXO, lw=2, hatch="///"))
aM.annotate("CQ: 20 em C", (xC + w - 0.03, -0.03), xytext=(xC + 0.9, -0.95), color=ROXO, fontsize=10,
            fontweight="bold", arrowprops=dict(arrowstyle="->", color=ROXO))
aM.annotate("CP: 20 em C", (xC - w + 0.03, 0.03), xytext=(0.2, 0.95), color=ROXO, fontsize=10,
            fontweight="bold", arrowprops=dict(arrowstyle="->", color=ROXO))
lab(aM, xC - 0.05, M(xC - eps) * -s + 0.13, "−18,89", cor, ha="right")
lab(aM, xC + 0.08, -M(xC + eps) * s - 0.13, "21,11", cor, ha="left")
lab(aM, xD, -M(xD) * s - 0.16, "2,22", cor)
lab(aM, xE, -0.16, "0 (rótula)", cor)
lab(aM, xF, -M(xF) * s + 0.14, "−8,89", cor)
lab(aM, xG, -0.14, "0", cor)
lab(aM, xB, -0.14, "0", cor)
lab(aM, xA + 0.5, -0.14, "0", cor)
aM.text(-0.55, -1.35, "viga: M > 0 traciona embaixo e fica embaixo do eixo.  barra vertical: CQ tracionada à direita, CP tracionada à esquerda",
        fontsize=8.5, color="#444")
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex13-diagramas.png"), dpi=160)
plt.close(fig)


# ---------- figura 3: V e M da viga em grafico x ----------
def eixo(ax, titulo):
    ax.axhline(0, color="black", lw=1.2)
    ax.set_xlim(-0.4, 6.4)
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.set_yticks([])
    ax.set_xticks(pontos)
    ax.set_xticklabels([f"{n}\n{x}" for n, x in zip("ABCDEFG", pontos)])
    ax.set_title(titulo, loc="left", fontsize=12, fontweight="bold")
    for x in pontos:
        ax.axvline(x, color="#bbb", lw=0.6, ls=":", zorder=0)


def rot(ax, x, y, t, dy, cor, ha="center"):
    ax.annotate(t, (x, y), xytext=(0, dy), textcoords="offset points", ha=ha,
                va="bottom" if dy > 0 else "top", fontsize=10, color=cor, fontweight="bold")


fig, (aV, aM) = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)
eixo(aV, "Viga ACG: esforço cortante V (kN)")
cor = "#2471a3"
for a, b in [(xA, xB), (xB, xD), (xD, xF), (xF, xG)]:
    xs = np.linspace(a + eps, b - eps, 200)
    ys = np.array([V(x) for x in xs])
    aV.plot(xs, ys, color=cor, lw=2)
    aV.fill_between(xs, ys, 0, color=cor, alpha=0.18)
for x in [xB, xD, xF]:
    aV.plot([x, x], [V(x - eps), V(x + eps)], color=cor, lw=2)
rot(aV, 1.5, V(1.5), "−18,89", -6, cor)
rot(aV, xD + 0.05, V(xD + eps), "−1,11", 4, cor, ha="left")
rot(aV, xE, V(xE), "−4,44", -6, cor)
rot(aV, xF - 0.05, V(xF - eps), "−14,44", -6, cor, ha="right")
rot(aV, xF + 0.05, V(xF + eps), "16,67", 4, cor, ha="left")
rot(aV, xG, 0, "0", 4, cor)
rot(aV, 0.5, 0, "0", 4, cor)
aV.set_ylim(-26, 24)

eixo(aM, "Viga ACG: momento fletor M (kN.m), positivo desenhado embaixo")
cor = "#b03a2e"
for a, b in [(xA, xC), (xC, xF), (xF, xG)]:
    xs = np.linspace(a + eps, b - eps, 300)
    ys = np.array([M(x) for x in xs])
    aM.plot(xs, ys, color=cor, lw=2)
    aM.fill_between(xs, ys, 0, color=cor, alpha=0.18)
aM.plot([xC, xC], [M(xC - eps), M(xC + eps)], color=cor, lw=2)
rot(aM, xC - 0.05, M(xC - eps), "−18,89", 4, cor, ha="right")
rot(aM, xC + 0.07, M(xC + eps), "21,11", -6, cor, ha="left")
rot(aM, xD, M(xD), "2,22", -6, cor)
rot(aM, xE, 0, "0 (rótula)", 4, cor)
rot(aM, xF, M(xF), "−8,89", 4, cor)
rot(aM, xG, 0, "0", 4, cor)
rot(aM, xB, 0, "0", -6, cor)
aM.set_ylim(30, -28)
aM.set_xlabel("x (m)")
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex13-viga.png"), dpi=160)
plt.close(fig)
print("figuras salvas em", SAIDA)
