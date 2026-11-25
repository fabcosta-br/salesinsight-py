"""Testes de preparação, análise e exportação de dados de vendas."""

import ast
import csv
import json
import re
import subprocess
import sys
import unittest
from collections import Counter
from contextlib import redirect_stdout
from datetime import datetime
from hashlib import sha256
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from salesinsight import (
    calcular_estatisticas,
    calcular_metricas,
    carregar_dataset,
    criar_colunas_derivadas,
    exibir_metricas,
    exibir_segmentacao,
    exportar_resultados,
    gerar_dataset_vendas,
    inspecionar_dados,
    limpar_dados,
    processar_coluna,
    segmentar_clientes,
)


CABECALHO = "id_venda,data_venda,cliente,produto,categoria,regiao,quantidade,preco_unitario"
RAIZ = Path(__file__).resolve().parent


class TesteDadosVendas(unittest.TestCase):
    def setUp(self):
        temporario = TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.pasta = Path(temporario.name)
        self.csv = self.pasta / "vendas.csv"

    def test_geracao_reproduzivel_com_oito_colunas_e_200_registros(self):
        copia = self.pasta / "copia.csv"
        gerar_dataset_vendas(self.csv)
        gerar_dataset_vendas(copia, n_registros=200, seed=42)
        conteudo_csv = self.csv.read_bytes()
        self.assertEqual(conteudo_csv, copia.read_bytes())
        self.assertEqual(
            sha256(conteudo_csv).hexdigest(),
            "5d8b1e07856f3b1ad4c433840cb1845643de3175450908f919cf83f7c21f0859",
        )

        with self.csv.open(encoding="utf-8", newline="") as arquivo:
            linhas = list(csv.reader(arquivo))

        self.assertEqual(linhas[0], CABECALHO.split(","))
        self.assertEqual(len(linhas[1:]), 200)
        self.assertTrue(all(len(linha) == 8 for linha in linhas[1:]))
        self.assertEqual(carregar_dataset(self.csv), carregar_dataset(RAIZ / "vendas.csv"))

    def test_dados_sinteticos_mantem_inconsistencias(self):
        gerar_dataset_vendas(self.csv)
        registros = carregar_dataset(self.csv)
        contagens = {
            "quantidade_vazia": sum(r["quantidade"] == "" for r in registros),
            "preco_vazio": sum(r["preco_unitario"] == "" for r in registros),
            "produto_com_espacos": sum(r["produto"] != r["produto"].strip() for r in registros),
            "data_invalida": sum(r["data_venda"] == "DATA INVALIDA" for r in registros),
            "cliente_com_ruido": sum(
                not re.fullmatch(r"Cliente_\d{3}", r["cliente"]) for r in registros
            ),
        }
        self.assertEqual(contagens, {
            "quantidade_vazia": 10,
            "preco_vazio": 4,
            "produto_com_espacos": 11,
            "data_invalida": 4,
            "cliente_com_ruido": 19,
        })

    def test_inspecao_conta_ausencias_e_exibe_somente_as_cinco_primeiras_linhas(self):
        self.csv.write_text(
            CABECALHO + "\n"
            "1,2025-01-01,  Cliente 001  ,Caneta,Papelaria,Sul,0,5.00\n"
            "2,DATA INVALIDA,Cliente_002!!,Caneta,Papelaria,Sul,,5.00\n"
            "3,2025-01-03,Cliente 003,Caneta,Papelaria,Sul,   ,5.00\n"
            "4,2025-01-04,Cliente 004,Caneta,Papelaria,Sul,1\n"
            "5,2025-01-05,Cliente 005,Caneta,Papelaria,Sul,1,5.00\n"
            "6,2025-01-06,Cliente 006,Caneta,Papelaria,Sul,1,\n",
            encoding="utf-8",
        )
        registros = carregar_dataset(self.csv)
        with redirect_stdout(StringIO()) as saida:
            inspecionar_dados(registros)

        linhas = saida.getvalue().splitlines()
        self.assertEqual(linhas[:11], [
            "Dimensões: 6 registros × 8 colunas",
            f"Colunas: {CABECALHO.replace(',', ', ')}",
            "Ausências por coluna:",
            "  id_venda: 0",
            "  data_venda: 0",
            "  cliente: 0",
            "  produto: 0",
            "  categoria: 0",
            "  regiao: 0",
            "  quantidade: 2",
            "  preco_unitario: 2",
        ])
        self.assertEqual(linhas[11], "Primeiras 5 linhas:")
        self.assertEqual(linhas[12:], [str(registro) for registro in registros[:5]])
        self.assertEqual(registros[0]["cliente"], "  Cliente 001  ")
        self.assertEqual(registros[1]["data_venda"], "DATA INVALIDA")
        self.assertEqual(registros[2]["quantidade"], "   ")
        self.assertIsNone(registros[3]["preco_unitario"])

    def test_inspecao_csv_so_com_cabecalho(self):
        gerar_dataset_vendas(self.csv, n_registros=0)
        registros = carregar_dataset(self.csv)
        self.assertEqual(registros, [])

        with redirect_stdout(StringIO()) as saida:
            inspecionar_dados(registros)

        linhas = saida.getvalue().splitlines()
        self.assertEqual(linhas[0], "Dimensões: 0 registros × 8 colunas")
        self.assertEqual(linhas[3:11], [f"  {campo}: 0" for campo in CABECALHO.split(",")])
        self.assertEqual(linhas[11:], ["Primeiras 5 linhas:"])

    def test_execucao_gera_csv_ausente_e_reutiliza_csv_existente(self):
        comando = [sys.executable, "-X", "utf8", str(RAIZ / "salesinsight.py")]
        primeira_execucao = subprocess.run(
            comando, cwd=self.pasta, capture_output=True, encoding="utf-8", check=True,
        )
        self.assertTrue(self.csv.is_file())
        self.assertIn("Dimensões: 200 registros × 8 colunas", primeira_execucao.stdout)

        self.csv.write_text(CABECALHO + "\n", encoding="utf-8")
        conteudo_existente = self.csv.read_bytes()
        segunda_execucao = subprocess.run(
            comando, cwd=self.pasta, capture_output=True, encoding="utf-8", check=True,
        )
        self.assertEqual(self.csv.read_bytes(), conteudo_existente)
        self.assertIn("Dimensões: 0 registros × 8 colunas", segunda_execucao.stdout)

    def test_execucao_rejeita_csv_de_zero_bytes_sem_traceback(self):
        self.csv.write_bytes(b"")
        modificacao_original = self.csv.stat().st_mtime_ns
        comando = [sys.executable, "-X", "utf8", str(RAIZ / "salesinsight.py")]
        resultado = subprocess.run(
            comando, cwd=self.pasta, capture_output=True, encoding="utf-8",
        )

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("vendas.csv: cabeçalho obrigatório ausente", resultado.stderr)
        self.assertIn(CABECALHO.replace(",", ", "), resultado.stderr)
        self.assertNotIn("Traceback", resultado.stderr)
        self.assertEqual(resultado.stdout, "")
        self.assertEqual(self.csv.read_bytes(), b"")
        self.assertEqual(self.csv.stat().st_mtime_ns, modificacao_original)


