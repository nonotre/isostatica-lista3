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

# exercicio 08: portico triarticulado, origem em A, x para a direita, y para cima
A, D, B, E, C, Fp = (0, 0), (2, 0), (6, 3), (10, 3), (10, 0), (10, 5)
q, P = 10, 20  # kN/m (por metro de projecao horizontal, de x = 0 a x = 10), kN (horizontal, para a direita, em F)

# reacoes: forcas positivas para a direita e para cima, momentos anti-horarios positivos
Q = q * 10                       # resultante da distribuida, em x = 5
VC = F(Q * 5 + P * 5, 10)        # soma de momentos em A
VA = Q - VC
Qe = q * 6                       # carga sobre a parte esquerda (x de 0 a 6), em x = 3
# rotula B, parte esquerda: -6 VA + 3 HA + 3 Qe = 0
HA = F(6 * VA - 3 * Qe, 3)
HC = -P - HA
# forca que a parte direita faz na parte esquerda, em B
HB = -HA
VB = Qe - VA

print("HA =", HA, " VA =", VA)
print("HC =", HC, " VC =", VC)
print("forca da parte direita na esquerda em B: HB =", HB, " VB =", VB)
# conferencias
print("soma Fx =", HA + HC + P, " soma Fy =", VA + VC - Q)
mB_dir = (4 * VC - (-3) * HC) + 2 * (-q * 4) + (-2 * P)
print("momento em B da parte direita =", mB_dir)

HA, VA, HC, VC = map(float, (HA, VA, HC, VC))


# barras: (nome, inicio, fim). percurso de inicio para fim.
# t = direcao da barra, n = t girado 90 graus no sentido anti-horario.
# N = -(R . t), V = R . n, M = -(momento anti-horario das forcas antes da secao em relacao a secao)
# R = resultante das forcas antes da secao (lado de onde o percurso vem).
# M positivo traciona a fibra do lado -n (a direita de quem anda no percurso).
def antes(ponto, barra):
    """forcas externas antes da secao: lista de (ponto de aplicacao, (fx, fy))"""
    x, y = ponto
    f = []
    if barra in ("AD", "DB", "BE"):
        f.append(((0, 0), (HA, VA)))
        f.append(((x / 2, 0), (0, -q * x)))
    elif barra == "CE":
        f.append(((10, 0), (HC, VC)))
    return f


BARRAS = [("AD", A, D), ("DB", D, B), ("BE", B, E), ("CE", C, E), ("EF", E, Fp)]


def esforcos(barra, s):
    p0, p1 = [np.array(p, float) for p in next((b[1], b[2]) for b in BARRAS if b[0] == barra)]
    L = np.linalg.norm(p1 - p0)
    t = (p1 - p0) / L
    n = np.array([-t[1], t[0]])
    pt = p0 + s * t
    if barra == "EF":
        # forcas antes da secao somam -P (a estrutura inteira esta em equilibrio)
        R = np.array([-P, 0.0])
        Nv = -R @ t
        Vv = R @ n
        # momento das forcas acima da secao (anti-horario) = M (positivo traciona -n)
        r = np.array(Fp, float) - pt
        Mv = r[0] * 0 - r[1] * P
        return Nv, Vv, Mv
    R = np.zeros(2)
    mz = 0.0
    for (ap, fo) in antes(pt, barra):
        fo = np.array(fo, float)
        R += fo
        r = np.array(ap, float) - pt
        mz += r[0] * fo[1] - r[1] * fo[0]
    return -R @ t, R @ n, -mz


def comp(barra):
    b = next(b for b in BARRAS if b[0] == barra)
    return float(np.hypot(b[2][0] - b[1][0], b[2][1] - b[1][1]))


eps = 1e-9
for nome, p0, p1 in BARRAS:
    L = comp(nome)
    for s in (0, L):
        Nv, Vv, Mv = esforcos(nome, min(max(s, eps), L - eps))
        print(f"{nome} s={s:4.2f}  N={Nv:8.3f}  V={Vv:8.3f}  M={Mv:8.3f}")
# extremo de M na barra DB: V = 0
print("DB s=0,625 (x=2,5)", [round(float(v), 4) for v in esforcos("DB", 0.625)])
# equilibrio do no E: momento que cada barra aplica no no (anti-horario)
mBE = esforcos("BE", 4 - eps)[2]
mCE = esforcos("CE", 3 - eps)[2]
mEF = esforcos("EF", eps)[2]
print("no E:", -mBE, -mCE, mEF, "soma =", -mBE - mCE + mEF)


def fmt(v):
    s = f"{abs(v):.2f}".replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("−" if v < -1e-6 else "") + s


