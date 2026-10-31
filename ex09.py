from fractions import Fraction as F
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Circle, Arc

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "figuras")
os.makedirs(SAIDA, exist_ok=True)

# exercicio 09: coordenadas (x, y) em metros, origem na base do apoio C deslocada: x = 0 em A, y = 0 em C
A = (F(0), F(2))
H1 = (F(3, 2), F(4))   # ponta esquerda do tirante, no meio da barra inclinada
D = (F(3), F(6))       # canto
B = (F(6), F(6))       # luva
E = (F(6), F(4))       # ponta direita do tirante, na coluna, onde nasce o balanco
P = (F(7), F(4))       # ponta do balanco
C = (F(6), F(0))
q = 10      # kN/m vertical, por metro de projecao horizontal, de x = 0 a x = 6
P6 = 6      # kN em D
FH = 20     # kN horizontal para a direita em H1
FP = 20     # kN para baixo na ponta do balanco


def mz(ponto, ref, f):
    # momento anti-horario de f aplicada em ponto, em relacao a ref
    return (ponto[0] - ref[0]) * f[1] - (ponto[1] - ref[1]) * f[0]


# luva em B: nao transmite forca horizontal, transmite forca vertical e momento
# coluna BC + balanco: soma de forcas em x
T = F(0)  # forca no tirante (tracao positiva)
# estrutura inteira
HA = -FH
cargas_mz_A = (mz((F(3), 0), A, (0, -q * 6)) + mz(D, A, (0, -P6)) + mz(P, A, (0, -FP))
               + mz(H1, A, (FH, 0)))
VC = -cargas_mz_A / (C[0] - A[0])
VA = q * 6 + P6 + FP - VC
# coluna isolada: forcas em y e momentos em B
VBc = FP - VC                        # forca da luva sobre a coluna (para cima positivo)
MBc = -(mz(P, B, (0, -FP)) + mz(C, B, (0, VC)))  # momento da luva sobre a coluna (anti-horario +)

print("HA =", HA, " VA =", VA, float(VA), " VC =", VC, float(VC))
print("tirante T =", T)
print("luva sobre a coluna: V =", VBc, " M =", MBc, "(anti-horario +)")

# conferencia do corpo 1 (A-H1-D-B)
fx = HA + FH + T
fy = VA - q * 6 - P6 - VBc
m = (mz(H1, A, (FH + T, 0)) + mz((F(3), 0), A, (0, -q * 6)) + mz(D, A, (0, -P6))
     + mz(B, A, (0, -VBc)) - MBc)
print("corpo 1: SFx =", fx, " SFy =", fy, " SMA =", m)

# alternativa: B como rotula
Tr = mz(P, B, (0, -FP)) / 2   # -2T - 20 = 0
print("alternativa rotula: T =", Tr, " HB =", Tr, " VB =", FP - VC)


# ---------- esforcos por barra ----------
def unit(p0, p1):
    d = np.array([float(p1[0] - p0[0]), float(p1[1] - p0[1])])
    L = np.hypot(*d)
    return d / L, L


def corpo1(S, depois_de):
    # resultante e momento (anti-horario, em S) das forcas no corpo 1 antes da secao S
    # depois_de: conjunto de pontos de carga ja ultrapassados
    R = [float(HA), float(VA)]
    M = float(mz(A, S, (HA, VA)))
    if "H1" in depois_de:
        R[0] += float(FH + T)
        M += float(mz(H1, S, (FH + T, 0)))
    if "D" in depois_de:
        R[1] -= P6
        M += float(mz(D, S, (0, -P6)))
    x = float(S[0])
    R[1] -= q * x
    M += -q * x * (x / 2 - x)  # resultante q x em x/2
    return np.array(R), M


