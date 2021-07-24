# ## Análise de Dados do Brasileirão de pontos corridos

# ### Organização e tratamento dos dados

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

st.set_option('deprecation.showPyplotGlobalUse', False)

dados = pd.read_csv('campeonato-brasileiro.csv', sep=";")
dados_classificacao = pd.read_csv('classificacao.csv', sep=';')

#Limpeza de Dados
dados.drop(["Dia", "Horário", "Arena", 
            "Estado Mandante", "Estado Visitante", "Estado Vencedor"],
            axis = 1, inplace = True)

#Renomeando as colunas
dados.rename(columns={'Mandante Placar': 'MP', 
                      'Visitante Placar': 'VP'}, inplace = True)

#Filtrando os campeonatos apenas dos pontos corridos até 2020
dados['Data'] = pd.to_datetime(dados['Data'])
dados['Ano'] = dados['Data'].dt.year
dados.query("Data > '2003-01-01'", inplace = True)
dados.drop('Data', axis = 1, inplace = True)

#Padronizando os nomes dos times e tratando dados
dados['Visitante'] = dados['Visitante'].str.lower().str.title()
dados['Mandante'] = dados['Mandante'].str.lower().str.title()
dados['Vencedor'] = dados['Vencedor'].str.lower().str.title()
dados.replace('-','Empate', inplace = True)
dados.Ano = dados.Ano.replace({2021: 2020})
dados = dados.astype({'ID': int, 'MP': int, 'VP': int, 'Ano': int})
dados.ID = range(1, dados.shape[0] + 1)

st.title('Visualização dos dados sobre a campanha do Brasileirao do Flamengo')

time = 'Flamengo'
colors = ['red', 'black']

st.markdown('## Total de Gols Marcados')

mandante = dados.query(f"Mandante == '{time}'")
gols_mandante = mandante.groupby('Ano')['MP'].sum()
gols_mandante = pd.DataFrame(gols_mandante)

#Gols marcados como visitante em cada edição
visitante = dados.query(f"Visitante == '{time}'")
gols_visitante = visitante.groupby('Ano')['VP'].sum()
gols_visitante = pd.DataFrame(gols_visitante)

#Total de gols marcados com stacked = True
gols_totais = pd.concat([gols_mandante, gols_visitante], axis = 1)
gols_totais_plot = gols_totais.plot.bar(stacked = True, 
                                   color={'MP': colors[0], 'VP': colors[1]},
                                   figsize = (9, 3))

gols_totais_plot.legend(['Gols Feitos em Casa', 'Gols Feitos Fora'])
st.pyplot()


# ### Total de Gols Sofridos ###

st.markdown('## Total de Gols Sofridos')
#Gols sofridos como mandante em cada edição
gols_sofridos_mandante = mandante.groupby('Ano')['VP'].sum()
gols_sofridos_mandante = pd.DataFrame(gols_sofridos_mandante)

#Gols sofridos como visitante em cada edição
gols_sofridos_visitante = visitante.groupby('Ano')['MP'].sum()
gols_sofridos_visitante = pd.DataFrame(gols_sofridos_visitante)

#Total de gols sofridos com stacked = True
gols_totais_sofridos = pd.concat([gols_sofridos_mandante, 
                                  gols_sofridos_visitante], axis = 1)

gols_totais_sofridos_plot = gols_totais_sofridos.plot.bar(stacked=True, 
                                      color={'MP': colors[0], 'VP': colors[1]},
                                      figsize = (9, 3))

gols_totais_sofridos_plot.legend(['Gols Sofridos Casa', 'Gols Sofridos Fora'])
st.pyplot()


# ### Média de Gols Marcados por Ano

st.markdown('## Média de Gols Marcados por ano')
#Média de gols marcados por ano
dados_time = dados.query(f'Mandante == "{time}" or Visitante == "{time}"')
rodadas = pd.DataFrame(dados_time.groupby('Ano')['Ano'].count())
rodadas.rename({'Ano': 'Jogos'}, axis=1, inplace=True)

gols_totais['Total'] = gols_totais.MP + gols_totais.VP
gols_totais['Media'] = gols_totais.Total / rodadas.Jogos

gols_totais = gols_totais.plot.bar(y='Media', color = colors[0], figsize = (9, 3))
gols_totais.set_ylim(0, 3)
st.pyplot()

# ### Média de Gols sofridos por Ano

st.markdown('## Media de gols sofridos por ano')
#Média de gols sofridos por ano
gols_totais_sofridos['Total'] = gols_totais_sofridos.MP + gols_totais_sofridos.VP
gols_totais_sofridos['Media'] = gols_totais_sofridos.Total / rodadas.Jogos
gols_totais_sofridos = gols_totais_sofridos.plot.bar(y='Media', color = colors[1], figsize = (9, 3))
gols_totais_sofridos.set_ylim(0, 3)
st.pyplot()

# ### Distribuição dos resultados em casa

st.markdown('## Distribuiçao de resultados em casa')
vitorias_casa = mandante.groupby('Ano')['Vencedor'].apply(lambda x: (x==f'{time}').sum()).reset_index(name='Vitórias')

