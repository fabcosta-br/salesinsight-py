"""Testes de geração, leitura e inspeção do Gate 01."""

import csv
import re
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from salesinsight import carregar_dataset, gerar_dataset_vendas, inspecionar_dados


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


if __name__ == "__main__":
    unittest.main()
