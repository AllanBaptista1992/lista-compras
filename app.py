import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# =====================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================
st.set_page_config(

    page_title="Lista de Compras",

    page_icon="🛒",

    layout="wide"

)

# =====================================
# CSS
# =====================================

st.markdown(
    """
    <style>

    /* Área principal */
    /* Espaço do conteúdo */
    .block-container{
        padding-top:7rem !important;
        padding-bottom:5rem !important;
        padding-left:1rem !important;
        padding-right:1rem !important;
    }

    /* Barra superior inteira */
    header[data-testid="stHeader"]{
        top:25px !important;
    }

    /* Rodapé mais para cima */
    footer{
        margin-bottom:70px !important;
    }

    /* Celular */
    @media (max-width:768px){

        .block-container{

            padding-top:7rem !important;

            padding-bottom:7rem !important;

            padding-left:0.7rem !important;

            padding-right:0.7rem !important;

        }

    }

    /* Sidebar menor */
    section[data-testid="stSidebar"]{

        width:200px !important;
        padding-top:6rem !important;
        min-width:200px !important;

    }

    /* Fonte maior do menu */
    section[data-testid="stSidebar"] label,

    section[data-testid="stSidebar"] p,

    section[data-testid="stSidebar"] div[data-baseweb="radio"] label{

        font-size:15px !important;

    }

    section[data-testid="stSidebar"] h1{

        font-size:20px !important;
    }

    /* Botões */
    button{

        border-radius:10px !important;

    }

    /* Tabelas */
    .stDataFrame{

        font-size:16px !important;
    }

    /* Métricas do Dashboard */
    [data-testid="stMetricValue"]{

        font-size:24px !important;

    }

    [data-testid="stMetricLabel"]{

        font-size:18px !important;

    }

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================
# SQLITE
# =====================================
conn = sqlite3.connect(

    "lista_compras.db",

    check_same_thread=False

)

cursor = conn.cursor()

# =====================================
# TABELA COMPRAS
# =====================================
cursor.execute(

    """

    CREATE TABLE IF NOT EXISTS compras(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        data TEXT,

        produto TEXT,

        quantidade INTEGER,

        valor_unitario REAL,

        total_produto REAL

    )


    """

)

# =====================================
# TABELA HISTÓRICO
# =====================================
cursor.execute(

    """

    CREATE TABLE IF NOT EXISTS historico(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        data TEXT,

        total_compra REAL

    )

    """

)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS lista_atual (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT,
        quantidade INTEGER,
        valor_unitario REAL,
        total_produto REAL
    )
    """
)


conn.commit()

# =====================================
# SESSION STATE
# =====================================
if "compras" not in st.session_state:

    df_lista = pd.read_sql_query(

        "SELECT * FROM lista_atual",

        conn

    )

    if df_lista.empty:

        st.session_state.compras = []

    else:

        st.session_state.compras = df_lista.to_dict(
            "records"
        )


if "form_key" not in st.session_state:

    st.session_state.form_key = 0

# =====================================
# MENU LATERAL
# =====================================
with st.sidebar:

    st.title(

        "🛒 Lista de Compras"

    )

    pagina = st.radio(

        "Menu",

        [

            "🛒 Lista de Compras",

            "📊 Dashboard",

            "📅 Histórico"

        ]

    )

    st.divider()

   