class TesteLimpezaTransformacao(unittest.TestCase):
    def setUp(self):
        self.bruto = {
            "id_venda": "1",
            "data_venda": "2025-07-08",
            "cliente": "Cliente_007",
            "produto": "Monitor",
            "categoria": "Computadores",
            "regiao": "Sul",
            "quantidade": "2",
            "preco_unitario": "10.50",
        }

    def test_limpeza_remove_datas_invalidas_e_ausencias_sem_dupla_contagem(self):
        registros = [
            dict(self.bruto, data_venda="DATA INVALIDA"),
            dict(self.bruto, data_venda="2025-02-30", quantidade=""),
            dict(self.bruto, quantidade="   "),
            dict(self.bruto, preco_unitario=None),
            dict(self.bruto, quantidade="", preco_unitario=""),
            dict(self.bruto, quantidade="0", preco_unitario="0.0"),
        ]
        with redirect_stdout(StringIO()) as saida:
            limpos, relatorio = limpar_dados(registros)

        self.assertEqual(relatorio, {
            "iniciais": 6,
            "removidos_data": 2,
            "removidos_nulos": 3,
            "removidos": 5,
            "finais": 1,
        })
        self.assertEqual(relatorio["iniciais"], relatorio["removidos"] + relatorio["finais"])
        self.assertEqual(limpos[0]["quantidade"], 0)
        self.assertEqual(limpos[0]["preco_unitario"], 0.0)
        self.assertIn("Registros recebidos: 6", saida.getvalue())
        self.assertIn("Registros removidos: 5", saida.getvalue())
        self.assertIn("Data inválida: 2", saida.getvalue())
        self.assertIn("Quantidade ou preço ausente: 3", saida.getvalue())
        self.assertIn("Registros válidos: 1", saida.getvalue())

    def test_limpeza_normaliza_variantes_e_sinaliza_nome_fora_do_padrao(self):
        nomes = (
            "Cliente_007",
            "CLIENTE-007",
            "Cliente_007!!",
            " Cliente_007",
            "cliente#007",
            "  Outro@ Nome!! ",
        )
        registros = [
            dict(
                self.bruto,
                cliente=nome,
                data_venda=" 2025-07-08 ",
                produto=" Monitor ",
                categoria=" Computadores ",
                regiao=" Sul ",
                quantidade=" 2.0 ",
                preco_unitario=" 10.50 ",
            )
            for nome in nomes
        ]
        brutos = [linha.copy() for linha in registros]
        with redirect_stdout(StringIO()):
            limpos, relatorio = limpar_dados(registros)

        self.assertEqual(registros, brutos)
        self.assertEqual(relatorio["removidos"], 0)
        self.assertEqual([r["cliente"] for r in limpos], ["Cliente_007"] * 5 + ["OutroNome"])
        self.assertEqual([r["cliente_fora_do_padrao"] for r in limpos], [False] * 5 + [True])
        self.assertEqual(limpos[0]["data_venda"], datetime(2025, 7, 8))
        self.assertIs(type(limpos[0]["quantidade"]), int)
        self.assertIs(type(limpos[0]["preco_unitario"]), float)
        self.assertEqual(limpos[0]["quantidade"], 2)
        self.assertEqual(limpos[0]["preco_unitario"], 10.5)
        self.assertEqual(limpos[0]["produto"], "Monitor")
        self.assertEqual(limpos[0]["categoria"], "Computadores")
        self.assertEqual(limpos[0]["regiao"], "Sul")

    def test_limpeza_rejeita_numero_preenchido_sem_valor_numerico_valido(self):
        for campos in ({"quantidade": "dois"}, {"preco_unitario": "texto"}, {"preco_unitario": "nan"}):
            with self.subTest(campos=campos), self.assertRaises(ValueError):
                limpar_dados([dict(self.bruto, **campos)])

    def test_transformacao_calcula_receita_e_calendario(self):
        nomes = (
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
        )
        limpos = [
            dict(self.bruto, data_venda=datetime(2025, mes, 1), quantidade=2, preco_unitario=10.5)
            for mes in range(1, 13)
        ]
        originais = [linha.copy() for linha in limpos]
        derivados = criar_colunas_derivadas(limpos)

        self.assertEqual(limpos, originais)
        self.assertEqual([r["mes"] for r in derivados], list(range(1, 13)))
        self.assertEqual([r["mes_nome"] for r in derivados], list(nomes))
        self.assertEqual(
            [r["trimestre"] for r in derivados],
            ["Q1"] * 3 + ["Q2"] * 3 + ["Q3"] * 3 + ["Q4"] * 3,
        )
        self.assertEqual([r["ano"] for r in derivados], [2025] * 12)
        self.assertEqual([r["receita_total"] for r in derivados], [21.0] * 12)
        self.assertIs(type(derivados[0]["receita_total"]), float)
        self.assertIs(type(derivados[0]["mes"]), int)
        self.assertIs(type(derivados[0]["ano"]), int)

    def test_transformacao_classifica_nos_limites_oficiais(self):
        casos = (
            (499.99, "Baixo Valor"),
            (500.0, "Medio Valor"),
            (4999.99, "Medio Valor"),
            (5000.0, "Alto Valor"),
        )
        for preco, faixa in casos:
            with self.subTest(receita=preco):
                linha = dict(
                    self.bruto, data_venda=datetime(2025, 1, 1), quantidade=1, preco_unitario=preco
                )
                resultado, = criar_colunas_derivadas([linha])
                self.assertEqual(resultado["receita_total"], preco)
                self.assertEqual(resultado["faixa_receita_item"], faixa)

    def test_dataset_oficial_fecha_contagens_e_gera_colunas_sem_ausencias(self):
        registros = carregar_dataset(RAIZ / "vendas.csv")
        with redirect_stdout(StringIO()):
            limpos, relatorio = limpar_dados(registros)
        derivados = criar_colunas_derivadas(limpos)

        self.assertEqual(relatorio, {
            "iniciais": 200,
            "removidos_data": 4,
            "removidos_nulos": 13,
            "removidos": 17,
            "finais": 183,
        })
        self.assertEqual(len(derivados), 183)
        self.assertTrue(all(not r["cliente_fora_do_padrao"] for r in derivados))
        self.assertTrue(all(
            r["receita_total"] == r["quantidade"] * r["preco_unitario"]
            and r["mes"] == r["data_venda"].month
            and r["ano"] == r["data_venda"].year
            and all(valor is not None and valor != "" for valor in r.values())
            for r in derivados
        ))


