import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime
import pandas as pd

class DatabaseManager:
    def __init__(self):
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.creds_path = os.path.join(".secrets", "google_creds.json")
        self.sheet_name = "AcessoHub_DB"
        self.client = None
        self.worksheet = None

    def connect(self):
        try:
            
            if os.path.exists("google_creds.json"):
                self.client = gspread.service_account(filename="google_creds.json")
                
            
            else:
                credenciais_google = dict(st.secrets["connections"]["gsheets"])
                self.client = gspread.service_account_from_dict(credenciais_google)

            
            planilha = self.client.open(self.sheet_name)
            self.worksheet = planilha.sheet1 
            
            return True
            
        
        except Exception as e:
            # Mostra o erro exato do Google Cloud direto na tela do sistema
            st.error(f"⚠️ Erro Real do Banco: {e}") 
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def registrar_entrada(self, dados_visitante: dict) -> bool:
        """Salva a entrada do visitante na planilha incluindo o número do crachá."""
        try:
            if not self.worksheet and not self.connect():
                return False
                
            agora = datetime.now()
            data_entrada_formatada = agora.strftime("%d/%m/%Y %H:%M:%S")
            
            cpf_limpo = "".join(filter(str.isdigit, dados_visitante["cpf"]))
            id_registro = f"{cpf_limpo}_{agora.strftime('%Y%m%d%H%M%S')}"
            
            nova_linha = [
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
            
            self.worksheet.append_row(nova_linha)
            return True
        except Exception as e:
            print(f"❌ Erro ao registrar entrada: {e}")
            return False

    def listar_visitantes_ativos(self) -> list:
        """Retorna uma lista de dicionários contendo apenas os visitantes que estão na unidade."""
        try:
            if not self.worksheet and not self.connect():
                return []
                
            todos_registros = self.worksheet.get_all_records()
            
            ativos = [r for r in todos_registros if str(r.get("data_saida", "")).strip() == ""]
            return ativos
        except Exception as e:
            print(f"❌ Erro ao listar visitantes ativos: {e}")
            return []

    def registrar_saida(self, id_registro: str) -> bool:
        """Localiza o visitante ativo pelo ID único e insere o horário de saída."""
        try:
            if not self.worksheet and not self.connect():
                return False
                
            celula_id = self.worksheet.find(id_registro, in_column=1)
            
            if celula_id:
                linha = celula_id.row
                agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
                self.worksheet.update_cell(linha, 8, agora)
                return True
            return False
        except Exception as e:
            print(f"❌ Erro ao registrar saída no Sheets: {e}")
            return False