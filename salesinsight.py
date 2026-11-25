"""SalesInsight PY — preparação e análise de dados de vendas.

Responsável acadêmico: Fabiano Rodrigo Costa.
"""

import csv
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from math import isfinite
from operator import itemgetter
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


def limpar_dados(
    registros: list[dict[str, str | None]],
) -> tuple[list[dict], dict[str, int]]:
    """Limpa os registros brutos e retorna os válidos e o relatório impresso."""
    limpos = []
    relatorio = {"iniciais": len(registros), "removidos_data": 0, "removidos_nulos": 0}
    padrao_cliente = re.compile(r"Cliente_?([0-9]{3})", flags=re.IGNORECASE)

    for bruto in registros:
        try:
            data = datetime.strptime((bruto["data_venda"] or "").strip(), "%Y-%m-%d")
        except ValueError:
            relatorio["removidos_data"] += 1
            continue

        quantidade_txt = (bruto["quantidade"] or "").strip()
        preco_txt = (bruto["preco_unitario"] or "").strip()
        if not quantidade_txt or not preco_txt:
            relatorio["removidos_nulos"] += 1
            continue

        quantidade = int(float(quantidade_txt))
        preco = float(preco_txt)
        if not isfinite(preco):
            raise ValueError("preco_unitario deve ser um número finito.")

        linha: dict = bruto.copy()
        for campo in ("cliente", "produto", "categoria", "regiao"):
            texto = bruto[campo]
            if texto is not None:
                linha[campo] = texto.strip()

        cliente = linha["cliente"]
        if cliente is not None:
            cliente = re.sub(r"[^A-Za-z0-9_]", "", cliente)
        identificador = padrao_cliente.fullmatch(cliente or "")
        linha.update(
            data_venda=data,
            quantidade=quantidade,
            preco_unitario=preco,
            cliente=f"Cliente_{identificador[1]}" if identificador else cliente,
            cliente_fora_do_padrao=identificador is None,
        )
        limpos.append(linha)

    relatorio["removidos"] = relatorio["removidos_data"] + relatorio["removidos_nulos"]
    relatorio["finais"] = len(limpos)
    print("\nRelatório de limpeza:")
    print(f"  Registros recebidos: {relatorio['iniciais']}")
    print(f"  Registros removidos: {relatorio['removidos']}")
    print(f"  Data inválida: {relatorio['removidos_data']}")
    print(f"  Quantidade ou preço ausente: {relatorio['removidos_nulos']}")
    print(f"  Registros válidos: {relatorio['finais']}")
    return limpos, relatorio


def criar_colunas_derivadas(registros: list[dict]) -> list[dict]:
    """Acrescenta receita, calendário e faixa de valor aos registros limpos."""
    meses = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro",
    }
    enriquecidos = []
    for linha in registros:
        data = linha["data_venda"]
        mes = data.month
        if mes <= 3:
            trimestre = "Q1"
        elif mes <= 6:
            trimestre = "Q2"
        elif mes <= 9:
            trimestre = "Q3"
        else:
            trimestre = "Q4"

        receita = linha["quantidade"] * linha["preco_unitario"]
        if receita < 500:
            faixa = "Baixo Valor"
        elif receita < 5000:
            faixa = "Medio Valor"
        else:
            faixa = "Alto Valor"

        enriquecidos.append({
            **linha,
            "receita_total": receita,
            "mes": mes,
            "mes_nome": meses[mes],
            "trimestre": trimestre,
            "ano": data.year,
            "faixa_receita_item": faixa,
        })
    return enriquecidos


def calcular_metricas(registros: list[dict]) -> dict[str, list[dict]]:
    """Agrupa registros válidos por mês, produto, categoria e região."""
    vendas_por_mes = defaultdict(Counter)
    receita_por_produto = Counter()
    receita_por_categoria = Counter()
    vendas_por_regiao = defaultdict(Counter)

    for registro in registros:
        receita_centavos = round(registro["receita_total"] * 100)

        mes = vendas_por_mes[registro["mes"]]
        mes["receita_centavos"] += receita_centavos
        mes["quantidade"] += registro["quantidade"]
        mes["n_vendas"] += 1

        produto = registro["produto"]
        if produto:
            receita_por_produto[produto] += receita_centavos

        receita_por_categoria[registro["categoria"] or ""] += receita_centavos
        regiao = vendas_por_regiao[registro["regiao"] or ""]
        regiao["receita_centavos"] += receita_centavos
        regiao["n_vendas"] += 1

    produtos_ordenados = sorted(receita_por_produto.items())
    produtos_ordenados.sort(key=itemgetter(1), reverse=True)
    return {
        "por_mes": [
            {
                "mes": mes,
                "receita_total": resumo["receita_centavos"] / 100,
                "quantidade": resumo["quantidade"],
                "n_vendas": resumo["n_vendas"],
            }
            for mes, resumo in sorted(vendas_por_mes.items())
        ],
        "top_produtos": [
            {"produto": produto, "receita_total": receita / 100}
            for produto, receita in produtos_ordenados[:5]
        ],
        "por_categoria": [
            {"categoria": categoria, "receita_total": receita / 100}
            for categoria, receita in sorted(receita_por_categoria.items())
        ],
        "por_regiao": [
            {
                "regiao": regiao,
                "receita_total": resumo["receita_centavos"] / 100,
                "n_vendas": resumo["n_vendas"],
                "ticket_medio": resumo["receita_centavos"] / (100 * resumo["n_vendas"]),
            }
            for regiao, resumo in sorted(vendas_por_regiao.items())
        ],
    }