# =====================================
# LISTA DE COMPRAS
# =====================================
if pagina == "🛒 Lista de Compras":

    st.title(
        "🛒 Lista de Compras"
    )

    # =====================================
    # FORMULÁRIO
    # =====================================
    with st.form(

        f"form_produto_{st.session_state.form_key}"

    ):

        produto = st.text_input(

            "Produto"

        )

        col1, col2 = st.columns(2)

        with col1:

            quantidade = st.number_input(

                "Quantidade",

                min_value=1,

                step=1

            )

        with col2:

            valor_unitario = st.number_input(

                "Valor Unitário (R$)",
                format="%.2f",
                value=None

            )

            
        adicionar_produto = st.form_submit_button(

            "➕ Adicionar Produto",

            use_container_width=True

        )

    # =====================================
    # ADICIONAR
    # =====================================
    if adicionar_produto:

        if produto.strip() != "":

            st.session_state.compras.append(

                {

                    "Produto": produto.title(),

                    "Quantidade": quantidade,

                    "Valor Unitário": valor_unitario,

                    "Total Produto": quantidade * valor_unitario

                }

            )

            st.session_state.form_key += 1

            st.rerun()

        else:

            st.warning(

                "Informe um produto."

            )

    st.divider()

    # =====================================
    # TABELA
    # =====================================
    if st.session_state.compras:

        st.subheader(

            "Produtos Adicionados"

        )

        df_compras = pd.DataFrame(

            st.session_state.compras

        )

        # Checkbox no final
        df_compras["Excluir"] = False

        df_editado = st.data_editor(

            df_compras,

            hide_index=True,

            use_container_width=True,

            column_config={

                "Produto": st.column_config.TextColumn(

                    "Produto"

                ),

                "Quantidade": st.column_config.NumberColumn(

                    "Qtde"

                ),

                "Valor Unitário": st.column_config.NumberColumn(

                    "Valor Unit.",

                    format="R$ %.2f"

                ),

                "Total Produto": st.column_config.NumberColumn(

                    "Total",

                    format="R$ %.2f"

                ),

                "Excluir": st.column_config.CheckboxColumn(

                    "☑"

                )

            }

        )

        total_geral = df_compras[

            "Total Produto"

        ].sum()

        st.subheader(

            f"💰 Total da Compra: R$ {total_geral:.2f}"

        )

        col1, col2, col3 = st.columns(3)

        # =====================================
        # EXCLUIR SELECIONADOS
        # =====================================
        with col1:

            if st.button(

                "🗑 Excluir Selecionados",

                use_container_width=True,

                key="btn_excluir"

            ):

                df_restante = df_editado[

                    ~df_editado["Excluir"]

                ]

                df_restante = df_restante.drop(

                    columns=["Excluir"]

                )

                st.session_state.compras = (

                    df_restante.to_dict(

                        orient="records"

                    )

                )

                st.rerun()

        # =====================================
        # LIMPAR LISTA
        # =====================================
        with col2:

            if st.button(

                "🧹 Limpar Lista",

                use_container_width=True,

                key="btn_limpar"

            ):

                st.session_state.compras = []

                st.rerun()

        # =====================================
        # FINALIZAR COMPRA
        # =====================================
        with col3:

            finalizar_compra = st.button(

                "✅ Finalizar Compra",

                use_container_width=True,

                key="btn_finalizar"

            )

        # =====================================
        # SALVAR NO SQLITE
        # =====================================
        if finalizar_compra:

            data_atual = datetime.now().strftime(

                "%Y-%m-%d %H:%M:%S"

            )

            for item in st.session_state.compras:

                cursor.execute(

                    """

                    INSERT INTO compras

                    (

                        data,

                        produto,

                        quantidade,

                        valor_unitario,

                        total_produto

                    )

                    VALUES

                    (?, ?, ?, ?, ?)

                    """,

                    (

                        data_atual,

                        item["Produto"],

                        item["Quantidade"],

                        item["Valor Unitário"],

                        item["Total Produto"]

                    )

                )

            cursor.execute(

                """

                INSERT INTO historico

                (

                    data,

                    total_compra

                )

                VALUES

                (?, ?)

                """,

                (

                    data_atual,

                    total_geral

                )

            )

            cursor.execute(

                """
                INSERT INTO lista_atual
                (
                    produto,
                    quantidade,
                    valor_unitario,
                    total_produto
                )

                VALUES
                (?, ?, ?, ?)
                """,
 
                (
                    item["Produto"],

                    item["Quantidade"],

                    item["Valor Unitário"],

                    item["Total Produto"]


                )

            )


            conn.commit()

            cursor.execute(

                "DELETE FROM lista_atual"

            )

            conn.commit()

            st.session_state.compras = []

            st.success(

                "Compra salva com sucesso!"

            )

            st.rerun()