class TesteMetricasSegmentacao(unittest.TestCase):
    def setUp(self):
        self.venda = {
            "mes": 1,
            "produto": "Notebook",
            "categoria": "Computadores",
            "regiao": "Sul",
            "cliente": "Cliente_001",
            "quantidade": 1,
            "receita_total": 100.0,
        }

    def test_metricas_agrupam_receita_e_calculam_ticket_por_registro(self):
        registros = [
            dict(self.venda, mes=2, produto="Mouse", categoria="Perifericos", quantidade=2),
            dict(self.venda, regiao="Norte", quantidade=4, receita_total=400.0),
            dict(self.venda, produto="Mouse", categoria="Perifericos", receita_total=50.0),
            dict(self.venda, quantidade=3, receita_total=450.0),
        ]
        originais = [registro.copy() for registro in registros]
        metricas = calcular_metricas(registros)

        self.assertEqual(registros, originais)
        self.assertEqual(metricas, {
            "por_mes": [
                {"mes": 1, "receita_total": 900.0, "quantidade": 8, "n_vendas": 3},
                {"mes": 2, "receita_total": 100.0, "quantidade": 2, "n_vendas": 1},
            ],
            "top_produtos": [
                {"produto": "Notebook", "receita_total": 850.0},
                {"produto": "Mouse", "receita_total": 150.0},
            ],
            "por_categoria": [
                {"categoria": "Computadores", "receita_total": 850.0},
                {"categoria": "Perifericos", "receita_total": 150.0},
            ],
            "por_regiao": [
                {"regiao": "Norte", "receita_total": 400.0, "n_vendas": 1, "ticket_medio": 400.0},
                {"regiao": "Sul", "receita_total": 600.0, "n_vendas": 3, "ticket_medio": 200.0},
            ],
        })

    def test_top_5_produtos_desempata_por_nome(self):
        produtos = ("Zeta", "Beta", "Alfa", "Gama", "Epsilon", "Delta", "Eta")
        registros = [dict(self.venda, produto=produto) for produto in produtos]
        registros[0]["receita_total"] = 200.0

        top = calcular_metricas(registros)["top_produtos"]

        self.assertEqual([linha["produto"] for linha in top], ["Zeta", "Alfa", "Beta", "Delta", "Epsilon"])

    def test_segmentacao_acumula_centavos_e_respeita_limites(self):
        gastos = (
            ("Cliente_005", 5000.0),
            ("Cliente_001", 4999.99),
            ("Cliente_002", 4999.70),
            ("Cliente_002", 3 * 0.1),
            ("Cliente_003", 15000.0),
            ("Cliente_004", 15000.01),
        )
        registros = [dict(self.venda, cliente=nome, receita_total=valor) for nome, valor in gastos]
        originais = [registro.copy() for registro in registros]
        clientes = segmentar_clientes(registros)

        self.assertEqual(registros, originais)
        self.assertEqual(clientes, [
            {"cliente": "Cliente_004", "total_gasto": 15000.01, "segmento": "Ouro"},
            {"cliente": "Cliente_003", "total_gasto": 15000.0, "segmento": "Prata"},
            {"cliente": "Cliente_002", "total_gasto": 5000.0, "segmento": "Prata"},
            {"cliente": "Cliente_005", "total_gasto": 5000.0, "segmento": "Prata"},
            {"cliente": "Cliente_001", "total_gasto": 4999.99, "segmento": "Bronze"},
        ])

    def test_exibicao_lista_top_10_e_conta_clientes_fora_do_ranking(self):
        registros = [
            dict(self.venda, cliente=f"Cliente_{i:03d}", receita_total=float(i * 1000))
            for i in range(1, 13)
        ]
        with redirect_stdout(StringIO()) as saida:
            exibir_segmentacao(segmentar_clientes(registros))

        ranking, distribuicao = saida.getvalue().split("\nClientes por segmento:\n")
        linhas = [linha.strip() for linha in ranking.splitlines() if linha.startswith("  ")]
        self.assertEqual([linha.split(" | ")[0] for linha in linhas], [
            f"Cliente_{i:03d}" for i in range(12, 2, -1)
        ])
        self.assertEqual(linhas[0], "Cliente_012 | R$ 12.000,00 | Prata")
        self.assertEqual(distribuicao.splitlines(), ["  Bronze: 4", "  Prata: 8", "  Ouro: 0"])

    def test_resultados_vazios_exibem_contagens_zero(self):
        metricas = calcular_metricas([])
        clientes = segmentar_clientes([])
        self.assertEqual(metricas, {
            "por_mes": [], "top_produtos": [], "por_categoria": [], "por_regiao": [],
        })
        self.assertEqual(clientes, [])
        with redirect_stdout(StringIO()) as saida:
            exibir_metricas(metricas)
            exibir_segmentacao(clientes)

        for texto in ("sem registros válidos", "Nenhum cliente identificado", "Bronze: 0", "Prata: 0", "Ouro: 0"):
            self.assertIn(texto, saida.getvalue())

    def test_vendas_sem_rotulos_opcionais_continuam_nos_totais(self):
        registro = dict(self.venda, produto=None, categoria="", regiao=None, cliente="")
        metricas = calcular_metricas([registro])

        self.assertEqual(metricas["por_mes"][0]["receita_total"], 100.0)
        self.assertEqual(metricas["por_categoria"], [{"categoria": "", "receita_total": 100.0}])
        self.assertEqual(metricas["por_regiao"], [
            {"regiao": "", "receita_total": 100.0, "n_vendas": 1, "ticket_medio": 100.0},
        ])
        self.assertEqual(metricas["top_produtos"], [])
        self.assertEqual(segmentar_clientes([registro]), [])

    def test_metricas_e_segmentos_reconciliam_o_dataset_oficial(self):
        brutos = carregar_dataset(RAIZ / "vendas.csv")
        with redirect_stdout(StringIO()):
            limpos, _ = limpar_dados(brutos)
        derivados = criar_colunas_derivadas(limpos)
        metricas = calcular_metricas(derivados)
        clientes = segmentar_clientes(derivados)

        self.assertEqual(len(derivados), 183)
        self.assertEqual(len(metricas["por_mes"]), 12)
        self.assertEqual(sum(linha["quantidade"] for linha in metricas["por_mes"]), 1031)
        for dimensao in ("por_mes", "por_regiao"):
            self.assertEqual(sum(linha["n_vendas"] for linha in metricas[dimensao]), 183)
        for dimensao in ("por_mes", "por_categoria", "por_regiao"):
            receita = sum(linha["receita_total"] for linha in metricas[dimensao])
            self.assertAlmostEqual(receita, 1290346.30, places=2)
        self.assertEqual([linha["produto"] for linha in metricas["top_produtos"]], [
            "Notebook", "Tablet", "Smartphone", "Monitor", "Headset",
        ])
        self.assertEqual(metricas["top_produtos"][0]["receita_total"], 374174.85)
        self.assertEqual(len(clientes), 50)
        self.assertAlmostEqual(sum(linha["total_gasto"] for linha in clientes), 1290346.30, places=2)
        self.assertEqual(clientes[0], {
            "cliente": "Cliente_006", "total_gasto": 65905.09, "segmento": "Ouro",
        })
        self.assertEqual(Counter(linha["segmento"] for linha in clientes), {"Bronze": 6, "Prata": 10, "Ouro": 34})

    def test_execucao_principal_exibe_as_quatro_metricas_e_a_segmentacao(self):
        with TemporaryDirectory() as pasta:
            (Path(pasta) / "vendas.csv").write_bytes((RAIZ / "vendas.csv").read_bytes())
            resultado = subprocess.run(
                [sys.executable, "-X", "utf8", str(RAIZ / "salesinsight.py")],
                cwd=pasta, capture_output=True, encoding="utf-8", check=True,
            )
        titulos = (
            "Primeiro registro após a transformação:",
            "Receita, unidades e vendas por mês:",
            "Top 5 produtos por receita:",
            "Receita por categoria:",
            "Receita e ticket médio por região:",
            "Top 10 clientes por gasto:",
            "Clientes por segmento:",
        )
        posicoes = [resultado.stdout.index(titulo) for titulo in titulos]
        self.assertEqual(posicoes, sorted(posicoes))
        self.assertIn("Registros válidos: 183", resultado.stdout)
        self.assertIn("Cliente_006 | R$ 65.905,09 | Ouro", resultado.stdout)
        self.assertEqual(resultado.stderr, "")


