"""SalesInsight PY — preparação e análise de dados de vendas.

Responsável acadêmico: Fabiano Rodrigo Costa.
"""

import csv
import json
import re
from collections import Counter, defaultdict
from collections.abc import Callable
from contextlib import ExitStack
from datetime import datetime, timedelta
from math import isfinite
from operator import itemgetter
from pathlib import Path
from random import Random
from shutil import copyfile


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

    produtos_ordenados = sorted(receita_por_produto.items(), key=lambda item: (-item[1], item[0]))
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


def processar_coluna(
    registros: list[dict], coluna: str, funcao_transformacao: Callable, nome_saida: str
) -> list[dict]:
    """Aplica uma função à coluna e devolve cópias com o campo resultante."""
    return [
        {**registro, nome_saida: funcao_transformacao(registro[coluna])}
        for registro in registros
    ]


def segmentar_clientes(registros: list[dict]) -> list[dict]:
    """Retorna os clientes identificados ordenados pelo gasto acumulado."""
    total_por_cliente = Counter()
    for registro in registros:
        cliente = registro["cliente"]
        if cliente:
            total_por_cliente[cliente] += round(registro["receita_total"] * 100)

    clientes_ordenados = sorted(total_por_cliente.items())
    clientes_ordenados.sort(key=itemgetter(1), reverse=True)
    clientes = [
        {"cliente": cliente, "total_gasto": centavos / 100}
        for cliente, centavos in clientes_ordenados
    ]
    return processar_coluna(
        clientes,
        "total_gasto",
        lambda total: "Ouro" if total > 15_000 else "Prata" if total >= 5_000 else "Bronze",
        "segmento",
    )


def _formatar_reais(valor: float) -> str:
    """Formata um valor monetário para exibição em reais."""
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

    print("\nClientes por segmento:")
    for segmento, quantidade in _contar_segmentos(clientes).items():
        print(f"  {segmento}: {quantidade}")


def _contar_segmentos(clientes: list[dict]) -> dict[str, int]:
    """Conta clientes em cada segmento, incluindo segmentos vazios."""
    distribuicao = Counter(linha["segmento"] for linha in clientes)
    return {segmento: distribuicao[segmento] for segmento in ("Bronze", "Prata", "Ouro")}


def calcular_estatisticas(
    metricas: dict[str, list[dict]], clientes: list[dict], relatorio_limpeza: dict[str, int]
) -> dict:
    """Consolida os totais de vendas, limpeza e segmentação para o JSON."""
    por_mes = metricas["por_mes"]
    receita_centavos = sum(round(linha["receita_total"] * 100) for linha in por_mes)
    return {
        "limpeza": relatorio_limpeza.copy(),
        "n_vendas": sum(linha["n_vendas"] for linha in por_mes),
        "unidades_vendidas": sum(linha["quantidade"] for linha in por_mes),
        "receita_total": receita_centavos / 100,
        "clientes_identificados": len(clientes),
        "clientes_por_segmento": _contar_segmentos(clientes),
    }


def exportar_resultados(
    metricas: dict[str, list[dict]],
    clientes: list[dict],
    estatisticas: dict,
    pasta_saida: str | Path = "outputs",
) -> dict:
    """Grava dois CSVs e devolve as estatísticas conferidas no JSON final."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)
    relatorios_csv = (
        ("metricas_por_mes.csv", ("mes", "receita_total", "quantidade", "n_vendas"), metricas["por_mes"]),
        ("segmentacao_clientes.csv", ("cliente", "total_gasto", "segmento"), clientes),
    )
    nome_json = "estatisticas_gerais.json"
    destinos = tuple(pasta / nome for nome, _, _ in relatorios_csv) + (pasta / nome_json,)

    # A reserva exclusiva herda as permissões da pasta de saída. No NTFS,
    # os relatórios mantêm essas permissões ao serem movidos para o destino.
    reserva = pasta / ".exportacao-em-andamento"
    with ExitStack() as limpar_temporarios:
        reserva.mkdir()
        limpar_temporarios.callback(reserva.rmdir)
        copia_anterior = reserva / "anterior"
        copia_anterior.mkdir()
        limpar_temporarios.callback(copia_anterior.rmdir)
        for destino in destinos:
            limpar_temporarios.callback((reserva / destino.name).unlink, missing_ok=True)
            limpar_temporarios.callback((copia_anterior / destino.name).unlink, missing_ok=True)

        for nome, campos, linhas in relatorios_csv:
            with (reserva / nome).open("w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=campos)
                escritor.writeheader()
                escritor.writerows(linhas)
        with (reserva / nome_json).open("w", encoding="utf-8") as arquivo:
            json.dump(estatisticas, arquivo, ensure_ascii=False, indent=2, allow_nan=False)
            arquivo.write("\n")

        for destino in destinos:
            if destino.exists():
                copyfile(destino, copia_anterior / destino.name)

        try:
            for destino in destinos:
                (reserva / destino.name).replace(destino)
            with (pasta / nome_json).open(encoding="utf-8") as arquivo:
                relidas = json.load(arquivo)
            if relidas != estatisticas:
                raise ValueError("As estatísticas relidas divergem dos resultados calculados.")
        except (OSError, ValueError, KeyboardInterrupt):
            for destino in reversed(destinos):
                if (reserva / destino.name).exists():
                    continue
                anterior = copia_anterior / destino.name
                if anterior.exists():
                    anterior.replace(destino)
                else:
                    destino.unlink()
            raise
    return relidas


def main() -> None:
    """Executa o fluxo de vendas do CSV bruto à conferência dos relatórios."""
    caminho_csv = Path("vendas.csv")
    if not caminho_csv.exists():
        gerar_dataset_vendas(caminho_csv)
    try:
        registros = carregar_dataset(caminho_csv)
    except CabecalhoCSVInvalido as erro:
        raise SystemExit(str(erro)) from None
    inspecionar_dados(registros)
    registros_limpos, relatorio = limpar_dados(registros)
    registros_transformados = criar_colunas_derivadas(registros_limpos)
    if registros_transformados:
        print("\nPrimeiro registro após a transformação:")
        print(registros_transformados[0])
    metricas = calcular_metricas(registros_transformados)
    exibir_metricas(metricas)
    clientes = segmentar_clientes(registros_transformados)
    exibir_segmentacao(clientes)
    estatisticas = calcular_estatisticas(metricas, clientes, relatorio)
    relidas = exportar_resultados(metricas, clientes, estatisticas)
    print("\nJSON gravado, relido e validado:")
    print(json.dumps(relidas, ensure_ascii=False, indent=2))
    print(
        f"\nExecução concluída: {relidas['n_vendas']} vendas válidas, "
        f"{relidas['unidades_vendidas']} unidades, {_formatar_reais(relidas['receita_total'])} "
        f"e {relidas['clientes_identificados']} clientes. Relatórios em outputs/."
    )


if __name__ == "__main__":
    main()
