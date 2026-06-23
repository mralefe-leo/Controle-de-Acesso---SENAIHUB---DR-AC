import streamlit as st
from database import DatabaseManager
import os
import time
import re
from datetime import datetime, timedelta


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
            
            img_tag = f'<img src="data:image/png;base64,{logo_b64}" style="max-width: 300px; width: 100%; margin: 0 auto; display: block; margin-bottom: 20px;">'
            
    _, col_login, _ = st.columns([1, 1.2, 1])
    
    with col_login:
        st.write("")
        st.write("")
        st.write("") 
        st.markdown(f"{img_tag}", unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #FFFFFF; margin-bottom: 30px; font-weight: 700;'>🔒 Acesso Restrito</h2>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            senha_digitada = st.text_input("Senha de Acesso", type="password", placeholder="Digite a senha corporativa...")
            submit_login = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if submit_login:
                if senha_digitada == st.secrets["SENHA_PORTARIA"]:
                    st.session_state.autenticado = True
                    st.rerun() 
                else:
                    st.error("❌ Senha incorreta. Acesso negado.")
                    
    return False


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
            
        # ==============================================================
        # GERENCIADOR DE TELAS (BUSCA -> CADASTRO)
        # ==============================================================
        if "etapa_checkin" not in st.session_state:
            st.session_state.etapa_checkin = "busca"
        if "visitante_temp" not in st.session_state:
            st.session_state.visitante_temp = {}

        # Mostra o card de sucesso após um registro finalizado
        if "mensagem_sucesso" in st.session_state:
            st.toast("Check-in ativo!", icon="✅")
            st.markdown(f"""
            <div style='background-color: #DCFCE7; border-left: 6px solid #16A34A; padding: 20px; border-radius: 8px; margin-bottom: 25px;'>
                <h3 style='color: #166534; margin: 0;'>✅ CADASTRO VERIFICADO E LIBERADO!</h3>
                <p style='color: #1F2937; margin-top: 10px; font-size: 16px;'>
                    O crachá de número <b>{st.session_state.mensagem_sucesso['cracha']}</b> foi alocado com sucesso para <b>{st.session_state.mensagem_sucesso['nome']}</b>.
                </p>
            </div>
            """, unsafe_allow_html=True)
            del st.session_state["mensagem_sucesso"] # Limpa a mensagem


        # --- TELA 1: BUSCAR CPF ---
        if st.session_state.etapa_checkin == "busca":
            st.markdown("### Passo 1: Identificação do Visitante")
            st.info("Digite o CPF. Se o visitante já possuir cadastro na unidade, puxaremos os dados automaticamente!")
            
            col_b1, col_b2 = st.columns([2, 1], vertical_alignment="bottom")
            with col_b1:
                cpf_busca = st.text_input("CPF do Visitante", placeholder="Apenas números (ex: 12345678900)", max_chars=14)
            with col_b2:
                if st.button("Buscar Cadastro", type="primary", use_container_width=True):
                    if not validar_cpf(cpf_busca):
                        st.error("❌ CPF inválido. Verifique os números digitados.")
                    else:
                        with st.spinner("Buscando no banco de dados..."):
                            visitante_db = st.session_state.db.buscar_visitante_por_cpf(cpf_busca)
                            
                            cpf_limpo = re.sub(r'[^0-9]', '', cpf_busca)
                            cpf_mascara = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
                            
                            if visitante_db:
                                st.session_state.visitante_temp = visitante_db
                                st.session_state.etapa_checkin = "encontrado"
                            else:
                                st.session_state.visitante_temp = {"cpf": cpf_mascara, "nome_completo": "", "telefone": ""}
                                st.session_state.etapa_checkin = "novo"
                            st.rerun()

        # --- TELA 2: FORMULÁRIO DE ENTRADA ---
        elif st.session_state.etapa_checkin in ["encontrado", "novo"]:
            is_novo = (st.session_state.etapa_checkin == "novo")
            
            if is_novo:
                st.warning("⚠️ **Novo Visitante:** CPF não encontrado. Preencha os dados completos para efetuar o primeiro cadastro.")
            else:
                st.success(f"✅ **Visitante Localizado:** Bem-vindo(a) de volta, {st.session_state.visitante_temp['nome_completo']}!")

            with st.form(key=f"form_checkin_{st.session_state.form_key}", clear_on_submit=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Se for visitante antigo (não é novo), bloqueia os campos de nome, cpf e telefone (disabled=True)
                    nome = st.text_input("Nome Completo *", value=st.session_state.visitante_temp["nome_completo"], disabled=not is_novo)
                    cpf = st.text_input("CPF *", value=st.session_state.visitante_temp["cpf"], disabled=True)
                    telefone = st.text_input("Telefone com DDD *", value=st.session_state.visitante_temp["telefone"], disabled=not is_novo)
                    
                with col2:
                    local = st.selectbox("Destino do Visitante *", LOCAIS_SENAI)
                    cracha_selecionado = st.selectbox(
                        "Alocar Crachá Disponível *", 
                        ["Selecione..."] + crachas_disponiveis
                    )
                    objetivo = st.text_area("Objetivo Real da Visita *", placeholder="Ex: Reunião de alinhamento ou manutenção...")
                
                st.write("")
                # Cria 3 colunas do mesmo tamanho: Esquerda, Meio (vazio) e Direita
                col_btn1, col_espaco, col_btn2 = st.columns([1, 1, 1])
                
                with col_btn1:
                    
                    if st.form_submit_button("⬅️ Cancelar / Nova Busca", use_container_width=True):
                        st.session_state.etapa_checkin = "busca"
                        st.rerun()
                        
                with col_btn2:
                   
                    botao_enviar = st.form_submit_button(label="Finalizar Agendamento e Liberar Entrada", type="primary", use_container_width=True)
                
                if botao_enviar:
                    # Recupera os dados (campos desativados não passam o valor no submit no Streamlit, então pegamos da memória)
                    nome_final = nome if is_novo else st.session_state.visitante_temp["nome_completo"]
                    telefone_final = telefone if is_novo else st.session_state.visitante_temp["telefone"]
                    cpf_final = st.session_state.visitante_temp["cpf"]

                    if not nome_final or not telefone_final or local == "Selecione o local..." or cracha_selecionado == "Selecione..." or not objetivo:
                        st.warning("⚠️ Atenção: Preencha todos os campos obrigatórios.")
                    elif is_novo and not validar_telefone(telefone_final):
                        st.error("❌ Telefone inválido. Certifique-se de digitar o DDD e o nono dígito.")
                    else:
                        # Formata o telefone apenas se for novo (o antigo já vem formatado do banco)
                        if is_novo:
                            tel_limpo = re.sub(r'[^0-9]', '', telefone_final)
                            if len(tel_limpo) == 11:
                                telefone_final = f"({tel_limpo[:2]}) {tel_limpo[2:7]}-{tel_limpo[7:]}"
                            else:
                                telefone_final = f"({tel_limpo[:2]}) {tel_limpo[2:6]}-{tel_limpo[6:]}"
                            
                        payload_visitante = {
                            "nome_completo": nome_final,
                            "cpf": cpf_final,          
                            "telefone": telefone_final,     
                            "local_visitado": local,
                            "numero_cracha": cracha_selecionado,
                            "objetivo": objetivo
                        }
                        
                        with st.spinner("Salvando dados de acesso..."):
                            sucesso = st.session_state.db.registrar_entrada(payload_visitante, is_novo=is_novo)
                            
                        if sucesso:
                            # Prepara a mensagem verde de sucesso e volta para a tela de busca!
                            st.session_state.mensagem_sucesso = {
                                "nome": nome_final.upper(),
                                "cracha": cracha_selecionado
                            }
                            st.session_state.etapa_checkin = "busca"
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
        col_tit5, col_tit6 = st.columns([35, 1000])
        with col_tit5:
            st.image("assets/icon_monitor.png", width=32)
        with col_tit6:
            st.markdown("<span style='font-size: 1.75rem; font-weight: 700; line-height: 1; margin-left: -5px;'>Painel de Monitoramento e Histórico</span>", unsafe_allow_html=True)
            
        st.write("")
        
        
        if "filtro_monitor" not in st.session_state:
            st.session_state.filtro_monitor = "🟢 Visitantes Ativos Agora"
        
        
        col_f1, col_f2 = st.columns([1.5, 1])
        
        with col_f1:
            st.radio(
                "Modo de Visualização:",
                ["🟢 Visitantes Ativos Agora", "📅 Histórico por Data"],
                horizontal=True,
                key="filtro_monitor" 
            )
            
        
        if st.session_state.filtro_monitor == "🟢 Visitantes Ativos Agora":
            dados_exibicao = visitantes_ativos
            texto_vazio = "ℹ️ Portaria limpa. Não há visitantes ativos ou crachás em circulação na unidade no momento."
            
        else:
            with col_f2:
                data_selecionada = st.date_input(
                    "Escolha a data para consulta:", 
                    (datetime.utcnow() - timedelta(hours=5)).date(),
                    key="calendario_busca"
                )
            
            data_busca = data_selecionada.strftime("%d/%m/%Y")
            
            with st.spinner("Buscando registros no histórico..."):
                todos_registros = st.session_state.db.listar_todos_registros()
            
            dados_exibicao = [
                r for r in todos_registros 
                if str(r.get("data_entrada", "")).startswith(data_busca)
            ]
            texto_vazio = f"ℹ️ Nenhum registro de visitante encontrado para o dia {data_busca}."

        # 3. EXIBIÇÃO DA TABELA BLINDADA
        if dados_exibicao:
            import pandas as pd
            df_ativos = pd.DataFrame(dados_exibicao)
            
            colunas_necessarias = ["numero_cracha", "nome_completo", "local_visitado", "data_entrada", "data_saida", "telefone", "objetivo"]
            for col in colunas_necessarias:
                if col not in df_ativos.columns:
                    df_ativos[col] = ""
            
            df_exibicao = df_ativos[["numero_cracha", "nome_completo", "local_visitado", "data_entrada", "data_saida", "telefone", "objetivo"]]
            df_exibicao.columns = ["Crachá", "Nome do Visitante", "Local Destino", "Horário Entrada", "Horário Saída", "Telefone", "Objetivo Visita"]
            
            
            chave_tabela = f"tabela_{st.session_state.filtro_monitor}_{st.session_state.get('form_key', 0)}"
            
            st.dataframe(
                df_exibicao, 
                use_container_width=True, 
                hide_index=True, 
                key=chave_tabela 
            )
        else:
            st.write("") 
            st.info(texto_vazio)


if __name__ == "__main__":
    if not verificar_senha():
        st.stop() 
    main()