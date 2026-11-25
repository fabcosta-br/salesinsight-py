"""SalesInsight PY — geração, leitura e inspeção de dados brutos de vendas.

Responsável acadêmico: Fabiano Rodrigo Costa.
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from random import Random


COLUNAS_VENDAS = (
    "id_venda",
    "data_venda",
    "cliente",
    "produto",
    "categoria",
    "regiao",
    "quantidade",
    "preco_unitario",
)

class CabecalhoCSVInvalido(ValueError):
    """O CSV não contém o cabeçalho esperado."""


def gerar_dataset_vendas(
    caminho_csv: str | Path = "vendas.csv", n_registros: int = 200, seed: int = 42
) -> None:
    """Grava o dataset sintético da opção A do RF01."""
    aleatorio = Random(seed)
    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor", "Teclado", "Mouse", "Headset"]
    categorias = {
        "Notebook": "Computadores",
        "Smartphone": "Celulares",
        "Tablet": "Celulares",
        "Monitor": "Computadores",
        "Teclado": "Perifericos",
        "Mouse": "Perifericos",
        "Headset": "Perifericos",
    }
    precos = {
        "Notebook": 3500,
        "Smartphone": 2200,
        "Tablet": 1800,
        "Monitor": 1200,
        "Teclado": 250,
        "Mouse": 120,
        "Headset": 350,
    }
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
    data_inicio = datetime(2025, 1, 1)

    with open(caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS_VENDAS)
        escritor.writeheader()

        for i in range(n_registros):
            produto = aleatorio.choice(produtos)
            categoria = categorias[produto]
            quantidade = aleatorio.randint(1, 10)
            preco = round(precos[produto] * aleatorio.uniform(0.85, 1.15), 2)
            data = data_inicio + timedelta(days=aleatorio.randint(0, 364))
            data_txt = data.strftime("%Y-%m-%d")
            cliente = f"Cliente_{aleatorio.randint(1, 50):03d}"

            if aleatorio.random() < 0.05:
                quantidade = ""
            if aleatorio.random() < 0.04:
                preco = ""
            if aleatorio.random() < 0.06:
                produto = " " + produto + " "
            if aleatorio.random() < 0.03:
                data_txt = "DATA INVALIDA"
            if aleatorio.random() < 0.10:
                cliente = aleatorio.choice([
                    cliente.upper().replace("_", "-"),
                    cliente + "!!",
                    " " + cliente,
                    cliente.replace("Cliente_", "cliente#"),
                ])

            escritor.writerow({
                "id_venda": i + 1,
                "data_venda": data_txt,
                "cliente": cliente,
                "produto": produto,
                "categoria": categoria,
                "regiao": aleatorio.choice(regioes),
                "quantidade": quantidade,
                "preco_unitario": preco,
            })


def carregar_dataset(caminho_csv: str | Path) -> list[dict[str, str | None]]:
    """Lê os oito campos esperados e mantém os valores brutos do CSV."""
    with open(caminho_csv, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = leitor.fieldnames or []
        if len(colunas) != len(COLUNAS_VENDAS) or set(colunas) != set(COLUNAS_VENDAS):
            raise CabecalhoCSVInvalido(
                f"{Path(caminho_csv).name}: cabeçalho obrigatório ausente ou inválido. "
                f"Colunas esperadas: {', '.join(COLUNAS_VENDAS)}."
            )

        registros = []
        for registro in leitor:
            if None in registro:
                raise ValueError(f"Campos excedentes na linha {leitor.line_num} do CSV.")
            registros.append(registro)
        return registros


def inspecionar_dados(registros: list[dict[str, str | None]]) -> None:
    """Exibe dimensões, colunas, ausências por coluna e até cinco linhas."""
    print(f"Dimensões: {len(registros)} registros × {len(COLUNAS_VENDAS)} colunas")
    print(f"Colunas: {', '.join(COLUNAS_VENDAS)}")
    print("Ausências por coluna:")
    for coluna in COLUNAS_VENDAS:
        ausencias = sum(not (registro.get(coluna) or "").strip() for registro in registros)
        print(f"  {coluna}: {ausencias}")

    print("Primeiras 5 linhas:")
    for registro in registros[:5]:
        print(registro)


if __name__ == "__main__":
    caminho_csv = Path("vendas.csv")
    if not caminho_csv.exists():
        gerar_dataset_vendas(caminho_csv)
    try:
        registros = carregar_dataset(caminho_csv)
    except CabecalhoCSVInvalido as erro:
        raise SystemExit(str(erro)) from None
    inspecionar_dados(registros)