# =====================================
# DASHBOARD
# =====================================
elif pagina == "📊 Dashboard":

    st.title(
        "📊 Dashboard"
    )

    historico = pd.read_sql_query(

        "SELECT * FROM historico",

        conn

    )

    if historico.empty:

        st.info(

            "Nenhuma compra registrada."

        )

    else:

        historico["data"] = pd.to_datetime(

            historico["data"]

        )

        hoje = datetime.now().date()

        mes_atual = datetime.now().month

        ano_atual = datetime.now().year

        total_dia = historico.loc[

            historico["data"].dt.date == hoje,

            "total_compra"

        ].sum()

        total_mes = historico.loc[

            (historico["data"].dt.month == mes_atual)
            &
            (historico["data"].dt.year == ano_atual),

            "total_compra"

        ].sum()

        total_ano = historico.loc[

            historico["data"].dt.year == ano_atual,

            "total_compra"

        ].sum()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(

                "📅 Hoje",

                f"R$ {total_dia:.2f}"

            )

        with col2:

            st.metric(

                "🗓 Mês",

                f"R$ {total_mes:.2f}"

            )

        with col3:

            st.metric(

                "📆 Ano",

                f"R$ {total_ano:.2f}"

            )

        st.divider()

        # =====================================
        # GASTOS POR MÊS
        # =====================================
        historico["Mês"] = historico["data"].dt.strftime(

            "%m/%Y"

        )

        gastos_mes = historico.groupby(

            "Mês"

        )["total_compra"].sum().reset_index()

        st.subheader(

            "📈 Gastos por Mês"

        )

        fig_mes = px.bar(

            gastos_mes,

            x="Mês",

            y="total_compra",

            text_auto=".2f"

        )

        st.plotly_chart(

            fig_mes,

            use_container_width=True

        )

        # =====================================
        # GASTOS POR ANO
        # =====================================
        historico["Ano"] = historico["data"].dt.year

        gastos_ano = historico.groupby(

            "Ano"

        )["total_compra"].sum().reset_index()

        st.subheader(

            "📊 Gastos por Ano"

        )

        fig_ano = px.pie(

            gastos_ano,

            names="Ano",

            values="total_compra"

        )

        st.plotly_chart(

            fig_ano,

            use_container_width=True

        )

# =====================================
# HISTÓRICO
# =====================================
elif pagina == "📅 Histórico":

    st.title(

        "📅 Histórico"

    )

    historico = pd.read_sql_query(

        "SELECT * FROM historico",

        conn

    )

    compras = pd.read_sql_query(

        "SELECT * FROM compras",

        conn

    )

    if not historico.empty:

        historico["data"] = pd.to_datetime(

            historico["data"]

        )

        historico["data"] = historico["data"].dt.strftime(

            "%d/%m/%Y %H:%M"

        )

    if not compras.empty:

        compras["data"] = pd.to_datetime(

            compras["data"]

        )

        compras["data"] = compras["data"].dt.strftime(

            "%d/%m/%Y %H:%M"

        )

    st.subheader(

        "💰 Histórico das Compras"

    )

    st.dataframe(

        historico,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    st.subheader(

        "🛒 Produtos Comprados"

    )

    st.dataframe(

        compras,

        use_container_width=True,

        hide_index=True

    )

    st.divider()

    # =====================================
    # LIMPAR HISTÓRICO
    # =====================================
    if st.button(

        "🗑 Limpar Todo Histórico",

        use_container_width=True,

        key="btn_limpar_historico"

    ):

        cursor.execute(

            "DELETE FROM historico"

        )

        cursor.execute(

            "DELETE FROM compras"

        )

        conn.commit()

        st.success(

            "Histórico apagado com sucesso!"

        )

        st.rerun()

# =====================================
# RODAPÉ
# =====================================
st.divider()

st.caption(

    "🛒 Lista de Compras • Python + Streamlit + SQLite"

)