def esforcos(barra, s, lado=+1):
    # retorna N, V, M na secao a s metros do inicio da barra
    # lado = -1 avalia logo antes de uma carga concentrada, +1 logo depois
    p0, p1, _ = BARRAS[barra]
    t, L = unit(p0, p1)
    n = np.array([-t[1], t[0]])
    S = (float(p0[0]) + s * t[0], float(p0[1]) + s * t[1])
    eps = 1e-9 * lado
    if barra == "AD":
        dep = set()
        if s + eps > 2.5:
            dep.add("H1")
        R, Mz = corpo1(S, dep)
    elif barra == "DB":
        R, Mz = corpo1(S, {"H1", "D"})
    elif barra == "CB":
        R = np.array([0.0, float(VC)])
        Mz = 0.0
        if s + eps > 4:
            R += np.array([-float(T), -FP])
            Mz += float(mz(E, S, (-T, 0))) + float(mz(P, S, (0, -FP)))
    elif barra == "EP":
        # pela frente: so a forca na ponta
        Rf = np.array([0.0, -FP])
        Mzf = float(mz(P, S, (0, -FP)))
        R, Mz = -Rf, -Mzf
    elif barra == "tirante":
        R = np.array([-float(T), 0.0])
        Mz = 0.0
    N = -R @ t
    V = R @ n
    M = -Mz
    return N, V, M


BARRAS = {
    "AD": (A, D, "A → D"),
    "DB": (D, B, "D → B"),
    "CB": (C, B, "C → B"),
    "EP": (E, P, "E → ponta"),
    "tirante": (H1, E, "H1 → E"),
}

chaves = [
    ("AD", 0, +1, "A"), ("AD", 4 / 3, +1, "N = 0"), ("AD", 2.5, -1, "H1-"), ("AD", 2.5, +1, "H1+"),
    ("AD", 2.5 + 4 / 3, +1, "N = 0"), ("AD", 2.5 + 4 / 3, +1, "V = 0"), ("AD", 5, -1, "D"),
    ("DB", 0, +1, "D"), ("DB", 2.5066, +1, "M = 0"), ("DB", 3, -1, "B"),
    ("CB", 0, +1, "C"), ("CB", 4, -1, "E-"), ("CB", 4, +1, "E+"), ("CB", 6, -1, "B"),
    ("EP", 0, +1, "E"), ("EP", 1, -1, "ponta"),
    ("tirante", 0, +1, "H1"),
]
for b, s, lado, nome in chaves:
    N, V, M = esforcos(b, s, lado)
    print(f"{b:8s} s={s:6.3f} {nome:6s} N={N:8.3f} V={V:8.3f} M={M:8.3f}")

# zero de M em DB: 5u^2 + 13u - 64 = 0
u0 = (-13 + np.sqrt(13 ** 2 + 4 * 5 * 64)) / 10
print("M = 0 em DB, u =", u0, " x =", 3 + u0)
print("M max em AD:", esforcos("AD", 2.5 + 4 / 3)[2])

# equilibrio de momentos nos nos
print("no D: M(AD) =", esforcos("AD", 5, -1)[2], " M(DB) =", esforcos("DB", 0)[2])
print("no E: M(CB-) =", esforcos("CB", 4, -1)[2], " M(CB+) =", esforcos("CB", 4, +1)[2],
      " M(EP) =", esforcos("EP", 0)[2])


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("−" if v < -1e-6 else "") + s


def pt(p):
    return float(p[0]), float(p[1])


cor_c = "#1f5fbf"
cor_r = "#c0392b"


def desenha_estrutura(ax, tirante=True):
    for p0, p1 in [(A, D), (D, (F(59, 10), F(6)))]:
        ax.plot(*zip(pt(p0), pt(p1)), color="black", lw=4, solid_capstyle="round")
    ax.plot([6, 6], [0, 5.9], color="black", lw=4, solid_capstyle="round")
    ax.plot([6, 7], [4, 4], color="black", lw=4, solid_capstyle="round")
    # luva
    ax.plot([5.8, 6.3], [6.12, 6.12], color="black", lw=1.4)
    ax.plot([5.8, 6.3], [5.88, 5.88], color="black", lw=1.4)
    if tirante:
        ax.plot([1.5, 6], [4, 4], color="#555", lw=1.6)
        for p in (H1, E):
            ax.add_patch(Circle(pt(p), 0.09, fc="white", ec="black", lw=1.3, zorder=5))