def segmentar_clientes(registros: list[dict]) -> list[dict]:
    """Retorna os clientes identificados ordenados pelo gasto acumulado."""
    total_por_cliente = Counter()
    for registro in registros:
        cliente = registro["cliente"]
        if cliente:
            total_por_cliente[cliente] += round(registro["receita_total"] * 100)

    clientes_ordenados = sorted(total_por_cliente.items())
    clientes_ordenados.sort(key=itemgetter(1), reverse=True)
    classificar = lambda total: (
        "Ouro" if total > 15_000 else "Prata" if total >= 5_000 else "Bronze"
    )
    clientes = []
    for cliente, centavos in clientes_ordenados:
        total = centavos / 100
        clientes.append({"cliente": cliente, "total_gasto": total, "segmento": classificar(total)})
    return clientes


def _formatar_reais(valor: float) -> str:
    return "R$ " + f"{valor:,.2f}".translate(str.maketrans(".,", ",."))


def exibir_metricas(metricas: dict[str, list[dict]]) -> None:
    """Mostra os quatro agrupamentos de vendas no console."""
    if not metricas["por_mes"]:
        print("\nMétricas de vendas: sem registros válidos.")
        return

    print("\nReceita, unidades e vendas por mês:")
    for linha in metricas["por_mes"]:
        print(
            f"  {linha['mes']:02d} | {_formatar_reais(linha['receita_total'])}"
            f" | {linha['quantidade']} un. | {linha['n_vendas']} vendas"
        )

    print("\nTop 5 produtos por receita:")
    for linha in metricas["top_produtos"]:
        print(f"  {linha['produto']} | {_formatar_reais(linha['receita_total'])}")

    print("\nReceita por categoria:")
    for linha in metricas["por_categoria"]:
        categoria = linha["categoria"] or "Sem categoria informada"
        print(f"  {categoria} | {_formatar_reais(linha['receita_total'])}")

    print("\nReceita e ticket médio por região:")
    for linha in metricas["por_regiao"]:
        regiao = linha["regiao"] or "Sem região informada"
        print(
            f"  {regiao} | {_formatar_reais(linha['receita_total'])}"
            f" | Ticket: {_formatar_reais(linha['ticket_medio'])}"
        )


def exibir_segmentacao(clientes: list[dict]) -> None:
    """Mostra os dez clientes com maior gasto e a distribuição de todos."""
    print("\nTop 10 clientes por gasto:")
    if not clientes:
        print("  Nenhum cliente identificado.")
    for linha in clientes[:10]:
        print(f"  {linha['cliente']} | {_formatar_reais(linha['total_gasto'])} | {linha['segmento']}")

    distribuicao = Counter(linha["segmento"] for linha in clientes)
    print("\nClientes por segmento:")
    for segmento in ("Bronze", "Prata", "Ouro"):
        print(f"  {segmento}: {distribuicao[segmento]}")


if __name__ == "__main__":
    caminho_csv = Path("vendas.csv")
    if not caminho_csv.exists():
        gerar_dataset_vendas(caminho_csv)
    try:
        registros = carregar_dataset(caminho_csv)
    except CabecalhoCSVInvalido as erro:
        raise SystemExit(str(erro)) from None
    inspecionar_dados(registros)
    registros_limpos, _ = limpar_dados(registros)
    registros_transformados = criar_colunas_derivadas(registros_limpos)
    if registros_transformados:
        print("\nPrimeiro registro após a transformação:")
        print(registros_transformados[0])
    exibir_metricas(calcular_metricas(registros_transformados))
    exibir_segmentacao(segmentar_clientes(registros_transformados))
