import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# =====================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================
st.set_page_config(
    page_title="Lista de Compras",
    page_icon="🛒",
    layout="wide"
)

# =====================================
# TEMA
# =====================================
tema = st.sidebar.radio(
    "Tema",
    ["☀ Claro", "🌙 Escuro"]
)

if tema == "🌙 Escuro":

    st.markdown("""
    <style>

    .stApp{
        background-color:#1E1E1E;
        color:white;
    }

    </style>
    """, unsafe_allow_html=True)

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
# PASTA DADOS
# =====================================
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PASTA_DADOS = os.path.join(
    BASE_DIR,
    "dados"
)

os.makedirs(
    PASTA_DADOS,
    exist_ok=True
)

arquivo_diario = os.path.join(
    PASTA_DADOS,
    "historico_diario.csv"
)

arquivo_mensal = os.path.join(
    PASTA_DADOS,
    "historico_mensal.csv"
)

arquivo_anual = os.path.join(
    PASTA_DADOS,
    "historico_anual.csv"
)

# =====================================
# CRIA CSV AUTOMATICAMENTE
# =====================================
if not os.path.exists(arquivo_diario):

    pd.DataFrame(
        columns=[
            "Data",
            "Total_Gasto"
        ]
    ).to_csv(
        arquivo_diario,
        index=False
    )

if not os.path.exists(arquivo_mensal):

    pd.DataFrame({

        "Mes":[

            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro"

        ],

       "Total_Gasto":[0.0]*12

    }).to_csv(

        arquivo_mensal,

        index=False

    )

if not os.path.exists(arquivo_anual):

    pd.DataFrame({

        "Ano":[datetime.now().year],

        "Total_Gasto":[0.0]

    }).to_csv(

        arquivo_anual,

        index=False

    )

# =====================================
# SESSION
# =====================================
if "compras" not in st.session_state:

    st.session_state.compras = []

