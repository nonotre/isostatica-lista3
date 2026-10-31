import os
import re
import shutil
import subprocess
import sys
import tempfile

import markdown

RAIZ = os.path.dirname(os.path.abspath(__file__))
COMPLETO = os.path.join(RAIZ, "lista3-completa.pdf")

EXERCICIOS = [
    ("01", "Viga com rótula e momento concentrado"),
    ("02", "Viga engastada com duas rótulas"),
    ("03", "Viga engastada com rótula"),
    ("04", "Pórtico em L engastado"),
    ("05", "Pórtico sobre apoios móveis com biela"),
    ("06", "Tesoura triarticulada com tirante"),
    ("07", "Pórtico engastado com pendural"),
    ("08", "Pórtico triarticulado com barra inclinada"),
    ("09", "Pórtico com tirante e luva"),
    ("10", "Pórtico com luva e barra inclinada"),
    ("11", "Pórtico triarticulado com peso próprio"),
    ("12", "Pórtico com luva e biela"),
    ("13", "Viga com binário e carga triangular"),
    ("14", "Chapa sobre bielas com peso próprio"),
]

CSS = """
@page { size: A4; margin: 2cm 1.8cm; }
body { font-family: 'DejaVu Serif', Georgia, serif; font-size: 10.5pt; line-height: 1.45; color: #111; }
h1 { font-size: 17pt; margin: 0 0 8pt; }
h2 { font-size: 13.5pt; margin-top: 18pt; border-bottom: 1px solid #999; padding-bottom: 2pt; break-after: avoid; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt; break-after: avoid; }
table { border-collapse: collapse; margin: 6pt 0 10pt; font-size: 9.5pt; page-break-inside: avoid; }
th, td { border: 1px solid #888; padding: 3pt 7pt; vertical-align: top; }
th { background: #eee; }
img { width: 100%; page-break-inside: avoid; margin: 6pt 0; }
p { margin: 5pt 0; }
.capa { text-align: center; margin-top: 3cm; }
.capa .disc { font-size: 13pt; }
.capa .titulo { font-size: 22pt; font-weight: bold; margin: 10pt 0 4pt; }
.capa .sub { font-size: 13pt; margin-bottom: 2cm; }
.capa table { margin: 0 auto; font-size: 10.5pt; text-align: left; }
.capa td.pag { text-align: right; }
"""


def html_para_pdf(corpo, pdf):
    html = f"<!doctype html><html lang='pt-br'><head><meta charset='utf-8'><base href='file://{RAIZ}/'><style>{CSS}</style></head><body>{corpo}</body></html>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp = f.name
    perfil = tempfile.mkdtemp(prefix="chromium-")
    try:
        subprocess.run(["chromium", "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={perfil}", f"--print-to-pdf={pdf}", f"file://{tmp}"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        os.remove(tmp)
        shutil.rmtree(perfil, ignore_errors=True)


def gerar(nome, destino=None):
    md = os.path.join(RAIZ, f"{nome}.md")
    pdf = destino or os.path.join(RAIZ, f"{nome}.pdf")
    corpo = markdown.markdown(open(md, encoding="utf-8").read(), extensions=["tables"])
    html_para_pdf(corpo, pdf)
    print("gerado", pdf)
    return pdf


def paginas(pdf):
    saida = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True, check=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", saida).group(1))


def capa(linhas):
    tabela = "".join(f"<tr><td>{rot}</td><td>{desc}</td><td class='pag'>{pag}</td></tr>" for rot, desc, pag in linhas)
    return f"""<div class="capa">
<div class="disc">SET 400 Isostática</div>
<div class="titulo">Lista 3: Esforços Solicitantes</div>
<div class="sub">Resolução dos exercícios 01 a 14</div>
<table><tr><th></th><th>Estrutura</th><th>Página</th></tr>{tabela}</table>
</div>"""


def gerar_completo():
    with tempfile.TemporaryDirectory() as tmp:
        conferir = gerar("CONFERIR", os.path.join(tmp, "conferir.pdf"))
        partes = [conferir] + [gerar(f"ex{n}") for n, _ in EXERCICIOS]
        linhas, pag = [], 2
        linhas.append(("", "O que conferir", pag))
        pag += paginas(conferir)
        for (n, desc), pdf in zip(EXERCICIOS, partes[1:]):
            linhas.append((f"Ex. {n}", desc, pag))
            pag += paginas(pdf)
        pdf_capa = os.path.join(tmp, "capa.pdf")
        html_para_pdf(capa(linhas), pdf_capa)
        if paginas(pdf_capa) != 1:
            sys.exit("a capa passou de uma página, os números do índice ficariam errados")
        subprocess.run(["pdfunite", pdf_capa, *partes, COMPLETO], check=True)
    print("gerado", COMPLETO, f"({paginas(COMPLETO)} páginas)")


if __name__ == "__main__":
    if sys.argv[1:] == ["completo"]:
        gerar_completo()
    else:
        for nome in sys.argv[1:] or ["ex01"]:
            gerar(nome)