cor_c = "#1f5fbf"
cor_r = "#c0392b"


def geometria(ax, lw=3, cor="black"):
    for _, p0, p1 in BARRAS:
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=cor, lw=lw, solid_capstyle="round", zorder=3)
    ax.add_patch(Circle(B, 0.11, fc="white", ec=cor, lw=1.5, zorder=6))


def apoio_fixo(ax, x, y):
    ax.add_patch(Polygon([[x, y], [x - 0.3, y - 0.5], [x + 0.3, y - 0.5]], closed=True, fill=False, lw=1.5))
    ax.plot([x - 0.45, x + 0.45], [y - 0.5, y - 0.5], color="black", lw=1.5)
    for i in np.linspace(x - 0.4, x + 0.4, 6):
        ax.plot([i, i - 0.12], [y - 0.5, y - 0.65], color="black", lw=0.8)
    ax.add_patch(Circle((x, y), 0.08, fc="white", ec="black", lw=1.2, zorder=6))


def seta(ax, ini, fim, cor, lw=2):
    ax.annotate("", fim, xytext=ini, arrowprops=dict(arrowstyle="-|>", color=cor, lw=lw, mutation_scale=16))


# ---------- figura 1: estrutura e reacoes ----------
fig, ax = plt.subplots(figsize=(11, 6.6))
ax.set_aspect("equal")
ax.axis("off")
geometria(ax)
apoio_fixo(ax, *A)
apoio_fixo(ax, *C)
for p, nome, dx, dy in [(A, "A", -0.45, 0.15), (D, "D", 0.0, -0.45), (B, "B", -0.1, -0.5), (E, "E", 0.2, -0.45),
                        (C, "C", 0.2, 0.1), (Fp, "F", -0.45, 0.0)]:
    ax.text(p[0] + dx, p[1] + dy, nome, fontsize=13)
# distribuida, desenhada acima da estrutura (por projecao horizontal)
yq = 4.0
ax.plot([0, 10], [yq, yq], color=cor_c, lw=1)
for x in np.linspace(0, 10, 21):
    ybar = 0 if x <= 2 else (0.75 * (x - 2) if x <= 6 else 3)
    ax.annotate("", (x, ybar + 0.05), xytext=(x, yq),
                arrowprops=dict(arrowstyle="->", color=cor_c, lw=0.8, alpha=0.8))
ax.text(4.2, yq + 0.15, "10 kN/m (por metro de projeção horizontal)", color=cor_c, fontsize=11)
seta(ax, (10.05, 5), (11.6, 5), cor_c, 2.4)
ax.text(10.3, 5.2, "20 kN", color=cor_c, fontsize=12)
# reacoes
seta(ax, (-1.9, 0.0), (-0.15, 0.0), cor_r)
ax.text(-1.9, 0.15, f"H$_A$ = {fmt(HA)} kN", color=cor_r, fontsize=11)
seta(ax, (0, -2.0), (0, -0.7), cor_r)
ax.text(0.15, -1.9, f"V$_A$ = {fmt(VA)} kN", color=cor_r, fontsize=11)
seta(ax, (11.9, 0.0), (10.15, 0.0), cor_r)
ax.text(10.6, 0.15, f"H$_C$ = {fmt(-HC)} kN", color=cor_r, fontsize=11)
seta(ax, (10, -2.0), (10, -0.7), cor_r)
ax.text(10.15, -1.9, f"V$_C$ = {fmt(VC)} kN", color=cor_r, fontsize=11)
# cotas
yc = -2.6
for a, b in [(0, 2), (2, 6), (6, 10)]:
    ax.annotate("", (a, yc), xytext=(b, yc), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text((a + b) / 2, yc + 0.08, f"{b - a} m", ha="center", va="bottom", fontsize=10)
xc = 12.6
for a, b in [(0, 3), (3, 5)]:
    ax.annotate("", (xc, a), xytext=(xc, b), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(xc + 0.1, (a + b) / 2, f"{b - a} m", va="center", fontsize=10)
ax.text(4.3, 1.1, "5 m", fontsize=10, rotation=36.87, color="#555", ha="center", va="center")
ax.set_xlim(-2.4, 13.4)
ax.set_ylim(-3.0, 5.8)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex08-estrutura.png"), dpi=160)
plt.close(fig)


# ---------- diagramas sobre o portico ----------
def diagrama(arquivo, titulo, idx, escala, cor, rotulos, nos):
    """idx: 0 N, 1 V, 2 M. valor positivo desenhado do lado -n (abaixo nas barras horizontais,
    a direita na coluna percorrida de baixo para cima). para M e o lado tracionado"""
    fig, ax = plt.subplots(figsize=(11, 6.6))
    ax.set_aspect("equal")
    ax.axis("off")
    geometria(ax, lw=2.2)
    for p in (A, C):
        ax.add_patch(Circle(p, 0.08, fc="white", ec="black", lw=1.2, zorder=6))
    for nome, p0, p1 in BARRAS:
        p0a, p1a = np.array(p0, float), np.array(p1, float)
        L = np.linalg.norm(p1a - p0a)
        t = (p1a - p0a) / L
        n = np.array([-t[1], t[0]])
        ss = np.linspace(eps, L - eps, 120)
        vals = np.array([esforcos(nome, s)[idx] for s in ss])
        base = p0a[None, :] + ss[:, None] * t[None, :]
        curva = base - (escala * vals)[:, None] * n[None, :]
        poly = np.vstack([base[0], curva, base[-1]])
        ax.fill(poly[:, 0], poly[:, 1], color=cor, alpha=0.2, lw=0)
        ax.plot(poly[:, 0], poly[:, 1], color=cor, lw=1.8)
        for k in range(0, len(ss), 8):
            ax.plot([base[k, 0], curva[k, 0]], [base[k, 1], curva[k, 1]], color=cor, lw=0.5, alpha=0.6)
    for (x, y, texto, ha, va) in rotulos:
        ax.text(x, y, texto, ha=ha, va=va, fontsize=11, fontweight="bold", color="black", zorder=8,
                bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.5))
    for nome, (x, y) in nos.items():
        ax.text(x, y, nome, fontsize=12, color="#555", style="italic", zorder=8)
    ax.set_title(titulo, loc="left", fontsize=13, fontweight="bold")
    ax.set_xlim(-1.6, 13.0)
    ax.set_ylim(-1.3, 6.0)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, arquivo), dpi=160)
    plt.close(fig)


