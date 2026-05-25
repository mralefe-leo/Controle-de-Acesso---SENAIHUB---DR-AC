import streamlit as st
from database import DatabaseManager
import os
import time
import re


st.set_page_config(
    page_title="AcessoHub",
    page_icon="assets/logo.png",
    layout="wide"
)


def carregar_estilo_css():
    caminho_css = "assets/styles.css"
    if os.path.exists(caminho_css):
        with open(caminho_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

carregar_estilo_css()

def verificar_senha():
    """Retorna True se o usuário já colocou a senha correta, False caso contrário."""
    if st.session_state.get("autenticado", False):
        return True

    # 1. INJETA CSS ESPECÍFICO SÓ PARA A TELA DE LOGIN
    st.markdown("""
        <style>
            /* Pinta o fundo da tela inteira de Azul SENAI */
            [data-testid="stAppViewContainer"] {
                background-color: #1D4ED8 !important;
            }
            /* Deixa a barra superior transparente */
            [data-testid="stHeader"] {
                background-color: transparent !important;
            }
            /* Força o cartão de login a ser branco e flutuante */
            [data-testid="stForm"] {
                background-color: #FFFFFF !important;
                border: none !important;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
            }
            /* Força o texto dentro do input a ficar escuro */
            [data-testid="stForm"] label {
                color: #1E293B !important;
                font-weight: 600 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    import base64
    import os
    
    caminho_logo_branca = os.path.join("assets", "logo_branca.png")
    img_tag = ""
    if os.path.exists(caminho_logo_branca):
        with open(caminho_logo_branca, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
            # 2. CSS INLINE NA LOGO: Garante tamanho perfeito (max 300px) e centralização absoluta
            img_tag = f'<img src="data:image/png;base64,{logo_b64}" style="max-width: 300px; width: 100%; margin: 0 auto; display: block; margin-bottom: 20px;">'
            
    _, col_login, _ = st.columns([1, 1.2, 1])
    
    with col_login:
        st.write("")
        st.write("")
        st.write("") # Mais respiro no topo
        st.markdown(f"{img_tag}", unsafe_allow_html=True)
        # 3. Título branco para contrastar com o fundo azul
        st.markdown("<h2 style='text-align: center; color: #FFFFFF; margin-bottom: 30px; font-weight: 700;'>🔒 Acesso Restrito</h2>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            senha_digitada = st.text_input("Senha de Acesso", type="password", placeholder="Digite a senha corporativa...")
            submit_login = st.form_submit_button("🔓 Entrar no Sistema", use_container_width=True)
            
            if submit_login:
                if senha_digitada == st.secrets["SENHA_PORTARIA"]:
                    st.session_state.autenticado = True
                    st.rerun() 
                else:
                    st.error("❌ Senha incorreta. Acesso negado.")
                    
    return False

# =========================================================
# FUNÇÕES DE VALIDAÇÃO MATEMÁTICA E CSS
# =========================================================
def validar_cpf(cpf: str) -> bool:
    cpf_limpo = re.sub(r'[^0-9]', '', cpf)
    if len(cpf_limpo) != 11:
        return False
    if cpf_limpo == cpf_limpo[0] * 11:
        return False
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10
    if int(cpf_limpo[9]) != digito1:
        return False
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10
    if int(cpf_limpo[10]) != digito2:
        return False
    return True

def validar_telefone(telefone: str) -> bool:
    telefone_limpo = re.sub(r'[^0-9]', '', telefone)
    if len(telefone_limpo) not in [10, 11]:
        return False
    if len(telefone_limpo) == 11 and telefone_limpo[2] != '9':
        return False
    return True

def carregar_estilo_css():
    caminho_css = "assets/styles.css"
    if os.path.exists(caminho_css):
        with open(caminho_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

LOCAIS_SENAI = [
    "Selecione o local...", "Gerência", "Núcleo de Educação", "Núcleo de Administração",
    "Sala de Instrutores", "Mercado", "Biblioteca", "Secretaria Escolar", "Auditório (24/25)",
    "Sala de Reunião 1º Piso (26)", "Espaço HUB - Núcleo de Inovação e Tecnologia (Consultoria)",
    "Sala de Reunião 2º Piso (37)", "SENAI Play", "Sala de Gravação Espaço SENAI HUB",
    "Marcenaria", "Sala de Afiação", "Sala de Gravação - Marcenaria",
    "Laboratório de ensaio em Materiais", "Laboratório em Ensaio em Mobiliário",
    "Laboratório em Ensaio Cerâmico e Solos"
]


def main():
    import base64
    
    if "db" not in st.session_state:
        st.session_state.db = DatabaseManager()
        st.session_state.db_conectado = st.session_state.db.connect()

    if "form_key" not in st.session_state:
        st.session_state.form_key = 1
    
    carregar_estilo_css()
    
    caminho_logo_branca = os.path.join("assets", "logo_branca.png")
    img_tag = ""
    
    if os.path.exists(caminho_logo_branca):
        with open(caminho_logo_branca, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
            img_tag = f'<img src="data:image/png;base64,{logo_b64}" class="header-logo">'

    st.markdown(f"""
        <div class="header-container">
            {img_tag}
            <div class="header-text">
                <h1>AcessoHUB</h1>
                <p>Gestão de Fluxo e Visitantes</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get("db_conectado", False):
        st.error("⚠️ Falha de conexão com o servidor de dados. Contate o suporte técnico.")
        return
    
    visitantes_ativos = st.session_state.db.listar_visitantes_ativos()
    crachas_ocupados = [int(v["numero_cracha"]) for v in visitantes_ativos if str(v["numero_cracha"]).isdigit()]
    crachas_disponiveis = [str(i) for i in range(1, 61) if i not in crachas_ocupados]
    
    aba_entrada, aba_saida, aba_ativos = st.tabs([
        "Registrar Entrada", 
        "Registrar Saída",
        "Monitor de Fluxo Interno"
    ])
    
    with aba_entrada:
        col_tit1, col_tit2 = st.columns([35, 1000], vertical_alignment="center")
        with col_tit1:
            st.image("assets/icon_entrada.png", width=32)
        with col_tit2:
            st.markdown("<span style='font-size: 1.75rem; font-weight: 700; line-height: 1; margin-left: -5px;'> Check-in Visitantes</span>", unsafe_allow_html=True)
            
        with st.form(key=f"form_checkin_{st.session_state.form_key}", clear_on_submit=False):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome Completo *", placeholder="Ex: Sadraque de Oliveira")
                cpf = st.text_input("CPF *", placeholder="Apenas números (ex: 12345678900)", max_chars=14)
                telefone = st.text_input("Telefone com DDD *", placeholder="Apenas números (ex: 68999999999)", max_chars=15)
                
            with col2:
                local = st.selectbox("Destino do Visitante *", LOCAIS_SENAI)
                cracha_selecionado = st.selectbox(
                    "Alocar Crachá Disponível *", 
                    ["Selecione..."] + crachas_disponiveis
                )
                objetivo = st.text_area("Objetivo Real da Visita *", placeholder="Ex: Reunião de alinhamento ou manutenção...")
            
            st.write("")
            botao_enviar = st.form_submit_button(label="Finalizar Agendamento e Liberar")
            
            if botao_enviar:
                if not nome or not cpf or not telefone or local == "Selecione o local..." or cracha_selecionado == "Selecione..." or not objetivo:
                    st.warning("⚠️ Atenção: Preencha todos os campos obrigatórios antes de confirmar.")
                elif not validar_cpf(cpf):
                    st.error("❌ CPF inválido. Verifique os números digitados e tente novamente.")
                elif not validar_telefone(telefone):
                    st.error("❌ Telefone inválido. Certifique-se de digitar o DDD e o nono dígito (ex: 68 9XXXX-XXXX).")
                # 4. Se passar por todos os bloqueios, formata e salva no banco!
                else:
                    # Limpa qualquer coisa que não seja número (caso a pessoa tenha digitado traço por costume)
                    cpf_limpo = re.sub(r'[^0-9]', '', cpf)
                    tel_limpo = re.sub(r'[^0-9]', '', telefone)
                    
                    # Aplica a máscara perfeita no CPF
                    cpf_mascara = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
                    
                    # Aplica a máscara perfeita no Telefone (Trata 10 ou 11 dígitos)
                    if len(tel_limpo) == 11:
                        tel_mascara = f"({tel_limpo[:2]}) {tel_limpo[2:7]}-{tel_limpo[7:]}"
                    else:
                        tel_mascara = f"({tel_limpo[:2]}) {tel_limpo[2:6]}-{tel_limpo[6:]}"

                    payload_visitante = {
                        "nome_completo": nome,
                        "cpf": cpf_mascara,          # Agora manda o CPF bonitão
                        "telefone": tel_mascara,     # Agora manda o Telefone bonitão
                        "local_visitado": local,
                        "numero_cracha": cracha_selecionado,
                        "objetivo": objetivo
                    }
                    
                    with st.spinner("Salvando dados de acesso..."):
                        sucesso = st.session_state.db.registrar_entrada(payload_visitante)
                        
                    if sucesso:
                        st.toast("Check-in ativo!", icon="✅")
                        st.markdown(f"""
                        <div style='background-color: #DCFCE7; border-left: 6px solid #16A34A; padding: 20px; border-radius: 8px; margin-top: 15px;'>
                            <h3 style='color: #166534; margin: 0;'>✅ CADASTRO VERIFICADO E LIBERADO!</h3>
                            <p style='color: #1F2937; margin-top: 10px; font-size: 16px;'>
                                O crachá de número <b>{cracha_selecionado}</b> foi alocado com sucesso para <b>{nome.upper()}</b>.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        progresso = st.progress(0)
                        for i in range(100):
                            time.sleep(0.02)
                            progresso.progress(i + 1)
                            
                        # ISSO AQUI LIMPA O FORMULÁRIO APENAS NO SUCESSO!
                        st.session_state.form_key += 1 
                        st.rerun()
                    else:
                        st.error("❌ Falha crítica de comunicação com a planilha. Tente novamente.")
    
    with aba_saida:
        col_tit3, col_tit4 = st.columns([35, 1000], vertical_alignment="center")
        with col_tit3:
            st.image("assets/icon_saida.png", width=32) 
        with col_tit4:
            st.markdown("<span style='font-size: 1.75rem; font-weight: 700; line-height: 1; margin-left: -5px;'>Check-out Visitantes </span>", unsafe_allow_html=True)
            
        st.caption("Localize o número do crachá entregue pelo visitante para registrar a saída imediata.")
        
        if not visitantes_ativos:
            st.info("ℹ️ Portaria limpa. Nenhum crachá em circulação na unidade neste momento.")
        else:
            st.write("")
            visitantes_ativos_ordenados = sorted(visitantes_ativos, key=lambda x: int(x["numero_cracha"]) if str(x["numero_cracha"]).isdigit() else 99)
            
            for visitante in visitantes_ativos_ordenados:
                with st.container():
                    c1, c2, c3 = st.columns([1, 4, 2])
                    with c1:
                        st.markdown(f"<h2 style='color: #F15A24; margin:0;'>🪪 {visitante['numero_cracha']}</h2>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"**{visitante['nome_completo']}**")
                        st.caption(f"📍 {visitante['local_visitado']} | Entrada: {visitante['data_entrada']}")
                    with c3:
                        if st.button(f"📥 Receber Crachá {visitante['numero_cracha']}", key=f"btn_{visitante['id_registro']}", use_container_width=True):
                            with st.spinner("Registrando saída..."):
                                encerrado = st.session_state.db.registrar_saida(visitante['id_registro'])
                            if encerrado:
                                st.toast("Saída concluída!", icon="📤")
                                st.success(f"Crachá {visitante['numero_cracha']} liberado!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Erro ao encerrar visitas.")
    
    with aba_ativos:
        col_tit5, col_tit6 = st.columns([35, 1000], vertical_alignment="center")
        with col_tit5:
            st.image("assets/icon_monitor.png", width=32)
        with col_tit6:
            st.markdown("<span style='font-size: 1.75rem; font-weight: 700; line-height: 1; margin-left: -5px;'>Painel Monitoramento</span>", unsafe_allow_html=True)
            
        if visitantes_ativos:
            import pandas as pd
            df_ativos = pd.DataFrame(visitantes_ativos)
            df_exibicao = df_ativos[["numero_cracha", "nome_completo", "local_visitado", "data_entrada", "telefone", "objetivo"]]
            df_exibicao.columns = ["Crachá", "Nome do Visitante", "Local Destino", "Horário Entrada", "Telefone contato", "Objetivo"]
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
        else:
            st.write("") 
            st.info("ℹ️ Painel limpo. Não ha visitantes ativos ou crachás em circulação na unidade no momento.")
   
    st.markdown("""
        <div class="footer-container">
            <div class="version-text">(AcessoHUB v1.0 - Sistema de Controle de Acesso)</div>
        </div>
    """, unsafe_allow_html=True)

# =========================================================
# INICIALIZAÇÃO E BLINDAGEM DO APLICATIVO (SEMPRE NO FINAL)
# =========================================================
if __name__ == "__main__":
    if not verificar_senha():
        st.stop() 
    main()