import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self):
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.creds_path = os.path.join(".secrets", "google_creds.json")
        self.sheet_name = "AcessoHub_DB"
        self.client = None
        
        
        self.ws_movimentacao = None
        self.ws_visitantes = None

    def connect(self):
        try:
            if os.path.exists(self.creds_path):
                self.client = gspread.service_account(filename=self.creds_path)
            else:
                credenciais_google = dict(st.secrets["connections"]["gsheets"])
                self.client = gspread.service_account_from_dict(credenciais_google)

            planilha = self.client.open(self.sheet_name)
            
            # Conecta nas duas abas pelo nome exato
            self.ws_movimentacao = planilha.worksheet("Movimentacao")
            self.ws_visitantes = planilha.worksheet("Visitantes")
            
            return True
            
        except Exception as e:
            st.error(f"⚠️ Erro ao conectar. Verifique se as abas se chamam 'Movimentacao' e 'Visitantes'. Detalhe: {e}")
            return False

    def buscar_visitante_por_cpf(self, cpf_busca: str) -> dict:
        """Busca se o visitante já existe na base de cadastro limpa (Aba Visitantes)."""
        try:
            if not self.ws_visitantes and not self.connect():
                return None
                
            registros_visitantes = self.ws_visitantes.get_all_records()
            cpf_limpo_busca = "".join(filter(str.isdigit, cpf_busca))
            
            for r in registros_visitantes:
                cpf_db = "".join(filter(str.isdigit, str(r.get("CPF", ""))))
                if cpf_db == cpf_limpo_busca:
                    return {
                        "nome_completo": r.get("Nome Completo", ""),
                        "cpf": r.get("CPF", ""),
                        "telefone": r.get("Telefone", "")
                    }
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar visitante por CPF: {e}")
            return None

    def registrar_entrada(self, dados_visitante: dict, is_novo: bool = False) -> bool:
        """Salva a entrada na Movimentação e, se for novo, cadastra na aba Visitantes."""
        try:
            if not self.ws_movimentacao and not self.connect():
                return False
                
            agora = datetime.utcnow() - timedelta(hours=5)
            data_entrada_formatada = agora.strftime("%d/%m/%Y %H:%M:%S")
            
            cpf_limpo = "".join(filter(str.isdigit, dados_visitante["cpf"]))
            id_registro = f"{cpf_limpo}_{agora.strftime('%Y%m%d%H%M%S')}"
            
            # 1. Salva sempre no Livro de Movimentação (Intacto para os seus PDFs)
            nova_linha_movimento = [
                id_registro,
                dados_visitante["nome_completo"].strip().upper(),
                dados_visitante["cpf"],
                dados_visitante["telefone"],
                dados_visitante["local_visitado"],
                dados_visitante["objetivo"],
                data_entrada_formatada,
                "", 
                dados_visitante["numero_cracha"] 
            ]
            self.ws_movimentacao.append_row(nova_linha_movimento)
            
            # 2. Se for um Novo Visitante, salva ele na base limpa de cadastro
            if is_novo:
                nova_linha_cadastro = [
                    dados_visitante["cpf"],
                    dados_visitante["nome_completo"].strip().upper(),
                    dados_visitante["telefone"]
                ]
                self.ws_visitantes.append_row(nova_linha_cadastro)
                
            return True
        except Exception as e:
            print(f"❌ Erro ao registrar entrada: {e}")
            return False

    def listar_visitantes_ativos(self) -> list:
        try:
            if not self.ws_movimentacao and not self.connect():
                return []
            todos_registros = self.ws_movimentacao.get_all_records()
            ativos = [r for r in todos_registros if str(r.get("data_saida", "")).strip() == ""]
            return ativos
        except Exception as e:
            return []
        
    def listar_todos_registros(self) -> list:
        try:
            if not self.ws_movimentacao and not self.connect():
                return []
            return self.ws_movimentacao.get_all_records()
        except Exception as e:
            return []

    def registrar_saida(self, id_registro: str) -> bool:
        try:
            if not self.ws_movimentacao and not self.connect():
                return False
                
            celula_id = self.ws_movimentacao.find(id_registro, in_column=1)
            if celula_id:
                linha = celula_id.row
                agora = (datetime.utcnow() - timedelta(hours=5)).strftime("%d/%m/%Y %H:%M:%S")
                self.ws_movimentacao.update_cell(linha, 8, agora)
                return True
            return False
        except Exception as e:
            return False