class TesteFuncoesReutilizaveis(unittest.TestCase):
    def test_processar_coluna_aplica_a_funcao_a_cada_valor(self):
        registros = [{"quantidade": 2}, {"quantidade": 5}]
        chamadas = []

        def dobrar(valor):
            chamadas.append(valor)
            return 2 * valor

        resultado = processar_coluna(registros, "quantidade", dobrar, "dobro")

        self.assertEqual(chamadas, [2, 5])
        self.assertEqual(resultado, [{"quantidade": 2, "dobro": 4}, {"quantidade": 5, "dobro": 10}])
        self.assertEqual(registros, [{"quantidade": 2}, {"quantidade": 5}])

    def test_lambdas_em_ranking_e_classificacao(self):
        arvore = ast.parse((RAIZ / "salesinsight.py").read_text(encoding="utf-8"))
        funcoes = {no.name: no for no in arvore.body if isinstance(no, ast.FunctionDef)}
        casos = (("calcular_metricas", "sorted"), ("segmentar_clientes", "processar_coluna"))
        for funcao, chamada in casos:
            with self.subTest(funcao=funcao):
                self.assertTrue(any(
                    isinstance(no, ast.Call)
                    and isinstance(no.func, ast.Name)
                    and no.func.id == chamada
                    and any(isinstance(arg, ast.Lambda) for arg in no.args + [kw.value for kw in no.keywords])
                    for no in ast.walk(funcoes[funcao])
                ))


