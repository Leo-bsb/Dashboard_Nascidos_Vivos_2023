import pandas as pd
import plotly.express as px
import streamlit as st
import squarify


df_filtro = pd.read_csv("Nascidos_Vivos_Dashboard_Reduzido.csv")


## Limpeza consolidada diretamente no df_filtro
df_filtro["Raça e Cor"] = df_filtro["Raça e Cor do Bebê"]
df_filtro["Unidade Federativa"] = df_filtro["UF"]
df_filtro.loc[~df_filtro["Raça e Cor"].isin(['Amarela', 'Branca', 'Indígena', 'Parda', 'Preta']), "Raça e Cor"] = None


df_filtro["Estado Civil da Mãe"] = df_filtro["Estado Civil da Mãe"].replace("Separada judicialmente/divorciada", "Divorciada")
df_filtro["Local de Nascimento"] = df_filtro["Local de Nascimento"].replace("Outros estabelecimentos de saúde", "Outros")
df_filtro.loc[~df_filtro["Local de Nascimento"].isin(['Hospital', 'Domicílio', 'Outros']), "Local de Nascimento"] = None

df_filtro.loc[~df_filtro["Indução de Parto"].isin(['Não', 'Sim']), "Indução de Parto"] = None
df_filtro.loc[~df_filtro["Tipo de Apresentação"].isin(['Cefálico', 'Pélvica ou podálica', 'Transversa']), "Tipo de Apresentação"] = None

df_filtro.drop(columns=["Raça e Cor do Bebê"], inplace=True, errors='ignore')
df_filtro.drop(columns=["UF"], inplace=True, errors='ignore')

# Copiar para df principal
df = df_filtro.copy()


st.set_page_config(
    page_title="Dashboard de Nascidos Vivos",
    page_icon="📈",
    layout="wide",
)

