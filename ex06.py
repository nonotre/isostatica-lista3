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

# exercicio 06: tesoura triarticulada com tirante
# A(0,0) apoio fixo, B(8,0) apoio movel, C(4,3) rotula, tirante D(2;1,5)-E(6;1,5)
A, D, C, E, B = (0, F(0)), (2, F(3, 2)), (4, F(3)), (6, F(3, 2)), (8, F(0))
P = 10  # kN em D, C e E

# global
HA = F(0)
VB = (P * 2 + P * 4 + P * 6) / F(8)  # momentos em A
VA = 3 * P - VB
# metade esquerda (A ate C), momentos em C, tirante a 1,5 m abaixo de C
T = (VA * 4 - P * 2 - HA * 3) / F(3, 2)
HC = -(HA + T)        # forca da direita sobre a esquerda em C (horizontal)
VC = -(VA - P)        # forca do pino sobre a barra esquerda (vertical)

print("HA =", HA, " VA =", VA, " VB =", VB)
print("T =", T, float(T))
print("pino C sobre barra esquerda: H =", HC, float(HC), " V =", VC)

# direcoes das barras (comprimento 2,5 m por trecho)
c, s = F(4, 5), F(3, 5)
L = F(5, 2)
barras = {
    "AD": dict(ini=A, t=(c, s), R=(HA, VA)),
    "DC": dict(ini=D, t=(c, s), R=(HA + T, VA - P)),
    "CE": dict(ini=C, t=(c, -s), R=(-HC, VC)),
    "EB": dict(ini=E, t=(c, -s), R=(-HC - T, VC - P)),
}
# M no inicio de cada trecho (percurso da esquerda para a direita)
M0 = {"AD": F(0), "CE": F(0)}


def esforcos(nome):
    b = barras[nome]
    tx, ty = b["t"]
    nx, ny = -ty, tx  # normal a esquerda do percurso (para cima)
    Rx, Ry = b["R"]
    N = -(Rx * tx + Ry * ty)
    V = Rx * nx + Ry * ny
    return N, V


res = {}
for nome in ["AD", "DC", "CE", "EB"]:
    N, V = esforcos(nome)
    if nome == "DC":
        M0["DC"] = res["AD"][3]
    if nome == "EB":
        M0["EB"] = res["CE"][3]
    Mi = M0[nome]
    Mf = Mi + V * L
    res[nome] = (N, V, Mi, Mf)
    print(f"{nome}: N={float(N):8.3f}  V={float(V):8.3f}  M_ini={float(Mi):8.3f}  M_fim={float(Mf):8.3f}")
print("tirante DE: N =", float(T))

# conferencias
assert res["DC"][3] == 0 and res["CE"][2] == 0
assert res["EB"][3] == 0
print("soma Fy =", VA + VB - 3 * P, " soma M_A =", VB * 8 - P * (2 + 4 + 6))


def fmt(v):
    s_ = f"{abs(v):.2f}".replace(".", ",")
    if s_.endswith(",00"):
        s_ = s_[:-3]
    return ("−" if v < -1e-6 else "") + s_


pts = {k: (float(v[0]), float(v[1])) for k, v in dict(A=A, D=D, C=C, E=E, B=B).items()}


def quadro(ax, ylim=(-1.6, 4.4)):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.3, 9.3)
    ax.set_ylim(*ylim)
    for a, b in [("A", "C"), ("C", "B")]:
        ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]], color="black", lw=2.6, zorder=3)
    ax.plot([pts["D"][0], pts["E"][0]], [pts["D"][1], pts["E"][1]], color="black", lw=1, zorder=3)
    for k in ["C", "D", "E"]:
        ax.add_patch(Circle(pts[k], 0.09, fc="white", ec="black", lw=1.3, zorder=6))