class TesteExportacaoFluxo(unittest.TestCase):
    def setUp(self):
        temporario = TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.pasta = Path(temporario.name)
        self.saida = self.pasta / "outputs"
        self.nomes = {"metricas_por_mes.csv", "segmentacao_clientes.csv", "estatisticas_gerais.json"}

    def ler_csv(self, nome, cabecalho):
        with (self.saida / nome).open(encoding="utf-8", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            self.assertEqual(leitor.fieldnames, cabecalho.split(","))
            return list(leitor)

    def ler_saidas(self):
        self.assertEqual({arquivo.name for arquivo in self.saida.iterdir()}, self.nomes)
        return {nome: (self.saida / nome).read_bytes() for nome in self.nomes}

    def executar_fluxo(self):
        return subprocess.run(
            [sys.executable, "-S", "-X", "utf8", str(RAIZ / "salesinsight.py")],
            cwd=self.pasta, capture_output=True, encoding="utf-8", check=True,
        )

    def test_exporta_csvs_e_json_coerentes_com_dados_e_calculos(self):
        brutos = carregar_dataset(RAIZ / "vendas.csv")
        with redirect_stdout(StringIO()):
            limpos, relatorio = limpar_dados(brutos)
        derivados = criar_colunas_derivadas(limpos)
        metricas = calcular_metricas(derivados)
        clientes = segmentar_clientes(derivados)
        estatisticas = calcular_estatisticas(metricas, clientes, relatorio)

        relidas = exportar_resultados(metricas, clientes, estatisticas, self.saida)

        arquivos = self.ler_saidas()
        meses = self.ler_csv("metricas_por_mes.csv", "mes,receita_total,quantidade,n_vendas")
        segmentos = self.ler_csv("segmentacao_clientes.csv", "cliente,total_gasto,segmento")
        self.assertEqual(meses, [{chave: str(valor) for chave, valor in linha.items()} for linha in metricas["por_mes"]])
        self.assertEqual(segmentos, [{chave: str(valor) for chave, valor in linha.items()} for linha in clientes])
        self.assertEqual(json.loads(arquivos["estatisticas_gerais.json"]), relidas)
        self.assertEqual(relidas, estatisticas)
        self.assertEqual(relidas["limpeza"], relatorio)
        self.assertEqual((relatorio["iniciais"], relatorio["removidos"], relatorio["finais"]), (200, 17, 183))
        self.assertEqual(sum(int(linha["n_vendas"]) for linha in meses), relidas["n_vendas"])
        self.assertEqual(relidas["n_vendas"], len(derivados))
        self.assertEqual(relidas["unidades_vendidas"], sum(linha["quantidade"] for linha in derivados))
        self.assertEqual(relidas["unidades_vendidas"], 1031)
        self.assertEqual(relidas["receita_total"], sum(round(linha["receita_total"] * 100) for linha in derivados) / 100)
        self.assertEqual(relidas["receita_total"], 1290346.30)
        self.assertEqual(relidas["clientes_identificados"], len(segmentos))
        self.assertEqual(relidas["clientes_identificados"], 50)
        self.assertEqual(relidas["clientes_por_segmento"], {"Bronze": 6, "Prata": 10, "Ouro": 34})

    def test_exportacao_preserva_acentos_em_utf8(self):
        clientes = [{"cliente": "São José", "total_gasto": 1.25, "segmento": "Bronze"}]
        estatisticas = {"descrição": "Análise de março"}
        self.assertEqual(exportar_resultados({"por_mes": []}, clientes, estatisticas, self.saida), estatisticas)
        arquivos = self.ler_saidas()
        self.assertIn("São José".encode(), arquivos["segmentacao_clientes.csv"])
        self.assertIn("Análise de março".encode(), arquivos["estatisticas_gerais.json"])

    def test_falha_na_escrita_do_json_preserva_exportacoes_anteriores(self):
        metricas = {"por_mes": []}
        exportar_resultados(metricas, [], {"n_vendas": 0}, self.saida)
        anteriores = self.ler_saidas()

        with self.assertRaises(ValueError):
            exportar_resultados(metricas, [], {"receita_total": float("nan")}, self.saida)

        self.assertEqual(self.ler_saidas(), anteriores)

    def test_falha_na_substituicao_restaura_exportacoes_anteriores(self):
        exportar_resultados({"por_mes": []}, [], {"n_vendas": 0}, self.saida)
        anteriores = self.ler_saidas()
        metricas = {"por_mes": [{"mes": 1, "receita_total": 50, "quantidade": 1, "n_vendas": 1}]}
        substituir = Path.replace

        for erro in (PermissionError, KeyboardInterrupt):
            def falhar_no_segundo_csv(origem, destino):
                if destino.name == "segmentacao_clientes.csv":
                    raise erro
                return substituir(origem, destino)

            with self.subTest(erro=erro.__name__):
                with patch.object(Path, "replace", autospec=True, side_effect=falhar_no_segundo_csv):
                    with self.assertRaises(erro):
                        exportar_resultados(metricas, [], {"n_vendas": 1}, self.saida)
                self.assertEqual(self.ler_saidas(), anteriores)

    def test_releitura_divergente_impede_publicacao_do_conjunto(self):
        with patch("salesinsight.json.load", return_value={"n_vendas": 2}):
            with self.assertRaisesRegex(ValueError, "divergem"):
                exportar_resultados({"por_mes": []}, [], {"n_vendas": 0}, self.saida)

        self.assertEqual(list(self.saida.iterdir()), [])

    def test_fluxo_do_zero_preserva_dados_e_reproduz_saidas_sem_site_packages(self):
        primeira = self.executar_fluxo()
        vendas = self.pasta / "vendas.csv"
        brutos = vendas.read_bytes()
        relatorios = self.ler_saidas()
        self.assertEqual(brutos, (RAIZ / "vendas.csv").read_bytes())
        self.assertEqual(len(carregar_dataset(vendas)), 200)
        self.assertIn("JSON gravado, relido e validado:", primeira.stdout)
        self.assertIn("Execução concluída: 183 vendas válidas, 1031 unidades, R$ 1.290.346,30 e 50 clientes", primeira.stdout)
        self.assertEqual(primeira.stderr, "")

        segunda = self.executar_fluxo()

        self.assertEqual(vendas.read_bytes(), brutos)
        self.assertEqual(self.ler_saidas(), relatorios)
        self.assertEqual(segunda.stdout, primeira.stdout)

    def test_fluxo_com_csv_sem_vendas_exporta_cabecalhos_e_totais_zero(self):
        (self.pasta / "vendas.csv").write_text(CABECALHO + "\n", encoding="utf-8")

        self.executar_fluxo()

        arquivos = self.ler_saidas()
        self.assertEqual(self.ler_csv("metricas_por_mes.csv", "mes,receita_total,quantidade,n_vendas"), [])
        self.assertEqual(self.ler_csv("segmentacao_clientes.csv", "cliente,total_gasto,segmento"), [])
        estatisticas = json.loads(arquivos["estatisticas_gerais.json"])
        self.assertEqual(estatisticas["n_vendas"], 0)
        self.assertEqual(estatisticas["receita_total"], 0.0)
        self.assertEqual(estatisticas["clientes_por_segmento"], {"Bronze": 0, "Prata": 0, "Ouro": 0})


if __name__ == "__main__":
    unittest.main()