#faixa azul
st.markdown(
    """
    <style>
        .faixa-azul {
            background-color: #022857;
            color: white;
            padding: 30px;
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            border-radius: 15px 15px 0 0;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="faixa-azul">Nascidos Vivos - 2023</div>', unsafe_allow_html=True)


col1, col2 = st.columns(2)

with col1:
    st.subheader("Filtros")
    col1_esquerda, col2_esquerda, col3_esquerda = st.columns(3)

    # Filtro 1 - Bebê
    with col1_esquerda:
        opcoes_filtro1 = {
            "Sexo": ["Todos"] + list(df_filtro["Sexo"].dropna().unique()),
            "Raça e Cor": ["Todos"] + list(df_filtro["Raça e Cor"].dropna().unique()),
        }
        filtro_selecionado1 = st.selectbox("Filtros do Bebê:", list(opcoes_filtro1.keys()))
        valor_selecionado1 = st.selectbox(f"Selecione uma opção de {filtro_selecionado1}:", opcoes_filtro1[filtro_selecionado1])

        if valor_selecionado1 != "Todos":
            df = df[df[filtro_selecionado1] == valor_selecionado1]

    #################################################

    # Filtro 2 - Gestação e Nascimento
    with col2_esquerda:
        opcoes_filtro2 = {
            "Local de Nascimento": ["Todos"] + list(df_filtro["Local de Nascimento"].dropna().unique()),
            "Indução de Parto": ["Todos"] + list(df_filtro["Indução de Parto"].dropna().unique()),
            "Tipo de Apresentação": ["Todos"] + list(df_filtro["Tipo de Apresentação"].dropna().unique()),
             "Unidade Federativa": ["Todos"] + list(df_filtro["Unidade Federativa"].dropna().unique()),
        }
        filtro_selecionado2 = st.selectbox("Filtros do Parto:", list(opcoes_filtro2.keys()))
        valor_selecionado2 = st.selectbox(f"Selecione uma opção de {filtro_selecionado2}:", opcoes_filtro2[filtro_selecionado2])

        if valor_selecionado2 != "Todos":
            df = df[df[filtro_selecionado2] == valor_selecionado2]

################################################

    # filtro 3 - Pais
    with col3_esquerda:
        opcoes_filtro3 = {
            "Estado Civil da Mãe": ["Todos"] + list(df_filtro["Estado Civil da Mãe"].dropna().unique()),
        }
        filtro_selecionado3 = st.selectbox("Filtros dos Pais:", list(opcoes_filtro3.keys()))
        valor_selecionado3 = st.selectbox(f"Selecione uma opção de {filtro_selecionado3}:", opcoes_filtro3[filtro_selecionado3])

        if valor_selecionado3 != "Todos":
            df = df[df[filtro_selecionado3] == valor_selecionado3]

    st.divider()

 ######################################################


    contagem = df['Unidade Federativa'].value_counts().reset_index()
    contagem.columns = ['Unidade Federativa', 'quantidade']
    contagem = contagem.sort_values(by='quantidade', ascending=True)


    fig_uf = px.bar(
        contagem, 
        x='quantidade', 
        y='Unidade Federativa', 
        text='quantidade',
        orientation='h',
        title='Nascimentos por Unidade Federativa',
        labels={'sigla_uf_nome': 'Unidade Federativa', 'quantidade': 'Quantidade de Nascimentos'},
        color='quantidade',
        color_continuous_scale='viridis'
    )

    fig_uf.update_layout(
        xaxis_title='Quantidade de Nascimentos',
        yaxis_title='Unidade Federativa',
        template='plotly_white',
        margin=dict(l=100, r=20, t=50, b=50),
        yaxis=dict(categoryorder='total ascending'),
        coloraxis_showscale=False
    )

    fig_uf.update_traces(textposition='outside', texttemplate='%{text}')
    st.plotly_chart(fig_uf)


##############################################

    df.loc[~df["Pré-Natal de Alto Risco"].isin(
        ['Nenhuma consulta', 'de 1 a 3 consultas', 'de 4 a 6 consultas', '7 e mais consultas']), 
        "Pré-Natal de Alto Risco"
    ] = None 

    ordem_consultas = ['Nenhuma consulta', 'de 1 a 3 consultas', 'de 4 a 6 consultas', '7 e mais consultas']
    contagem = df.groupby(['Escolaridade da Mãe em 2010', 'Pré-Natal de Alto Risco']).size().unstack(fill_value=0)

    categorias_faltando = [categoria for categoria in ordem_consultas if categoria not in contagem.columns]
    for categoria in categorias_faltando:
        contagem[categoria] = 0

    contagem = contagem[ordem_consultas]

    porcentagem = contagem.div(contagem.sum(axis=1), axis=0) * 100
    porcentagem = porcentagem.reset_index().melt(
        id_vars='Escolaridade da Mãe em 2010', 
        var_name='Número de Pré-Natais', 
        value_name='Porcentagem'
    )

    fig_prenatal = px.line(
        porcentagem, 
        x='Número de Pré-Natais', 
        y='Porcentagem', 
        color='Escolaridade da Mãe em 2010', 
        markers=True,
        title='Percentual de Pré-Natais por Escolaridade'
    )

    fig_prenatal.update_layout(
        xaxis_title='Número de Pré-Natais Realizados',
        yaxis_title='Porcentagem de Ocorrências (%)',
        legend_title='Escolaridade',
        template='plotly_white',
    )
    st.plotly_chart(fig_prenatal)

##########################################333
with col2:
    st.subheader("")
    card1, card2 = st.columns(2)
    with card1:
        st.metric(label="Total de Nascimentos", value=f"{len(df):,}".replace(",", "."))
        media_idade_mãe = int(round(df['Idade da Mãe'].mean(), 0))
        st.metric(label="Idade Média da Mãe", value=media_idade_mãe)

    with card2:
        media_peso = df["Peso"].mean()
        media_peso_formatada = f"{media_peso:,.0f}".replace(",", "X").replace(",", ",").replace("X", ",")

        st.metric(label="Peso Médio do Bebê (Kg)", value=media_peso_formatada)
        media_idade_pai = int(round(df["Idade do Pai"].mean(), 0))
        st.metric(label="Idade Média do Pai", value=media_idade_pai)


    st.divider()

    col1_direita, col2_direita = st.columns(2)

    with col1_direita:
        contagem_sexo = df['Sexo'].value_counts().reset_index()
        contagem_sexo.columns = ['Sexo', 'Contagem']

        contagem_sexo['Contagem_formatada'] = contagem_sexo['Contagem'].apply(lambda x: f"{x:,}".replace(',', '.'))
        fig_pizza_sexo = px.pie(contagem_sexo, names="Sexo", values="Contagem_formatada", 
                                title="Nascimentos por Sexo",
                                color_discrete_sequence=["#87e6eb", "#ff9999"],
                                hover_data={'Sexo': True, 'Contagem': True},
                                labels={'Contagem_formatada': 'Ocorrências'})

        fig_pizza_sexo.update_traces(hovertemplate='%{label} = %{value}')
        fig_pizza_sexo.update_layout(width=300)
        st.plotly_chart(fig_pizza_sexo)
    
    with col2_direita:
        
        tipo_parto = df[df['Tipo de Parto'] != "Ignorado"]
        tipo_parto = df['Tipo de Parto'].value_counts().reset_index()
        tipo_parto.columns = ['Tipo de Parto', 'Contagem']

        tipo_parto['Contagem_formatada'] = tipo_parto['Contagem'].apply(lambda x: f"{x:,}".replace(',', '.'))
        fig_pizza_parto = px.pie(tipo_parto, names="Tipo de Parto", values="Contagem_formatada", 
                                title="Nascimentos por Tipo de Parto",
                                color_discrete_sequence=["#ffbb99", "#e1fcb6"],
                                hover_data={'Tipo de Parto': True, 'Contagem': True},
                                labels={'Contagem_formatada': 'Ocorrências'})

        fig_pizza_parto.update_traces(hovertemplate='%{label} = %{value}')
        fig_pizza_parto.update_layout(width=275)
        st.plotly_chart(fig_pizza_parto)

            
    contagem_estado_civil_mae = df['Estado Civil da Mãe'].value_counts()

    df_plotly = pd.DataFrame({
        'Estado Civil': contagem_estado_civil_mae.index,
        'Contagem': contagem_estado_civil_mae.values,
        'Porcentagem': (contagem_estado_civil_mae.values / contagem_estado_civil_mae.values.sum()) * 100
    })

    # Criando o treemap com plotly
    fig_treemap = px.treemap(df_plotly, 
                    path=['Estado Civil'], 
                    values='Contagem',
                    color='Estado Civil',
                    color_discrete_sequence=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#CCCCFF'],
                    title='Estado Civil da Mãe',
                    hover_data={'Contagem': True, 'Porcentagem': ':.1f'},
                    labels={'Contagem': 'Número de Ocorrências', 'Porcentagem': 'Porcentagem'})

    fig_treemap.update_traces(
        textinfo="label+value+percent parent",
        textfont=dict(size=18))
    fig_treemap.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        title_font=dict(size=20))

    fig_treemap.update_layout(
        annotations=[
            dict(
                text="Clique na área desejada para expandir a visualização",
                x=-0.043,
                y=1.05,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=15))])

    st.plotly_chart(fig_treemap)

