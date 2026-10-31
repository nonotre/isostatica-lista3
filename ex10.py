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

# exercicio 10: coordenadas (x, y) em metros, origem em A
A, C, D, E = (0, 0), (4, 3), (4, 5), (8, 5)
qh = 10  # kN/m horizontal, por metro de altura, de y = 0 a y = 5
qv = 10  # kN/m vertical, por metro horizontal, na viga DE
H = 5    # altura total carregada
L = 4    # vao da viga DE

# luva em D: nao transmite forca horizontal
# viga DE: soma de forcas em x
HE = F(0)
# estrutura inteira: soma de forcas em x
HA = -(qh * H) - HE
# estrutura inteira: momentos em A (anti-horario positivo)
# carga horizontal 50 kN a y = 2,5 (horario), carga vertical 40 kN em x = 6 (horario)
VE = (qv * L * F(E[0] + D[0], 2) + qh * H * F(H, 2)) / E[0]
VA = qv * L - VE
# viga DE isolada: forcas em y e momentos em D
VDv = qv * L - VE                    # forca da coluna sobre a viga (para cima positivo)
MDv = qv * L * F(L, 2) - VE * L      # momento da coluna sobre a viga (anti-horario positivo)

print("HA =", HA, float(HA))
print("VA =", VA, float(VA))
print("HE =", HE, "VE =", VE, float(VE))
print("luva D, sobre a viga: V =", VDv, float(VDv), " M =", MDv, float(MDv))

# conferencia global
sfx = HA + HE + qh * H
sfy = VA + VE - qv * L
sma = VE * 8 - qv * L * 6 - qh * H * F(5, 2)
print("conferencia: sum Fx =", sfx, " sum Fy =", sfy, " sum MA =", sma)
# conferencia da parte A-C-D
smA_col = -qh * H * F(5, 2) + 4 * (-VDv) + (-MDv)
print("conferencia parte ACD, sum MA =", smA_col)

# barras: (nome, inicio, fim)
barras = [("AC", A, C), ("CD", C, D), ("DE", D, E)]


def unit(p, q):
    v = np.array(q, float) - np.array(p, float)
    return v / np.linalg.norm(v)


def esforcos(barra, s):
    """N, V, M na secao a distancia s do inicio da barra, pelas forcas do lado do inicio"""
    nome, p0, p1 = barra
    t = unit(p0, p1)
    n = np.array([-t[1], t[0]])  # t girado 90 graus anti-horario
    P = np.array(p0, float) + s * t
    # carga horizontal: tudo de y = 0 ate a altura da secao (ou ate 5 na viga)
    ylim = min(P[1], H) if nome != "DE" else H
    lista = [(np.array([float(HA), float(VA)]), np.array([0.0, 0.0]))]
    # carga horizontal ao longo do caminho A-C-D, integrada por faixas de altura
    if ylim > 0:
        # ponto de aplicacao: na barra AC ou CD conforme a altura
        def ponto_em_y(y):
            if y <= 3:
                return np.array([4 * y / 3, y])
            return np.array([4.0, y])
        ys = np.linspace(0, ylim, 401)
        dy = ys[1] - ys[0]
        for y in (ys[:-1] + ys[1:]) / 2:
            lista.append((np.array([qh * dy, 0.0]), ponto_em_y(y)))
    if nome == "DE" and s > 0:
        lista.append((np.array([0.0, -qv * s]), np.array([D[0] + s / 2, D[1]])))
    R = sum(f for f, _ in lista)
    mom = sum((pt - P)[0] * f[1] - (pt - P)[1] * f[0] for f, pt in lista)
    N = -R @ t
    V = R @ n
    M = -mom
    return N, V, M


# expressoes exatas (s ao longo da barra)
def N_AC(s): return 43.375 - 4.8 * s
def V_AC(s): return 25.5 - 3.6 * s
def M_AC(s): return 25.5 * s - 1.8 * s ** 2
def N_CD(h): return 5.625
def V_CD(h): return 20 - 10 * h
def M_CD(h): return 82.5 + 20 * h - 5 * h ** 2
def N_DE(u): return 0.0
def V_DE(u): return -5.625 - 10 * u
def M_DE(u): return 102.5 - 5.625 * u - 5 * u ** 2


expr = {"AC": (N_AC, V_AC, M_AC, 5), "CD": (N_CD, V_CD, M_CD, 2), "DE": (N_DE, V_DE, M_DE, 4)}

# confere as expressoes contra o calculo direto por corpo livre
for b in barras:
    fN, fV, fM, Lb = expr[b[0]]
    for s in [0, Lb / 3, Lb / 2, Lb]:
        Nn, Vn, Mn = esforcos(b, s)
        assert abs(Nn - fN(s)) < 1e-3 and abs(Vn - fV(s)) < 1e-3 and abs(Mn - fM(s)) < 1e-3, (b[0], s, Nn, Vn, Mn)
    print(f"barra {b[0]}: inicio N={fN(0):8.3f} V={fV(0):8.3f} M={fM(0):8.3f} | fim N={fN(Lb):8.3f} V={fV(Lb):8.3f} M={fM(Lb):8.3f}")