def apoio(ax, p, movel):
    x, y = pt(p)
    ax.add_patch(Circle((x, y), 0.09, fc="white", ec="black", lw=1.3, zorder=5))
    ax.add_patch(Polygon([[x, y - 0.09], [x - 0.3, y - 0.55], [x + 0.3, y - 0.55]], closed=True, fill=False, lw=1.4))
    base = y - 0.55
    if movel:
        ax.plot([x - 0.45, x + 0.45], [base, base], color="black", lw=1.4)
        base -= 0.12
    ax.plot([x - 0.45, x + 0.45], [base, base], color="black", lw=1.0)
    for i in np.linspace(x - 0.4, x + 0.4, 7):
        ax.plot([i, i - 0.12], [base, base - 0.15], color="black", lw=0.8)


def seta(ax, xy_ponta, xy_cauda, cor, lw=2):
    ax.annotate("", xy_ponta, xytext=xy_cauda, arrowprops=dict(arrowstyle="-|>", color=cor, lw=lw))


# ---------- figura 1: estrutura e reacoes ----------
fig, ax = plt.subplots(figsize=(9.5, 8))
ax.set_aspect("equal")
ax.axis("off")
desenha_estrutura(ax)
apoio(ax, A, False)
apoio(ax, C, True)
for p, nome, dx, dy in [(A, "A", -0.45, 0.05), (H1, "H1", -0.55, 0.15), (D, "D", -0.2, 0.2),
                        (B, "B", 0.4, 0.15), (E, "E", -0.45, 0.15), (C, "C", -0.45, 0.1)]:
    ax.text(float(p[0]) + dx, float(p[1]) + dy, nome, fontsize=12)
ax.text(3.4, 3.7, "tirante (biela) H1E", fontsize=9, color="#555", ha="center", va="top")
ax.text(6.35, 6.35, "luva", fontsize=9, color="#555")
# carga distribuida
yq = 7.0
ax.plot([0, 6], [yq, yq], color=cor_c, lw=1)
for x in np.linspace(0, 6, 17):
    ytopo = 2 + 4 * x / 3 if x <= 3 else 6
    seta(ax, (x, ytopo + 0.08), (x, yq), cor_c, lw=0.9)
