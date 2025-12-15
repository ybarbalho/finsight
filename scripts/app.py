import streamlit as st
import pandas as pd
import plotly.express as px

# Importando os dados
data = pd.read_csv(
    './datasets/transactions.csv', index_col='transaction_id')

data['transaction_time'] = pd.to_datetime(data['transaction_time'], utc=True)

# Criando uma coluna de montadoras para observação.
print(data.head())

st.title('Finsight: análise para identificação de fraudes em transações digitais')

st.header('Visualização dos dados')

# Filtragem dos dados por meio do preço dos automóveis.
filter_view = st.slider('Filtrar o valor da compra:', 0.0,
                        data['amount'].max(), (500.0, 5000.0))

data_filtered = data[(data['amount'] >= filter_view[0]) &
                     (data['amount'] <= filter_view[1])]

show_fraud = st.checkbox('Mostrar apenas fraudes')

# Checa se a fraude foi selecionada e filtra.
if show_fraud:
    data_filtered = data_filtered[data_filtered['is_fraud'] == 1]

st.subheader('Filtragem por países')

# Dicionário com as bandeiras dos países.
flags = {
    'FR': '🇫🇷',
    'US': '🇺🇸',
    'TR': '🇹🇷',
    'PL': '🇵🇱',
    'ES': '🇪🇸',
    'IT': '🇮🇹',
    'RO': '🇷🇴',
    'GB': '🇬🇧',
    'NL': '🇳🇱',
    'DE': '🇩🇪'
}

# Isolando os valores únicos de país.
unique_countries = sorted(data['country'].unique())

cols = st.columns(4)  # Número de colunas.
selected_countries = []

for i, country in enumerate(unique_countries):
    col = cols[i % 4]  # Distribui as checkboxes entre as colunas.

    label = f"{flags.get(country)} {country}"  # Bandeira + nome do país.

    if col.checkbox(label, value=True, key=country):
        selected_countries.append(country)

# Filtra os dados pelos países selecionados.
data_filtered = data_filtered[data_filtered['country'].isin(
    selected_countries)]

# Informações sobre os VALORES TOTAIS DE COMPRAS.

cols = st.columns(2)

cols[0].subheader('Compras fraudulentas ($)')
cols[0].header("$ " + (data_filtered[data_filtered['is_fraud']
               == 1]['amount'].sum().round(2)).astype(str))

# Oculta o montante total caso fraude esteja ativado.
if not show_fraud:
    cols[1].subheader('Total de compras ($)')
    cols[1].header("$ " + (data_filtered['amount'].sum().round(2).astype(str)))

# Exibe o CONJUNTO DE DADOS completo.
st.subheader('Exibição do conjunto de dados')
st.write(data_filtered)

# Cria uma coluna de início de cada semana.
data_filtered['week'] = data_filtered['transaction_time'].dt.to_period(
    'W').dt.start_time

# GRÁFICO DE DISPERSÃO para observação dos dados do VALOR DAS COMPRAS por país.

st.subheader('Distribuição do montante de compras por país')

fig = px.scatter(data_filtered.sort_values(by='country'), x='country', y='amount', labels={
    'country': 'País de origem', 'amount': 'Valor da compra'}, color='is_fraud')

st.plotly_chart(fig, width='stretch')

# SÉRIE TEMPORAL para observação dos dados de IDADE DE CRIAÇÃO DA CONTA por semana.

st.subheader('Países com menor aplicação de AVS no ato da compra')

avs_check = data_filtered.groupby('country')[
    'avs_match'].mean().reset_index()

st.write(avs_check.sort_values(by='avs_match', ascending=False).tail())

# SÉRIE TEMPORAL para observação dos dados de DISTÂNCIA DE ENTREGA por semana.

data_ship_distance = data_filtered.groupby('week')[
    'shipping_distance_km'].mean().reset_index()

# último registro contém informações incompletas e será removido.
data_ship_distance.drop(data_ship_distance.index[-1], axis=0, inplace=True)

st.subheader('Distância média para os destinos de entrega')

fig = px.line(data_ship_distance, x='week',
              y='shipping_distance_km', labels={'week': 'Semana do ano', 'shipping_distance_km': 'Distância média do frete'})
st.plotly_chart(fig, width='stretch')

# SÉRIE TEMPORAL para observação dos dados de IDADE DE CRIAÇÃO DA CONTA por semana.

data_account_days = data_filtered.groupby('week')[
    'account_age_days'].median().reset_index()

st.subheader('Mediana da idade de criação das contas')

fig = px.line(data_account_days, x='week',
              y='account_age_days', labels={'week': 'Semana do ano', 'account_age_days': 'Dias desde a criação da conta'})
st.plotly_chart(fig, width='stretch')