def apoio(ax, x, y, fixo):
    ax.add_patch(Polygon([[x, y], [x - 0.25, y - 0.42], [x + 0.25, y - 0.42]], closed=True, fill=False, lw=1.3))
    ax.add_patch(Circle((x, y), 0.08, fc="white", ec="black", lw=1.2, zorder=6))
    base = y - 0.42 if fixo else y - 0.55
    if not fixo:
        ax.plot([x - 0.38, x + 0.38], [y - 0.42, y - 0.42], color="black", lw=1.3)
    ax.plot([x - 0.4, x + 0.4], [base, base], color="black", lw=1.3)
    for i in np.linspace(x - 0.36, x + 0.36, 6):
        ax.plot([i, i - 0.1], [base, base - 0.13], color="black", lw=0.7)


# ---------- figura 1: estrutura e reacoes ----------
fig, ax = plt.subplots(figsize=(10, 6.2))
quadro(ax, (-2.6, 4.8))
apoio(ax, 0, 0, True)
apoio(ax, 8, 0, False)
for k, dx, dy in [("A", -0.45, 0.1), ("B", 0.25, 0.1), ("C", 0.2, 0.15), ("D", -0.45, -0.05), ("E", 0.25, -0.05)]:
    ax.text(pts[k][0] + dx, pts[k][1] + dy, k, fontsize=13)
azul = "#1f5fbf"
for k in ["D", "C", "E"]:
    x, y = pts[k]
    ax.annotate("", (x, y + 0.12), xytext=(x, y + 1.3), arrowprops=dict(arrowstyle="-|>", color=azul, lw=2))
    ax.text(x + 0.12, y + 1.0, "10 kN", color=azul, fontsize=11)
ax.text(4, 1.2, f"tirante DE: N = {fmt(float(T))} kN (tração)", ha="center", fontsize=10.5, color="#6c3483")
vermelho = "#c0392b"
for x in [0, 8]:
    ax.annotate("", (x, -0.75), xytext=(x, -1.8), arrowprops=dict(arrowstyle="-|>", color=vermelho, lw=2))
    ax.text(x + 0.15, -1.5, "15 kN", color=vermelho, fontsize=11)