# N: escala 0,025 m por kN
diagrama("ex08-normal.png", "Esforço normal N (kN), tração positiva", 0, 0.025, "#7d3c98", [
    (1.0, 0.25, "−20", "center", "center"),
    (1.55, 0.75, "−28", "right", "bottom"),
    (5.75, 3.2, "−4", "right", "bottom"),
    (8.0, 3.25, "−20", "center", "center"),
    (8.4, 1.5, "−60", "right", "center"),
    (10.15, 4.0, "0", "left", "center"),
    (0.0, 5.3, "todas as barras comprimidas, exceto EF (N = 0)", "left", "center"),
], {"A": (-0.5, 0.1), "D": (1.85, -0.45), "B": (6.05, 2.55), "E": (10.15, 2.55), "F": (9.55, 5.0), "C": (10.15, -0.35)})

# V: escala 0,02 m por kN
diagrama("ex08-cortante.png", "Esforço cortante V (kN), positivo desenhado do lado das fibras inferiores", 1, 0.02,
         "#2471a3", [
    (0.05, -0.85, "+40", "left", "top"),
    (1.95, -0.45, "+20", "right", "top"),
    (2.35, -0.15, "+4", "left", "top"),
    (2.45, 0.45, "0 em x = 2,5", "right", "bottom"),
    (5.6, 3.5, "−28", "right", "bottom"),
    (6.15, 3.45, "−20", "left", "bottom"),
    (9.9, 4.25, "−60", "right", "bottom"),
    (10.85, 1.5, "+40", "left", "center"),
    (10.45, 4.0, "+20", "left", "center"),
], {"A": (-0.5, 0.1), "D": (1.7, 0.15), "B": (6.1, 2.55), "E": (9.6, 2.55), "F": (9.55, 5.0), "C": (9.5, -0.35)})

# M: escala 0,008 m por kN.m, desenhado do lado tracionado
diagrama("ex08-momento.png", "Momento fletor M (kN.m), desenhado do lado tracionado", 2, 0.008, "#b03a2e", [
    (0.0, 0.12, "0", "center", "bottom"),
    (2.05, -0.55, "60", "left", "top"),
    (3.0, -0.15, "61,25 (máx, x = 2,5)", "left", "top"),
    (6.0, 3.15, "0 (rótula)", "center", "bottom"),
    (9.4, 4.35, "−160 (BE)", "right", "bottom"),
    (10.15, 4.2, "−40 (EF)", "left", "center"),
    (11.1, 3.0, "120 (CE)", "left", "center"),
    (10.15, 5.05, "0", "left", "bottom"),
    (10.15, -0.2, "0", "left", "top"),
], {"A": (-0.5, 0.1), "D": (1.7, 0.15), "B": (6.1, 2.5), "E": (10.15, 3.15), "F": (9.55, 5.0), "C": (9.5, -0.35)})
print("figuras salvas em", SAIDA)