empates_casa = mandante.groupby('Ano')['Vencedor'].apply(lambda x: (x=='Empate').sum()).reset_index(name='Empates')

resultado_casa = rodadas.merge(vitorias_casa, how='left', on='Ano')
resultado_casa = resultado_casa.merge(empates_casa, how='left', on='Ano')

resultado_casa.Jogos = resultado_casa.Jogos // 2
resultado_casa['Derrotas'] = resultado_casa['Jogos'] - resultado_casa['Vitórias'] - resultado_casa['Empates']

resultado_casa.plot.bar(stacked=True, x = 'Ano', 
                        y = ['Vitórias', 'Empates', 'Derrotas'], 
                        color = {'Vitórias': colors[0], 'Empates': 'lightgray', 'Derrotas': colors[1]}, 
                        figsize = (9, 3))
st.pyplot()


# ### Distribuição dos resultados fora de casa

st.markdown('## Distribuiçao de resultados fora de casa')
vitorias_fora = visitante.groupby('Ano')['Vencedor'].apply(lambda x: (x==f'{time}').sum()).reset_index(name='Vitórias')

empates_fora = visitante.groupby('Ano')['Vencedor'].apply(lambda x: (x=='Empate').sum()).reset_index(name='Empates')

resultado_fora = rodadas.merge(vitorias_fora, how='left', on='Ano')
resultado_fora = resultado_fora.merge(empates_fora, how='left', on='Ano')

resultado_fora.Jogos = resultado_fora.Jogos // 2
resultado_fora['Derrotas'] = resultado_fora['Jogos'] - resultado_fora['Vitórias'] - resultado_fora['Empates']

resultado_fora.plot.bar(stacked=True, x = 'Ano', 
                        y = ['Vitórias', 'Empates', 'Derrotas'], 
                        color = {'Vitórias': colors[0], 'Empates': 'lightgray', 'Derrotas': colors[1]}, 
                        figsize = (9, 3))
st.pyplot()


# ### Distribuição geral dos resultados
st.markdown('## Distribuição geral dos resultados')
resultado_total = resultado_fora + resultado_casa
resultado_total['Ano'] = resultado_fora.Ano
resultado_total.plot.bar(stacked=True, x = 'Ano', 
                        y = ['Vitórias', 'Empates', 'Derrotas'], 
                        color = {'Vitórias': colors[0], 'Empates': 'lightgray', 'Derrotas': colors[1]}, 
                        figsize = (9, 3))
st.pyplot()

# ### Evolução dos pontos ganhos

st.markdown('## Evolução dos pontos ganhos')
resultado_total['PG'] = (3 * resultado_total['Vitórias'] + 
     resultado_total['Empates'])
 
resultado_total.plot(x='Ano', y='PG', color=colors[0], 
                     xticks = range(2003, 2020, 2), grid = True, figsize = (9, 3))
st.pyplot()


# ### Distribuição dos pontos ganhos em casa e fora de casa

st.markdown('## Distribuição dos pontos ganhos em casa e fora de casa')
resultado_total['Aprov Casa']= 3 * resultado_casa['Vitórias'] + resultado_casa['Empates']
resultado_total['Aprov Fora']= 3 * resultado_fora['Vitórias'] + resultado_fora['Empates']

resultado_total.plot.bar(x='Ano', y=['Aprov Casa', 'Aprov Fora'], stacked = True, 
                         color = {'Aprov Casa':colors[0], 'Aprov Fora':colors[1]}, 
                         figsize = (9, 3))
st.pyplot()


# ### Times que mais venceram o seu clube
st.markdown('## Times que mais venceu o Flamengo')

adversarios_vit = dados_time.groupby('Vencedor')['Vencedor'].count()
adversarios_vit = pd.DataFrame(adversarios_vit)
adversarios_vit.columns = ['Vitórias']

adversarios_vit = adversarios_vit.query(f'index != "{time}" and index != "Empate"')
adversarios_vit.sort_values(by=['Vitórias'], inplace=True, ascending=False)

adversarios_vit.plot.barh(figsize = (5, 8), color = colors[0])
st.pyplot()

# ### Times que seu clube mais venceu

st.markdown('## Times que o Flamnego mais venceu')
perdedores = dados_time.copy()

condicoes = [(perdedores['Mandante'] == perdedores['Vencedor']), 
             (perdedores['Visitante'] == perdedores['Vencedor'])]
             
valores = [perdedores['Visitante'], perdedores['Mandante']]
perdedores['Perdedor'] = np.select(condicoes, valores, default='Empate')

time_vit = perdedores.groupby('Perdedor')['Perdedor'].count()
time_vit = pd.DataFrame(time_vit)
time_vit.columns = ['Vitórias']
time_vit.reset_index(level=0, inplace=True)

time_vit = time_vit.drop(time_vit[(time_vit['Perdedor'] == f'{time}')].index)
time_vit = time_vit.drop(time_vit[(time_vit['Perdedor'] == 'Empate')].index)

time_vit.sort_values(by=['Vitórias'], inplace=True, ascending=False)
time_vit.plot.barh(x = 'Perdedor', y = 'Vitórias', figsize = (5, 9),
                  color = colors[1])
st.pyplot()