ax.text(-1.25, -1.0, "H$_A$ = 0", color=vermelho, fontsize=11)
for a, b in [(0, 2), (2, 4), (4, 6), (6, 8)]:
    ax.annotate("", (a, -2.3), xytext=(b, -2.3), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((a + b) / 2, -2.25, "2 m", ha="center", va="bottom", fontsize=9)
for a, b in [(0, 1.5), (1.5, 3)]:
    ax.annotate("", (8.9, a), xytext=(8.9, b), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(8.97, (a + b) / 2, "1,5 m", va="center", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex06-estrutura.png"), dpi=160)
plt.close(fig)

# ---------- figura 2: diagramas sobre a geometria ----------
trechos = [("AD", "A", "D"), ("DC", "D", "C"), ("CE", "C", "E"), ("EB", "E", "B")]


def normal(nome):
    tx, ty = barras[nome]["t"]
    return np.array([-float(ty), float(tx)])


def desenhar(ax, valores, escala, cor, lado, rotulos):
    """valores[nome] = (v_ini, v_fim); lado = +1 desenha positivo para o lado de n, -1 oposto"""
    for nome, a, b in trechos:
        p0, p1 = np.array(pts[a]), np.array(pts[b])
        n = normal(nome)
        vi, vf = valores[nome]
        q0 = p0 + lado * escala * vi * n
        q1 = p1 + lado * escala * vf * n
        poly = np.array([p0, q0, q1, p1])
        ax.add_patch(Polygon(poly, closed=True, fc=cor, alpha=0.22, ec="none", zorder=1))
        ax.plot([p0[0], q0[0], q1[0], p1[0]], [p0[1], q0[1], q1[1], p1[1]], color=cor, lw=1.8, zorder=2)
    for (x, y, txt, ha) in rotulos:
        ax.text(x, y, txt, ha=ha, va="center", fontsize=10.5, fontweight="bold", color="black", zorder=8)


fig, axs = plt.subplots(3, 1, figsize=(10, 15.5))

# N: modulo desenhado para fora das barras inclinadas, sinal escrito
aN = axs[0]
quadro(aN, (-0.6, 4.4))
eN = 0.03
valN = {k: (abs(float(res[k][0])), abs(float(res[k][0]))) for k in res}
desenhar(aN, valN, eN, "#7d3c98", +1, [])
aN.add_patch(Polygon([[2, 1.5], [2, 1.5 - eN * float(T)], [6, 1.5 - eN * float(T)], [6, 1.5]],
                     closed=True, fc="#27ae60", alpha=0.3, ec="#27ae60", lw=1.5, zorder=1))
aN.text(4, 1.5 - eN * float(T) / 2, f"+{fmt(float(T))} (tirante, tração)", ha="center", va="center",
        fontsize=10.5, fontweight="bold")
for nome, a, b in trechos:
    mid = (np.array(pts[a]) + np.array(pts[b])) / 2
    n_ = float(res[nome][0])
    aN.text(*(mid + normal(nome) * eN * abs(n_) / 2), fmt(n_), ha="center", va="center", fontsize=10.5,
            fontweight="bold", rotation=36.87 if nome in ("AD", "DC") else -36.87)
aN.set_title("Esforço normal N (kN), negativo = compressão", loc="left", fontsize=12, fontweight="bold")

# V: positivo desenhado para fora (lado da normal n, para cima)
aV = axs[1]
quadro(aV, (-0.9, 4.2))
valV = {k: (float(res[k][1]), float(res[k][1])) for k in res}
desenhar(aV, valV, 0.04, "#2471a3", +1, [])
for nome, a, b in trechos:
    mid = (np.array(pts[a]) + np.array(pts[b])) / 2
    v = float(res[nome][1])
    pos = mid + normal(nome) * 0.04 * v / 2
    sinal = "+" if v > 0 else "−"
    aV.text(*pos, f"{sinal}{fmt(abs(v))}", ha="center", va="center", fontsize=10.5, fontweight="bold",
            rotation=36.87 if nome in ("AD", "DC") else -36.87)
aV.set_title("Esforço cortante V (kN), positivo desenhado para cima/fora", loc="left", fontsize=12, fontweight="bold")
aV.text(4, 1.62, "V = 0 no tirante", ha="center", fontsize=10)

# M: positivo traciona embaixo (lado oposto a n), desenhado do lado tracionado
aM = axs[2]
quadro(aM, (-1.6, 4.0))
valM = {k: (float(res[k][2]), float(res[k][3])) for k in res}
desenhar(aM, valM, 0.04, "#b03a2e", -1, [])
for k, nome in [("D", "AD"), ("E", "CE")]:
    p = np.array(pts[k]) - normal(nome if k == "D" else "EB") * 0.04 * 30
    aM.plot([pts[k][0], p[0]], [pts[k][1], p[1]], color="#b03a2e", lw=1, ls=":")
aM.text(2 + 0.72, 1.5 - 1.2, "30", ha="left", va="center", fontsize=11, fontweight="bold")
aM.text(6 - 0.72, 1.5 - 1.2, "30", ha="right", va="center", fontsize=11, fontweight="bold")
aM.text(4.25, 3.15, "0 (rótula)", ha="left", fontsize=10.5, fontweight="bold")
aM.text(0.2, -0.35, "0", fontsize=10.5, fontweight="bold")
aM.text(7.65, -0.35, "0", fontsize=10.5, fontweight="bold")
aM.text(4, 1.75, "M = 0 no tirante", ha="center", fontsize=10)
aM.set_title("Momento fletor M (kN.m), desenhado do lado tracionado (dentro)", loc="left", fontsize=12, fontweight="bold")

for ax_ in axs:
    for k, dx, dy in [("A", -0.4, 0.0), ("B", 0.2, 0.0), ("C", -0.08, 0.25), ("D", -0.4, 0.05), ("E", 0.2, 0.05)]:
        ax_.text(pts[k][0] + dx, pts[k][1] + dy, k, fontsize=12, color="#444")
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex06-diagramas.png"), dpi=150)
plt.close(fig)
print("figuras salvas em", SAIDA)
