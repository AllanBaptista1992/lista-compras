import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
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
# CONEXÃO COM O BANCO
# =====================================
conn = sqlite3.connect(
    "lista_compras.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =====================================
# CRIA AS TABELAS
# =====================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS compras(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    produto TEXT,
    quantidade INTEGER,
    valor_unitario REAL,
    total_produto REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS historico(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    total_compra REAL
)
""")

conn.commit()

# =====================================
# TEMA
# =====================================
tema = st.sidebar.radio(
    "Tema",
    [
        "☀ Claro",
        "🌙 Escuro"
    ]
)

if tema == "🌙 Escuro":

    st.markdown("""
    <style>

    .stApp{
        background-color:#1E1E1E;
        color:white;
    }

    </style>
    """,
    unsafe_allow_html=True)

# =====================================
# MENU
# =====================================
pagina = st.sidebar.radio(

    "Menu",

    [

        "🛒 Compras",
        "📊 Dashboard",
        "📅 Histórico"

    ]

)

# =====================================
# SESSION STATE
# =====================================
if "compras" not in st.session_state:
    st.session_state.compras = []

if "produto_input" not in st.session_state:
    st.session_state.produto_input = ""

if "quantidade_input" not in st.session_state:
    st.session_state.quantidade_input = 1

if "valor_input" not in st.session_state:
    st.session_state.valor_input = 0.0

# =====================================
# PÁGINA COMPRAS
# =====================================
if pagina == "🛒 Compras":

    st.title(
        "🛒 Lista de Compras"
    )

    st.divider()

    with st.form("form_produto"):

        produto = st.text_input(

            "Produto",

            placeholder="Ex: Arroz",

            key="produto_input"

        )

        quantidade = st.number_input(

            "Quantidade",

            min_value=1,

            key="quantidade_input"

        )

        valor = st.number_input(

            "Valor Unitário (R$)",

            min_value=0.0,

            format="%.2f",

            key="valor_input"

        )

        adicionar = st.form_submit_button(

            "➕ Adicionar Produto",

            use_container_width=True

        )

    if adicionar:

        total_produto = quantidade * valor

        st.session_state.compras.append({

            "Produto": produto.title(),

            "Quantidade": quantidade,

            "Valor Unitário": valor,

            "Total Produto": total_produto

        })

        
        st.rerun()

    # =====================================
    # MOSTRAR PRODUTOS
    # =====================================
    if len(st.session_state.compras) > 0:

        st.divider()

        st.subheader(
            "🛒 Produtos"
        )

        df = pd.DataFrame(
            st.session_state.compras
        )

        total_geral = df[
            "Total Produto"
        ].sum()

        st.success(
            f"💰 Total da Compra: R$ {total_geral:.2f}"
        )

        # =====================================
        # LISTA DOS PRODUTOS
        # =====================================
        for i, item in enumerate(
            st.session_state.compras
        ):

            with st.container(border=True):

                col1, col2, col3, col4, col5, col6 = st.columns(
                    [3,1,1,1,0.5,0.5]
                )

                with col1:
                    st.write(
                        f"**{item['Produto']}**"
                    )

                with col2:
                    st.write(
                        item["Quantidade"]
                    )

                with col3:
                    st.write(
                        f"R$ {item['Valor Unitário']:.2f}"
                    )

                with col4:
                    st.write(
                        f"R$ {item['Total Produto']:.2f}"
                    )

                # EDITAR
                with col5:

                    if st.button(
                        "✏",
                        key=f"editar_{i}"
                    ):

                        st.session_state.produto_editar = i

                # EXCLUIR
                with col6:

                    if st.button(
                        "❌",
                        key=f"excluir_{i}"
                    ):

                        st.session_state.compras.pop(i)

                        st.rerun()

        # =====================================
        # EDITAR PRODUTO
        # =====================================
        if "produto_editar" in st.session_state:

            indice = st.session_state.produto_editar

            st.divider()

            st.subheader(
                "✏ Editar Produto"
            )

            novo_nome = st.text_input(

                "Produto",

                value=st.session_state.compras[indice]["Produto"]

            )

            nova_quantidade = st.number_input(

                "Quantidade",

                min_value=1,

                value=int(
                    st.session_state.compras[indice]["Quantidade"]
                )

            )

            novo_valor = st.number_input(

                "Valor Unitário",

                min_value=0.0,

                value=float(
                    st.session_state.compras[indice]["Valor Unitário"]
                )

            )

            if st.button(
                "💾 Salvar Alterações"
            ):

                st.session_state.compras[indice] = {

                    "Produto": novo_nome.title(),

                    "Quantidade": nova_quantidade,

                    "Valor Unitário": novo_valor,

                    "Total Produto":
                    nova_quantidade * novo_valor

                }

                del st.session_state.produto_editar

                st.rerun()

        st.divider()

        col1, col2 = st.columns(2)

        # =====================================
        # LIMPAR LISTA
        # =====================================
        with col1:

            if st.button(

                "🧹 Limpar Lista",

                use_container_width=True

            ):

                st.session_state.compras = []

                st.rerun()

        # =====================================
        # FINALIZAR COMPRA
        # =====================================
        with col2:

            if st.button(

                "✅ Finalizar Compra",

                use_container_width=True

            ):

                data_atual = datetime.now().strftime(
                    "%d/%m/%Y"
                )

                # Salvar produtos
                for item in st.session_state.compras:

                    cursor.execute(

                        """
                        INSERT INTO compras(
                            data,
                            produto,
                            quantidade,
                            valor_unitario,
                            total_produto
                        )
                        VALUES(?,?,?,?,?)
                        """,

                        (

                            data_atual,

                            item["Produto"],

                            item["Quantidade"],

                            item["Valor Unitário"],

                            item["Total Produto"]

                        )

                    )

                # Salvar total da compra
                cursor.execute(

                    """
                    INSERT INTO historico(
                        data,
                        total_compra
                    )
                    VALUES(?,?)
                    """,

                    (

                        data_atual,

                        total_geral

                    )

                )

                conn.commit()

                st.session_state.compras = []

                st.success(
                    "✅ Compra salva com sucesso!"
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

            historico["data"],

            format="%d/%m/%Y"

        )

        hoje = datetime.now().date()

        mes_atual = datetime.now().month

        ano_atual = datetime.now().year

        total_dia = historico.loc[

            historico["data"].dt.date == hoje,

            "total_compra"

        ].sum()

        total_mes = historico.loc[

            historico["data"].dt.month == mes_atual,

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

        # ==========================
        # GASTOS POR MÊS
        # ==========================
        gastos_mes = historico.copy()

        gastos_mes["Mês"] = gastos_mes["data"].dt.strftime("%m/%Y")

        gastos_mes = gastos_mes.groupby(

            "Mês"

        )["total_compra"].sum().reset_index()

        st.subheader(

            "📊 Gastos por Mês"

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

        # ==========================
        # GASTOS POR ANO
        # ==========================
        gastos_ano = historico.copy()

        gastos_ano["Ano"] = gastos_ano["data"].dt.year

        gastos_ano = gastos_ano.groupby(

            "Ano"

        )["total_compra"].sum().reset_index()

        st.subheader(

            "📆 Gastos por Ano"

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

    st.subheader(

        "💰 Histórico das Compras"

    )

    st.dataframe(

        historico,

        use_container_width=True

    )

    st.divider()

    st.subheader(

        "🛒 Produtos Comprados"

    )

    st.dataframe(

        compras,

        use_container_width=True

    )

    st.divider()

    # =====================================
    # LIMPAR HISTÓRICO
    # =====================================
    if st.button(

        "🗑 Limpar Todo Histórico",

        use_container_width=True

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

    "🛒 Sistema de Lista de Compras com SQLite"

)