print("expressoes conferidas por corpo livre")


def fmt(v):
    from decimal import Decimal, ROUND_HALF_UP
    s = str(Decimal(repr(abs(float(v)))).quantize(Decimal("0.01"), ROUND_HALF_UP)).replace(".", ",")
    if s.endswith(",00"):
        s = s[:-3]
    return ("−" if v < -1e-6 else "") + s


cor_c = "#1f5fbf"
cor_r = "#c0392b"


def desenha_estrutura(ax, lw=3, cor="black"):
    ax.plot([A[0], C[0], D[0]], [A[1], C[1], D[1] - 0.12], color=cor, lw=lw, solid_capstyle="round")
    ax.plot([D[0] + 0.05, E[0]], [D[1], D[1]], color=cor, lw=lw, solid_capstyle="round")
    # luva
    for yy in (D[1] + 0.15, D[1] - 0.12):
        ax.plot([D[0] - 0.35, D[0] + 0.35], [yy, yy], color=cor, lw=1.2)


def apoio(ax, x, y):
    ax.add_patch(Polygon([[x, y], [x - 0.25, y - 0.42], [x + 0.25, y - 0.42]], closed=True, fill=False, lw=1.5))
    ax.plot([x - 0.4, x + 0.4], [y - 0.42, y - 0.42], color="black", lw=1.5)
    for i in np.linspace(x - 0.35, x + 0.35, 6):
        ax.plot([i, i - 0.1], [y - 0.42, y - 0.55], color="black", lw=0.8)
    ax.add_patch(Circle((x, y), 0.07, fc="white", ec="black", lw=1.2, zorder=5))


# ---------- figura 1: estrutura e reacoes ----------
fig, ax = plt.subplots(figsize=(10, 7.2))
ax.set_aspect("equal")
ax.axis("off")
desenha_estrutura(ax)
apoio(ax, *A)
apoio(ax, *E)
for p, nome, dx, dy in [(A, "A", 0.15, 0.15), (C, "C", 0.15, -0.25), (D, "D", -0.55, 0.3), (E, "E", 0.1, 0.2)]:
    ax.text(p[0] + dx, p[1] + dy, nome, fontsize=13)
# carga horizontal
xq = -1.6
ax.plot([xq - 0.7, xq - 0.7], [0, 5], color=cor_c, lw=1)
for y in np.linspace(0, 5, 11):
    ax.annotate("", (xq, y), xytext=(xq - 0.7, y), arrowprops=dict(arrowstyle="->", color=cor_c, lw=1))
ax.text(xq - 1.0, 5.25, "10 kN/m\n(por metro de altura)", color=cor_c, fontsize=10)
# carga vertical
ax.plot([D[0], E[0]], [D[1] + 0.95, D[1] + 0.95], color=cor_c, lw=1)
for x in np.linspace(D[0], E[0], 9):
    ax.annotate("", (x, D[1] + 0.2), xytext=(x, D[1] + 0.95), arrowprops=dict(arrowstyle="->", color=cor_c, lw=1))
ax.text(5.5, D[1] + 1.05, "10 kN/m", color=cor_c, fontsize=11)
# reacoes
ax.annotate("", (A[0] - 0.15, A[1]), xytext=(A[0] + 0.0 - 1.3, A[1] - 0.0),
            arrowprops=dict(arrowstyle="<|-", color=cor_r, lw=2))
