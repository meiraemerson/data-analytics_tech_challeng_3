"""Verifica estrutura e sintaxe sem acessar a AWS."""
from pathlib import Path
import ast
import json
import pandas as pd

raiz = Path(__file__).resolve().parents[1]
nb = json.loads((raiz / "notebooks/Tech_Challenge_Fase3.ipynb").read_text())
assert nb["nbformat"] == 4 and nb["cells"]
for i, cell in enumerate(nb["cells"]):
    assert cell["cell_type"] in {"code", "markdown", "raw"}
    if cell["cell_type"] == "code":
        codigo = "\n".join(l for l in "".join(cell["source"]).splitlines() if not l.lstrip().startswith("%"))
        ast.parse(codigo, filename=f"celula_{i}")
ast.parse((raiz / "src/glue_etl.py").read_text())
for caminho in (raiz / "config").glob("*.json"):
    json.loads(caminho.read_text())
for caminho in (raiz / "results").glob("*.csv"):
    assert not pd.read_csv(caminho).empty, caminho.name
assert len(list((raiz / "sql").glob("*.sql"))) >= 8
print("Estrutura, sintaxe, contratos e agregados válidos. AWS não executada.")