ax.text(4.3, yq + 0.15, "10 kN/m (por metro horizontal)", color=cor_c, fontsize=10)
seta(ax, (3, 6.1), (3, 7.9), cor_c, lw=2.2)
ax.text(2.2, 7.9, "6 kN", color=cor_c, fontsize=11)
seta(ax, (1.42, 4), (0.0, 4), cor_c, lw=2.2)
ax.text(-0.1, 4.15, "20 kN", color=cor_c, fontsize=11)
seta(ax, (7, 4.05), (7, 5.3), cor_c, lw=2.2)
ax.text(7.1, 5.0, "20 kN", color=cor_c, fontsize=11)
# reacoes
seta(ax, (-1.4, 2), (-0.12, 2), cor_r)
ax.text(-1.6, 1.7, "H$_A$ = 20 kN", color=cor_r, fontsize=10)
seta(ax, (0, 1.35), (0, 0.0), cor_r)
ax.text(0.12, 0.25, "V$_A$ = 23 kN", color=cor_r, fontsize=10)
seta(ax, (6, -0.7), (6, -1.9), cor_r)
ax.text(6.15, -1.7, "V$_C$ = 63 kN", color=cor_r, fontsize=10)
# cotas
yc = -2.4
for a, b in [(0, 1.5), (1.5, 3), (3, 6), (6, 7)]:
    ax.annotate("", (a, yc), xytext=(b, yc), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((a + b) / 2, yc + 0.05, fmt(b - a).replace(",50", ",5") + " m", ha="center", va="bottom", fontsize=9)
xc = 8.2
for a, b in [(0, 2), (2, 4), (4, 6)]:
    ax.annotate("", (xc, a), xytext=(xc, b), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(xc + 0.1, (a + b) / 2, f"{b - a} m", va="center", fontsize=9)
ax.set_xlim(-1.8, 9)
ax.set_ylim(-2.8, 8.3)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex09-estrutura.png"), dpi=150)
plt.close(fig)

# ---------- figura 2: corpos livres ----------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 6.2), gridspec_kw={"width_ratios": [1.5, 1]})
for a in (a1, a2):
    a.set_aspect("equal")
    a.axis("off")
# corpo 1
a1.plot([0, 3, 6], [2, 6, 6], color="black", lw=4, solid_capstyle="round")
a1.plot([0, 6], [6.9, 6.9], color=cor_c, lw=1)
for x in np.linspace(0, 6, 13):
    ytopo = 2 + 4 * x / 3 if x <= 3 else 6
    seta(a1, (x, ytopo + 0.08), (x, 6.9), cor_c, lw=0.8)
a1.text(0.3, 7.05, "10 kN/m", color=cor_c, fontsize=10)
seta(a1, (3, 6.1), (3, 7.7), cor_c, lw=2)
a1.text(3.12, 7.45, "6 kN", color=cor_c, fontsize=10)
seta(a1, (1.42, 4), (0.1, 4), cor_c, lw=2)
a1.text(0.0, 4.15, "20 kN", color=cor_c, fontsize=10)
a1.text(1.65, 3.55, "T = 0", color="#555", fontsize=10)
seta(a1, (-1.3, 2), (-0.1, 2), cor_r)
a1.text(-1.4, 2.15, "20 kN", color=cor_r, fontsize=10)
seta(a1, (0, 1.9), (0, 0.7), cor_r)
a1.text(0.12, 0.85, "23 kN", color=cor_r, fontsize=10)
seta(a1, (6, 5.9), (6, 4.6), "#7d3c98")
a1.text(6.12, 4.8, "43 kN", color="#7d3c98", fontsize=10)
a1.add_patch(Arc((6, 6), 0.9, 0.9, theta1=-40, theta2=200, color="#7d3c98", lw=1.6))
seta(a1, (6.33, 5.67), (6.42, 5.78), "#7d3c98", lw=1.6)
a1.text(6.4, 6.4, "20 kN.m", color="#7d3c98", fontsize=10)
a1.text(3.4, 3.0, "Corpo 1: A, H1, D, B", fontsize=11, fontweight="bold")
a1.set_xlim(-1.6, 7.6)
a1.set_ylim(0.4, 8)
# corpo 2
a2.plot([6, 6], [0, 6], color="black", lw=4, solid_capstyle="round")
a2.plot([6, 7], [4, 4], color="black", lw=4, solid_capstyle="round")
seta(a2, (7, 4.05), (7, 5.3), cor_c, lw=2)
a2.text(7.1, 5.0, "20 kN", color=cor_c, fontsize=10)
seta(a2, (6, 6.05), (6, 7.3), "#7d3c98")
a2.text(6.12, 7.0, "43 kN", color="#7d3c98", fontsize=10)
a2.add_patch(Arc((6, 6), 0.9, 0.9, theta1=-20, theta2=220, color="#7d3c98", lw=1.6))
seta(a2, (5.67, 5.67), (5.58, 5.78), "#7d3c98", lw=1.6)
a2.text(4.5, 6.4, "20 kN.m", color="#7d3c98", fontsize=10)
a2.text(5.1, 3.6, "T = 0", color="#555", fontsize=10)
seta(a2, (6, -0.05), (6, -1.3), cor_r)
a2.text(6.12, -1.0, "63 kN", color=cor_r, fontsize=10)
a2.text(4.4, 1.5, "Corpo 2:\nB, E, C\ne balanço", fontsize=11, fontweight="bold")
a2.set_xlim(4.2, 8)
a2.set_ylim(-1.6, 7.6)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex09-partes.png"), dpi=150)
plt.close(fig)


# ---------- figuras 3 a 5: diagramas sobre o portico ----------
def curva(barra, idx, escala, sinal_desenho, trechos):
    p0, p1, _ = BARRAS[barra]
    t, L = unit(p0, p1)
    n = np.array([-t[1], t[0]])
    xs, ys = [], []
    out = []
    for a, b in trechos:
        ss = np.linspace(a, b, 120)
        vals = []
        for i, s in enumerate(ss):
            lado = +1 if i == 0 else -1
            vals.append(esforcos(barra, s, lado)[idx])
        out.append((ss, np.array(vals)))
    return out, t, n, p0


def desenha_diagrama(ax, barra, idx, escala, sinal, trechos, cor):
    out, t, n, p0 = curva(barra, idx, escala, sinal, trechos)
    x0, y0 = pt(p0)
    for ss, vals in out:
        base = np.array([[x0 + s * t[0], y0 + s * t[1]] for s in ss])
        off = base + np.outer(vals * escala * sinal, n)
        poly = np.vstack([base, off[::-1]])
        ax.add_patch(Polygon(poly, closed=True, fc=cor, alpha=0.2, ec="none"))
        ax.plot(off[:, 0], off[:, 1], color=cor, lw=1.8)
        for k in (0, -1):
            ax.plot([base[k, 0], off[k, 0]], [base[k, 1], off[k, 1]], color=cor, lw=1.2)


def rot(ax, barra, s, lado, idx, escala, sinal, texto, extra=0.25, ha="center", va="center", dx=0, dy=0):
    p0, p1, _ = BARRAS[barra]
    t, L = unit(p0, p1)
    n = np.array([-t[1], t[0]])
    v = esforcos(barra, s, lado)[idx]
    d = v * escala * sinal
    dirr = np.sign(d) if abs(d) > 1e-9 else 1
    pos = np.array([float(p0[0]), float(p0[1])]) + s * t + n * (d + dirr * extra)
    ax.text(pos[0] + dx, pos[1] + dy, texto, ha=ha, va=va, fontsize=10, fontweight="bold",
            bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.5))


def base_portico(ax, titulo):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot([0, 3, 6], [2, 6, 6], color="black", lw=2.2)
    ax.plot([6, 6], [0, 6], color="black", lw=2.2)
    ax.plot([6, 7], [4, 4], color="black", lw=2.2)
    ax.plot([1.5, 6], [4, 4], color="#777", lw=1.0, ls="--")
    for p, nome, dx, dy in [(A, "A", -0.4, -0.3), (H1, "H1", -0.55, 0.0), (D, "D", -0.35, 0.15),
                            (B, "B", 0.15, 0.25), (E, "E", -0.35, -0.3), (C, "C", -0.4, -0.1),
                            (P, "ponta", 0.1, 0.12)]:
        ax.text(float(p[0]) + dx, float(p[1]) + dy, nome, fontsize=11, color="#333")
    ax.set_title(titulo, loc="left", fontsize=12, fontweight="bold")
    ax.set_xlim(-1.5, 8.5)
    ax.set_ylim(-0.8, 8.0)


# N: positivo desenhado do lado n (esquerda de quem percorre a barra)
fig, ax = plt.subplots(figsize=(9, 7.4))
base_portico(ax, "Esforço normal N (kN), tração +")
eN = 1.1 / 63
cN = "#1e8449"
desenha_diagrama(ax, "AD", 0, eN, 1, [(0, 2.5), (2.5, 5)], cN)
desenha_diagrama(ax, "CB", 0, eN, 1, [(0, 4), (4, 6)], cN)
rot(ax, "AD", 0, +1, 0, eN, 1, "−6,4", extra=0.35, dx=0.25, dy=-0.2)
rot(ax, "AD", 2.5, -1, 0, eN, 1, "+5,6", extra=0.4, dx=-0.15)
rot(ax, "AD", 2.5, +1, 0, eN, 1, "−6,4", extra=0.3, dx=0.25, dy=-0.1)
rot(ax, "AD", 5, -1, 0, eN, 1, "+5,6", extra=0.35, dx=-0.45, dy=-0.1)
rot(ax, "AD", 4 / 3, +1, 0, eN, 1, "0 (s = 1,33)", extra=0.75, dx=-0.6, dy=0.1)
rot(ax, "AD", 2.5 + 4 / 3, +1, 0, eN, 1, "0 (s = 3,83)", extra=0.6, dx=-0.7, dy=0.1)
rot(ax, "CB", 2, +1, 0, eN, 1, "−63", extra=0.35, ha="left")
rot(ax, "CB", 5, +1, 0, eN, 1, "−43", extra=0.35, ha="left", dy=0.3)
ax.text(4.5, 6.35, "N = 0 em DB", ha="center", fontsize=10, fontweight="bold")
ax.text(7.25, 3.55, "N = 0 no balanço", ha="left", fontsize=9)
ax.text(3.75, 3.7, "N = 0 no tirante", ha="center", va="top", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex09-N.png"), dpi=150)
plt.close(fig)

# V
fig, ax = plt.subplots(figsize=(9, 7.4))
base_portico(ax, "Esforço cortante V (kN)")
eV = 1.1 / 43
cV = "#2471a3"
desenha_diagrama(ax, "AD", 1, eV, 1, [(0, 2.5), (2.5, 5)], cV)
desenha_diagrama(ax, "DB", 1, eV, 1, [(0, 3)], cV)
desenha_diagrama(ax, "EP", 1, eV, 1, [(0, 1)], cV)
rot(ax, "AD", 0, +1, 1, eV, 1, "+29,8", extra=0.35, dx=-0.2)
rot(ax, "AD", 2.5, -1, 1, eV, 1, "+20,8", extra=0.35, dx=-0.3)
rot(ax, "AD", 2.5, +1, 1, eV, 1, "+4,8", extra=0.3, dx=0.6, dy=0.3)
rot(ax, "AD", 2.5 + 4 / 3, +1, 1, eV, 1, "0 (s = 3,83)", extra=0.55, dx=-0.75, dy=0.2)
ax.annotate("−4,2", (3 + 4.2 * eV * 0.8 * 0.5, 6 - 4.2 * eV * 0.6 - 0.02), xytext=(3.3, 5.0), fontsize=10, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color="#555", lw=0.8))
rot(ax, "DB", 0, +1, 1, eV, 1, "−13", extra=0.25, dx=0.2)
rot(ax, "DB", 3, -1, 1, eV, 1, "−43", extra=0.25, dx=-0.3)
rot(ax, "EP", 0.5, +1, 1, eV, 1, "+20", extra=0.25)
ax.text(6.15, 1.8, "V = 0 em CB", ha="left", fontsize=10, fontweight="bold")
ax.text(3.75, 3.7, "V = 0 no tirante", ha="center", va="top", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex09-V.png"), dpi=150)
plt.close(fig)

# M: desenhado do lado tracionado. M positivo traciona o lado direito de quem percorre (-n)
fig, ax = plt.subplots(figsize=(9, 7.4))
base_portico(ax, "Momento fletor M (kN.m), lado tracionado")
eM = 0.9 / 66.45
cM = "#b03a2e"
desenha_diagrama(ax, "AD", 2, eM, -1, [(0, 2.5), (2.5, 5)], cM)
desenha_diagrama(ax, "DB", 2, eM, -1, [(0, 3)], cM)
desenha_diagrama(ax, "CB", 2, eM, -1, [(4, 6)], cM)
desenha_diagrama(ax, "EP", 2, eM, -1, [(0, 1)], cM)
rot(ax, "AD", 0, +1, 2, eM, -1, "0", extra=0.3, dx=0.1, dy=-0.1)
rot(ax, "AD", 2.5, -1, 2, eM, -1, "63,25", extra=0.4)
rot(ax, "AD", 2.5 + 4 / 3, +1, 2, eM, -1, "66,45 (máx)", extra=0.75)
rot(ax, "DB", 0, +1, 2, eM, -1, "64", extra=0.3, dx=0.2)
rot(ax, "DB", float(u0), +1, 2, eM, -1, "0 (x = 5,51)", extra=0.35, dx=-1.1, dy=0.1)
rot(ax, "DB", 3, -1, 2, eM, -1, "−20", extra=0.2, dx=-0.3, dy=0.1)
rot(ax, "CB", 5, +1, 2, eM, -1, "20", extra=0.3, ha="left")
ax.annotate("−20 em E", (6.02, 4.22), xytext=(4.6, 4.45), fontsize=10, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color="#555", lw=0.8))
ax.text(6.15, 1.8, "M = 0 em CE", ha="left", fontsize=10, fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex09-M.png"), dpi=150)
plt.close(fig)
print("figuras salvas em", SAIDA)