ax.text(-1.45, -0.42, "H$_A$ = 50 kN", color=cor_r, fontsize=10)
ax.annotate("", (A[0] + 0.45, -1.6), xytext=(A[0] + 0.45, -0.6), arrowprops=dict(arrowstyle="-|>", color=cor_r, lw=2))
ax.text(A[0] + 0.6, -1.45, "V$_A$ = 5,63 kN", color=cor_r, fontsize=10)
ax.annotate("", (E[0], E[1] - 0.6), xytext=(E[0], E[1] - 1.7), arrowprops=dict(arrowstyle="-|>", color=cor_r, lw=2))
ax.text(E[0] + 0.12, E[1] - 1.5, "V$_E$ = 45,63 kN", color=cor_r, fontsize=10)
ax.text(E[0] - 0.6, E[1] - 2.0, "H$_E$ = 0", color=cor_r, fontsize=10)
# cotas
ax.annotate("", (0, -2.1), xytext=(4, -2.1), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.annotate("", (4, -2.1), xytext=(8, -2.1), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(2, -2.05, "4 m", ha="center", va="bottom", fontsize=9)
ax.text(6, -2.05, "4 m", ha="center", va="bottom", fontsize=9)
ax.annotate("", (9.2, 0), xytext=(9.2, 3), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.annotate("", (9.2, 3), xytext=(9.2, 5), arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(9.3, 1.5, "3 m", va="center", fontsize=9)
ax.text(9.3, 4, "2 m", va="center", fontsize=9)
ax.text(2.3, 1.15, "barra AC: 5 m", rotation=36.87, fontsize=9, color="#555")
ax.set_xlim(-3.2, 10)
ax.set_ylim(-2.5, 6.6)
fig.tight_layout()
fig.savefig(os.path.join(SAIDA, "ex10-estrutura.png"), dpi=160)
plt.close(fig)


# ---------- figuras 2 a 4: N, V, M sobre o portico ----------
def geom(nome):
    for b in barras:
        if b[0] == nome:
            t = unit(b[1], b[2])
            return np.array(b[1], float), t, np.array([-t[1], t[0]])


def diagrama(arquivo, qual, escala, cor, titulo, lado_m=False, rotulos=(), sinais=()):
    fig, ax = plt.subplots(figsize=(10, 7))
    desenha_estrutura(ax, lw=2, cor="#333")
    apoio(ax, *A)
    apoio(ax, *E)
    for nome, p0, p1 in barras:
        o, t, n = geom(nome)
        f = expr[nome][qual]
        Lb = expr[nome][3]
        ss = np.linspace(0, Lb, 120)
        vals = np.array([f(s) for s in ss])
        d = -n if lado_m else n  # M positivo vai para o lado -n (tracionado)
        base = o[None, :] + ss[:, None] * t[None, :]
        pts = base + (escala * vals)[:, None] * d[None, :]
        poly = np.vstack([base, pts[::-1]])
        ax.add_patch(Polygon(poly, closed=True, fc=cor, alpha=0.16, ec="none"))
        ax.plot(pts[:, 0], pts[:, 1], color=cor, lw=2)
        for k in (0, -1):
            ax.plot([base[k, 0], pts[k, 0]], [base[k, 1], pts[k, 1]], color=cor, lw=1.5)
    # rotulos: (barra, s, texto, folga extra em m, deslocamento ao longo da barra)
    for rot in rotulos:
        nome, s, txt, folga, ds = rot[:5]
        o, t, n = geom(nome)
        f = expr[nome][qual]
        v = f(s)
        d = -n if lado_m else n
        sgn = 1 if v >= 0 else -1
        p = o + (s + ds) * t + (escala * v + sgn * folga) * d
        if txt is None:
            txt = fmt(v)
        caixa = dict(fc="white", ec="none", alpha=0.85, pad=0.6)
        if len(rot) > 5:  # texto deslocado com seta apontando para o ponto
            alvo = o + s * t + escala * v * d
            ax.annotate(txt, alvo, xytext=(alvo[0] + rot[5][0], alvo[1] + rot[5][1]), fontsize=11,
                        fontweight="bold", ha="center", va="center", bbox=caixa,
                        arrowprops=dict(arrowstyle="-", color="#444", lw=0.8))
        else:
            ax.text(p[0], p[1], txt, fontsize=11, fontweight="bold", ha="center", va="center", bbox=caixa)
    for x, y, txt in sinais:
        ax.text(x, y, txt, fontsize=15, fontweight="bold", color=cor, ha="center", va="center")
    ax.set_title(titulo, loc="left", fontsize=13, fontweight="bold")
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-2.4, 9.6)
    ax.set_ylim(-0.8, 7.0)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, arquivo), dpi=150)
    plt.close(fig)


sN, sV, sM = 0.04, 0.045, 0.011
diagrama("ex10-N.png", 0, sN, "#7d3c98", "Esforço normal N (kN), positivo = tração", rotulos=[
    ("AC", 0, None, 0.45, 0.25),
    ("AC", 5, None, 0.4, -0.7),
    ("CD", 1.4, None, 0.7, 0),
    ("DE", 2, "N = 0", 0.35, 0),
], sinais=[(-0.2, 1.6, "+"), (3.55, 4.0, "+")])
diagrama("ex10-V.png", 1, sV, "#2471a3", "Esforço cortante V (kN)", rotulos=[
    ("AC", 0, None, 0.4, 0.3),
    ("AC", 5, None, 0, 0, (0.9, -0.9)),
    ("CD", 0, None, 0, 0, (-0.9, 0.5)),
    ("CD", 2, "0", 0.45, 0.0),
    ("DE", 0, None, 0.4, 0.6),
    ("DE", 4, None, 0.35, -0.2),
], sinais=[(1.0, 1.9, "+"), (3.5, 3.9, "+"), (6.6, 4.3, "−")])
diagrama("ex10-M.png", 2, sM, "#b03a2e", "Momento fletor M (kN.m), desenhado do lado tracionado", lado_m=True, rotulos=[
    ("AC", 0, None, 0.35, 0.3),
    ("AC", 2.5, None, 0.45, 0),
    ("AC", 5, None, 0.5, 0),
    ("CD", 1, None, 0.5, -0.3),
    ("CD", 2, None, -0.4, -0.3),
    ("DE", 2, None, -0.3, 0.2),
    ("DE", 4, "0", 0.3, 0),
])
print("figuras salvas em", SAIDA)
