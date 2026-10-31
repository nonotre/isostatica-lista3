# SET 400 Isostática, Lista 3: Esforços Solicitantes

Resolução dos exercícios 01 a 14, com reações externas e internas, diagramas de N, V e M com valores e explicação da forma das curvas.

| Arquivo | Conteúdo |
|---|---|
| [lista3-completa.pdf](lista3-completa.pdf) | tudo num PDF só: índice, o que conferir e os 14 exercícios |
| [CONFERIR.md](CONFERIR.md) | leituras da figura e hipóteses que valem conferir antes de usar |

| Ex | Estrutura | Texto | PDF |
|---|---|---|---|
| 01 | Viga com rótula e momento concentrado | [ex01.md](ex01.md) | [ex01.pdf](ex01.pdf) |
| 02 | Viga engastada com duas rótulas | [ex02.md](ex02.md) | [ex02.pdf](ex02.pdf) |
| 03 | Viga engastada com rótula | [ex03.md](ex03.md) | [ex03.pdf](ex03.pdf) |
| 04 | Pórtico em L engastado | [ex04.md](ex04.md) | [ex04.pdf](ex04.pdf) |
| 05 | Pórtico sobre apoios móveis com biela | [ex05.md](ex05.md) | [ex05.pdf](ex05.pdf) |
| 06 | Tesoura triarticulada com tirante | [ex06.md](ex06.md) | [ex06.pdf](ex06.pdf) |
| 07 | Pórtico engastado com pendural | [ex07.md](ex07.md) | [ex07.pdf](ex07.pdf) |
| 08 | Pórtico triarticulado com barra inclinada | [ex08.md](ex08.md) | [ex08.pdf](ex08.pdf) |
| 09 | Pórtico com tirante e luva | [ex09.md](ex09.md) | [ex09.pdf](ex09.pdf) |
| 10 | Pórtico com luva e barra inclinada | [ex10.md](ex10.md) | [ex10.pdf](ex10.pdf) |
| 11 | Pórtico triarticulado com peso próprio | [ex11.md](ex11.md) | [ex11.pdf](ex11.pdf) |
| 12 | Pórtico com luva e biela | [ex12.md](ex12.md) | [ex12.pdf](ex12.pdf) |
| 13 | Viga com binário e carga triangular | [ex13.md](ex13.md) | [ex13.pdf](ex13.pdf) |
| 14 | Chapa sobre bielas com peso próprio | [ex14.md](ex14.md) | [ex14.pdf](ex14.pdf) |

Cada `exNN.py` calcula as reações com frações exatas, confere o equilíbrio e gera as figuras em `figuras/`.

```
python -m venv .venv && .venv/bin/pip install matplotlib markdown
.venv/bin/python ex01.py               # reações, valores e figuras
.venv/bin/python gerar_pdf.py ex01     # ex01.pdf (precisa do chromium)
.venv/bin/python gerar_pdf.py completo # lista3-completa.pdf
```