# =====================================
# PÁGINA COMPRAS
# =====================================
if pagina == "🛒 Compras":

    st.title("🛒 Lista de Compras")

    st.divider()

    with st.form("form_produto"):

        produto = st.text_input(
            "Produto",
            placeholder="Ex: Arroz"
        )

        quantidade = st.number_input(

            "Quantidade",

            min_value=1,

            value=1

        )

        valor = st.number_input(

            "Valor Unitário (R$)",
            
            min_value=0.0,

            value=0.0,

            format="%.2f"

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

        st.subheader("🛒 Produtos")

        df = pd.DataFrame(
            st.session_state.compras
        )

        total_geral = df[
            "Total Produto"
        ].sum()

        st.success(
            f"💰 Total da Compra: R$ {total_geral:.2f}"
        )

        # ==============================
        # LISTA DOS PRODUTOS
        # ==============================
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

        # ==============================
        # EDITAR PRODUTO
        # ==============================
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

        # ==============================
        # LIMPAR LISTA
        # ==============================
        with col1:

            if st.button(

                "🧹 Limpar Lista",

                use_container_width=True

            ):
                st.session_state.compras = []
                st.rerun()
                

        # ==============================
        # FINALIZAR COMPRA
        # ==============================
        with col2:

            if st.button(

                "✅ Finalizar Compra",

                use_container_width=True

            ):

                hoje = datetime.now().strftime(
                    "%d/%m/%Y"
                )

                # HISTÓRICO DIÁRIO
                historico_diario = pd.read_csv(
                    arquivo_diario
                )

                nova_linha = pd.DataFrame({

                    "Data":[hoje],

                    "Total_Gasto":[total_geral]

                })

                historico_diario = pd.concat(

                    [

                        historico_diario,

                        nova_linha

                    ],

                    ignore_index=True

                )

                historico_diario.to_csv(

                    arquivo_diario,

                    index=False

                )

                # HISTÓRICO MENSAL
                historico_mensal = pd.read_csv(
                    arquivo_mensal
                )

                meses = {

                    1:"Janeiro",
                    2:"Fevereiro",
                    3:"Março",
                    4:"Abril",
                    5:"Maio",
                    6:"Junho",
                    7:"Julho",
                    8:"Agosto",
                    9:"Setembro",
                    10:"Outubro",
                    11:"Novembro",
                    12:"Dezembro"

                }

                mes_atual = meses[
                    datetime.now().month
                ]

                historico_mensal.loc[

                    historico_mensal["Mes"]
                    == mes_atual,

                    "Total_Gasto"

                ] += total_geral

                historico_mensal.to_csv(

                    arquivo_mensal,

                    index=False

                )

                # HISTÓRICO ANUAL
                historico_anual = pd.read_csv(
                    arquivo_anual
                )

                ano_atual = datetime.now().year

                if ano_atual not in historico_anual["Ano"].values:

                    nova_linha = pd.DataFrame({

                        "Ano":[ano_atual],

                        "Total_Gasto":[0.0]

                    })

                    historico_anual = pd.concat(

                        [

                            historico_anual,

                            nova_linha

                        ],

                        ignore_index=True

                    )

                historico_anual.loc[

                    historico_anual["Ano"]
                    == ano_atual,

                    "Total_Gasto"

                ] += total_geral

                historico_anual.to_csv(

                    arquivo_anual,

                    index=False

                )
                st.session_state.compras = []
                st.rerun()
                st.success(
                    "✅ Compra salva com sucesso!"
                )


# =====================================
# DASHBOARD
# =====================================
elif pagina == "📊 Dashboard":

    st.title("📊 Dashboard")

    historico_diario = pd.read_csv(
        arquivo_diario
    )

    historico_mensal = pd.read_csv(
        arquivo_mensal
    )

    historico_anual = pd.read_csv(
        arquivo_anual
    )

    # ==============================
    # TOTAL DO DIA
    # ==============================
    hoje = datetime.now().strftime(
        "%d/%m/%Y"
    )

    total_dia = 0

    if not historico_diario.empty:

        total_dia = historico_diario.loc[
            historico_diario["Data"] == hoje,
            "Total_Gasto"
        ].sum()

    # ==============================
    # TOTAL DO MÊS
    # ==============================
    meses = {

        1:"Janeiro",
        2:"Fevereiro",
        3:"Março",
        4:"Abril",
        5:"Maio",
        6:"Junho",
        7:"Julho",
        8:"Agosto",
        9:"Setembro",
        10:"Outubro",
        11:"Novembro",
        12:"Dezembro"

    }

    mes_atual = meses[
        datetime.now().month
    ]

    total_mes = historico_mensal.loc[
        historico_mensal["Mes"] == mes_atual,
        "Total_Gasto"
    ].sum()

    # ==============================
    # TOTAL DO ANO
    # ==============================
    ano_atual = datetime.now().year

    total_ano = historico_anual.loc[
        historico_anual["Ano"] == ano_atual,
        "Total_Gasto"
    ].sum()

    # ==============================
    # CARDS
    # ==============================
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

    # ==============================
    # GRÁFICO MENSAL
    # ==============================
    st.subheader(
        "📊 Gastos por Mês"
    )

    grafico_mes = px.bar(

        historico_mensal,

        x="Mes",

        y="Total_Gasto",

        text_auto=".2f"

    )

    st.plotly_chart(

        grafico_mes,

        use_container_width=True

    )

    # ==============================
    # GRÁFICO ANUAL
    # ==============================
    st.subheader(
        "📆 Gastos por Ano"
    )

    grafico_ano = px.pie(

        historico_anual,

        names="Ano",

        values="Total_Gasto"

    )

    st.plotly_chart(

        grafico_ano,

        use_container_width=True

    )

# =====================================
# HISTÓRICO
# =====================================
elif pagina == "📅 Histórico":

    st.title(
        "📅 Histórico"
    )

    historico_diario = pd.read_csv(
        arquivo_diario
    )

    historico_mensal = pd.read_csv(
        arquivo_mensal
    )

    historico_anual = pd.read_csv(
        arquivo_anual
    )

    st.subheader(
        "📅 Histórico Diário"
    )

    st.dataframe(

        historico_diario,

        use_container_width=True

    )

    st.divider()

    st.subheader(
        "🗓 Histórico Mensal"
    )

    st.dataframe(

        historico_mensal,

        use_container_width=True

    )

    if st.button(
        "🗑 Limpar Histórico Mensal",
        use_container_width=True,
        key="limpar_historico_mensal"
    ):

        # Limpar histórico mensal
        historico_mensal = pd.DataFrame({

            "Mes":[
                "Janeiro",
                "Fevereiro",
                "Março",
                "Abril",
                "Maio",
                "Junho",
                "Julho",
                "Agosto",
                "Setembro",
                "Outubro",
                "Novembro",
                "Dezembro"
            ],

            "Total_Gasto":[0.0]*12

        })

        historico_mensal.to_csv(
            arquivo_mensal,
            index=False
        )

        # Limpar histórico anual
        historico_anual = pd.DataFrame({

            "Ano":[datetime.now().year],

            "Total_Gasto":[0.0]

        })

        historico_anual.to_csv(
            arquivo_anual,
            index=False
        )

        st.success(
            "Histórico mensal e anual limpos com sucesso!"
        )

        st.rerun()

    st.divider()

    st.subheader(
        "📆 Histórico Anual"
    )

    st.dataframe(

        historico_anual,

        use_container_width=True

    )

# =====================================
# RODAPÉ
# =====================================
st.divider()

st.caption(
    "🛒 Sistema de Lista de Compras"
)