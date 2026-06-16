import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

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

/* Espaçamento */
.block-container{

    padding-top:8rem;

    padding-bottom:1rem;

    padding-left:1rem;

    padding-right:1rem;

}

/* Botões */
.stButton button{

    border-radius:10px;

}

/* Dashboard */
[data-testid="metric-container"]{

    border-radius:15px;

    padding:15px;

}

/* Celular */
@media (max-width:768px){

    .block-container{

        padding-left:0.5rem;

        padding-right:0.5rem;

    }

}

</style>
""",

    unsafe_allow_html=True

)

# =====================================
# BANCO SQLITE
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

conn.commit()

# =====================================
# SESSION STATE
# =====================================
if "compras" not in st.session_state:

    st.session_state.compras = []

if "indice_edicao" not in st.session_state:

    st.session_state.indice_edicao = None

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

    tema = st.selectbox(

        "🎨 Tema",

        [

            "Claro",

            "Escuro"

        ]

    )

# =====================================
# TEMA ESCURO
# =====================================
if tema == "Escuro":

    st.markdown(

        """
        <style>

        .stApp{

            background-color:#0E1117;

            color:white;

        }

        </style>
        """,

        unsafe_allow_html=True

    )


# =====================================
# LISTA DE COMPRAS
# =====================================
if pagina == "🛒 Lista de Compras":

    st.markdown(
        "## 🛒 Lista de Compras"
    )

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

            valor = st.number_input(

                "Valor Unitário (R$)",

                min_value=0.0,

                format="%.2f"

            )

        adicionar = st.form_submit_button(

            "➕ Adicionar Produto",

            use_container_width=True

        )

    # =====================================
    # ADICIONAR
    # =====================================
    if adicionar:

        if produto.strip() != "":

            total_produto = quantidade * valor

            st.session_state.compras.append(

                {

                    "Produto": produto.title(),

                    "Quantidade": quantidade,

                    "Valor Unitário": valor,

                    "Total Produto": total_produto

                }

            )

            st.session_state.form_key += 1

            st.rerun()

        else:

            st.warning(
                "Informe o produto."
            )

    st.divider()

    # =====================================
    # TABELA
    # =====================================
    if st.session_state.compras:

        st.subheader(
            "Produtos Adicionados"
        )

        h1, h2, h3, h4, h5, h6 = st.columns(
            [3, 1, 1.5, 1.5, 0.7, 0.7]
        )

        h1.markdown("**Produto**")
        h2.markdown("**Qtde**")
        h3.markdown("**Valor Unit.**")
        h4.markdown("**Total**")
        h6.markdown("**❌**")

        st.divider()

        total_geral = 0

        for i, item in enumerate(
            st.session_state.compras
        ):

            total_geral += item[
                "Total Produto"
            ]

            c1, c2, c3, c4, c5 = st.columns(
                [3, 1, 1.5, 1.5, 1.5]
            )

            c1.write(
                item["Produto"]
            )

            c2.write(
                item["Quantidade"]
            )

            c3.write(
                f'R$ {item["Valor Unitário"]:.2f}'
            )

            c4.write(
                f'R$ {item["Total Produto"]:.2f}'
            )

            with c5:

                if st.button(

                    "❌",

                    key=f"excluir_{i}"

                ):

                    st.session_state.compras.pop(
                        i
                    )

                    st.rerun()

            st.divider()

        st.subheader(

            f"💰 Total da Compra: R$ {total_geral:.2f}"

        )

        col1, col2 = st.columns(2)

        with col1:

            limpar_lista = st.button(

                "🧹 Limpar Lista",

                use_container_width=True,

                key="btn_limpar_lista"

            )

        with col2:

            finalizar_compra = st.button(

                "✅ Finalizar Compra",

                use_container_width=True,

                key="btn_finalizar"

            )

        # =====================================
        # LIMPAR LISTA
        # =====================================
        if limpar_lista:

            st.session_state.compras = []

            st.rerun()

        # =====================================
        # FINALIZAR COMPRA
        # =====================================
        if finalizar_compra:

            data_atual = datetime.now().strftime(
                "%d/%m/%Y"
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

    st.markdown(
        "## 📊 Dashboard"
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

        # =====================================
        # GASTOS POR MÊS
        # =====================================
        gastos_mes = historico.copy()

        gastos_mes["Mês"] = gastos_mes["data"].dt.strftime(
            "%m/%Y"
        )

        gastos_mes = gastos_mes.groupby(
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
        gastos_ano = historico.copy()

        gastos_ano["Ano"] = gastos_ano["data"].dt.year

        gastos_ano = gastos_ano.groupby(
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

    st.markdown(
        "## 📅 Histórico"
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