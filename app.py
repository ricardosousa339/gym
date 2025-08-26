import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os

# Configuração da página
st.set_page_config(
    page_title="GymRun Dashboard",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar dados
@st.cache_data
def load_data():
    """Carrega os dados do arquivo CSV"""
    file_path = "Exportação CSV.eml"
    
    if not os.path.exists(file_path):
        st.error(f"Arquivo {file_path} não encontrado!")
        return pd.DataFrame()
    
    try:
        # Lendo o arquivo CSV com separador ponto e vírgula
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        
        # Convertendo a coluna Date para datetime
        df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
        
        # Criando coluna de data e hora combinada
        df['DateTime'] = pd.to_datetime(df['Date'].dt.strftime('%Y-%m-%d') + ' ' + df['Time'])
        
        # Convertendo colunas numéricas
        numeric_columns = ['Weight', 'Reps', 'Duration', 'Distance']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# Função para calcular volume de treino
def calculate_volume(df):
    """Calcula o volume de treino (Weight x Reps)"""
    df['Volume'] = df['Weight'] * df['Reps']
    return df

# Função para calcular 1RM estimado
def calculate_1rm(weight, reps):
    """Calcula 1RM usando a fórmula de Epley"""
    if pd.isna(weight) or pd.isna(reps) or reps == 0:
        return None
    return weight * (1 + reps / 30.0)

# Função para análise de tendência
def calculate_trend(df, column, periods=5):
    """Calcula a tendência usando média móvel"""
    return df[column].rolling(window=periods, min_periods=1).mean()

def create_comparison_chart(df, exercise1, exercise2):
    """Cria gráfico de comparação entre dois exercícios"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f'{exercise1} - Evolução do Peso', f'{exercise2} - Evolução do Peso'),
        vertical_spacing=0.1
    )
    
    for i, exercise in enumerate([exercise1, exercise2], 1):
        exercise_data = df[df['Exercise'] == exercise].copy()
        if not exercise_data.empty:
            daily_max = exercise_data.groupby('Date')['Weight'].max().reset_index()
            
            fig.add_trace(
                go.Scatter(
                    x=daily_max['Date'],
                    y=daily_max['Weight'],
                    mode='lines+markers',
                    name=exercise,
                    line=dict(width=2)
                ),
                row=i, col=1
            )
    
    fig.update_layout(height=600, showlegend=True)
    fig.update_xaxes(title_text="Data", row=2, col=1)
    fig.update_yaxes(title_text="Peso Máximo (kg)", row=1, col=1)
    fig.update_yaxes(title_text="Peso Máximo (kg)", row=2, col=1)
    return fig

def main():
    st.title("💪 GymRun Dashboard - Análise de Progresso na Academia")
    st.markdown("### 📊 Acompanhe sua evolução nos treinos de forma simples e visual")
    st.markdown("---")
    
    # Explicação do Volume
    with st.expander("❓ O que é Volume de Treino?"):
        st.markdown("""
        **Volume = Peso levantado × Número de repetições**
        
        **Exemplos:**
        - Supino: 80kg × 12 repetições = **960kg de volume**
        - Leg Press: 100kg × 15 repetições = **1.500kg de volume**
        - Rosca: 15kg × 10 repetições = **150kg de volume**
        
        **Por que é importante?**
        - 📈 Mostra o total de "trabalho" realizado
        - 🎯 Ajuda a acompanhar o progresso
        - 📊 Permite comparar diferentes treinos
        """)
    
    # Carregando dados
    df = load_data()
    
    if df.empty:
        st.warning("Nenhum dado encontrado. Certifique-se de que o arquivo 'Exportação CSV.eml' está na mesma pasta.")
        return
    
    # Calculando volume
    df = calculate_volume(df)
    
    # Calculando 1RM estimado para exercícios com peso
    df['Estimated_1RM'] = df.apply(lambda row: calculate_1rm(row['Weight'], row['Reps']), axis=1)
    
    # Sidebar para filtros
    st.sidebar.header("🔍 Filtrar Dados")
    st.sidebar.markdown("Use os filtros abaixo para analisar períodos ou exercícios específicos:")
    
    # Filtro de data
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    start_date = st.sidebar.date_input(
        "📅 Data Inicial",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    end_date = st.sidebar.date_input(
        "📅 Data Final",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtro por rotina
    routines = ['Todas as Rotinas'] + sorted(df['Routine'].unique().tolist())
    selected_routine = st.sidebar.selectbox("🏋️ Tipo de Treino", routines)
    
    # Filtro por exercício
    exercises = ['Todos os Exercícios'] + sorted(df['Exercise'].unique().tolist())
    selected_exercise = st.sidebar.selectbox("💪 Exercício Específico", exercises)
    
    # Aplicando filtros
    filtered_df = df[
        (df['Date'] >= pd.to_datetime(start_date)) &
        (df['Date'] <= pd.to_datetime(end_date))
    ]
    
    if selected_routine != 'Todas as Rotinas':
        filtered_df = filtered_df[filtered_df['Routine'] == selected_routine]
    
    if selected_exercise != 'Todos os Exercícios':
        filtered_df = filtered_df[filtered_df['Exercise'] == selected_exercise]
    
    # Tabs para organizar o conteúdo
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Resumo Geral", 
        "📈 Meu Progresso", 
        "🏋️ Comparar Exercícios", 
        "📅 Padrões de Treino", 
        "📋 Dados Completos"
    ])
    
    with tab1:
        # Métricas principais
        st.header("📊 Resumo dos Seus Treinos")
        st.markdown("*Veja um panorama geral do seu desempenho na academia*")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_workouts = filtered_df['Date'].nunique()
            st.metric("🗓️ Dias de Treino", total_workouts)
        
        with col2:
            total_exercises = filtered_df['Exercise'].nunique()
            st.metric("💪 Exercícios Diferentes", total_exercises)
        
        with col3:
            total_sets = len(filtered_df)
            st.metric("🔢 Séries Realizadas", total_sets)
        
        with col4:
            avg_volume = filtered_df['Volume'].mean() if not filtered_df['Volume'].isna().all() else 0
            st.metric("⚖️ Volume Médio por Série", f"{avg_volume:.0f} kg")
            st.caption("Peso × Repetições")
        
        # Volume por treino ao longo do tempo
        st.header("📈 Como Está Evoluindo o Seu Volume de Treino")
        st.markdown("*Volume = peso levantado × repetições (quanto mais alto, mais trabalho você fez)*")
        
        daily_volume = filtered_df.groupby('Date')['Volume'].sum().reset_index()
        daily_volume['Trend'] = calculate_trend(daily_volume, 'Volume')
        
        fig_volume = go.Figure()
        
        fig_volume.add_trace(
            go.Scatter(
                x=daily_volume['Date'],
                y=daily_volume['Volume'],
                mode='lines+markers',
                name='Volume do Dia',
                line=dict(color='lightblue', width=1),
                marker=dict(size=4)
            )
        )
        
        fig_volume.add_trace(
            go.Scatter(
                x=daily_volume['Date'],
                y=daily_volume['Trend'],
                mode='lines',
                name='Tendência (5 dias)',
                line=dict(color='red', width=3)
            )
        )
        
        fig_volume.update_layout(
            title="Volume Total por Dia de Treino",
            xaxis_title="Data do Treino",
            yaxis_title="Volume Total (kg)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)
        
        # Top exercícios por volume
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Exercícios que Mais Trabalham")
            st.markdown("*Ranking por volume total acumulado*")
            
            top_exercises = filtered_df.groupby('Exercise')['Volume'].sum().sort_values(ascending=False).head(10)
            
            fig_top = px.bar(
                x=top_exercises.values,
                y=top_exercises.index,
                orientation='h',
                title="Top 10 Exercícios por Volume Acumulado",
                labels={'x': 'Volume Total (kg)', 'y': 'Exercício'}
            )
            st.plotly_chart(fig_top, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Distribuição dos Tipos de Treino")
            st.markdown("*Como você divide seus treinos*")
            
            routine_counts = filtered_df['Routine'].value_counts()
            
            fig_routines = px.pie(
                values=routine_counts.values,
                names=routine_counts.index,
                title="Proporção de Cada Tipo de Treino"
            )
            st.plotly_chart(fig_routines, use_container_width=True)
    
    with tab2:
        # Progresso por exercício
        st.header("🏋️ Acompanhe Seu Progresso em Detalhes")
        st.markdown("*Escolha um exercício para ver como você está evoluindo*")
        
        exercise_for_analysis = st.selectbox(
            "🎯 Selecione um exercício para análise detalhada:",
            options=sorted(filtered_df['Exercise'].unique()),
            key="exercise_analysis"
        )
        
        exercise_data = filtered_df[filtered_df['Exercise'] == exercise_for_analysis].copy()
        
        if not exercise_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Evolução do Peso Máximo")
                st.markdown("*Peso mais alto levantado em cada treino*")
                
                # Gráfico de peso máximo por treino
                max_weight_by_date = exercise_data.groupby('Date')['Weight'].max().reset_index()
                max_weight_by_date['Trend'] = calculate_trend(max_weight_by_date, 'Weight')
                
                fig_weight = go.Figure()
                
                fig_weight.add_trace(
                    go.Scatter(
                        x=max_weight_by_date['Date'],
                        y=max_weight_by_date['Weight'],
                        mode='lines+markers',
                        name='Peso Máximo do Dia',
                        line=dict(color='blue', width=2),
                        marker=dict(size=6)
                    )
                )
                
                fig_weight.add_trace(
                    go.Scatter(
                        x=max_weight_by_date['Date'],
                        y=max_weight_by_date['Trend'],
                        mode='lines',
                        name='Tendência de Progresso',
                        line=dict(color='red', width=3, dash='dash')
                    )
                )
                
                fig_weight.update_layout(
                    title=f"Peso Máximo - {exercise_for_analysis}",
                    xaxis_title="Data",
                    yaxis_title="Peso Máximo (kg)"
                )
                st.plotly_chart(fig_weight, use_container_width=True)
            
            with col2:
                st.subheader("💪 Força Máxima Estimada (1RM)")
                st.markdown("*Estimativa do peso que você conseguiria levantar 1 vez*")
                
                # Gráfico de 1RM estimado
                if not exercise_data['Estimated_1RM'].isna().all():
                    max_1rm_by_date = exercise_data.groupby('Date')['Estimated_1RM'].max().reset_index()
                    max_1rm_by_date['Trend'] = calculate_trend(max_1rm_by_date, 'Estimated_1RM')
                    
                    fig_1rm = go.Figure()
                    
                    fig_1rm.add_trace(
                        go.Scatter(
                            x=max_1rm_by_date['Date'],
                            y=max_1rm_by_date['Estimated_1RM'],
                            mode='lines+markers',
                            name='1RM Estimado',
                            line=dict(color='green', width=2),
                            marker=dict(size=6)
                        )
                    )
                    
                    fig_1rm.add_trace(
                        go.Scatter(
                            x=max_1rm_by_date['Date'],
                            y=max_1rm_by_date['Trend'],
                            mode='lines',
                            name='Tendência de Força',
                            line=dict(color='red', width=3, dash='dash')
                        )
                    )
                    
                    fig_1rm.update_layout(
                        title=f"Força Máxima Estimada - {exercise_for_analysis}",
                        xaxis_title="Data",
                        yaxis_title="1RM Estimado (kg)"
                    )
                    st.plotly_chart(fig_1rm, use_container_width=True)
            
            # Análise detalhada das séries
            st.subheader(f"📋 Histórico Completo - {exercise_for_analysis}")
            st.markdown("*Todas as suas séries registradas para este exercício*")
            
            series_data = exercise_data[['Date', 'Set', 'Weight', 'Reps', 'Volume']].copy()
            series_data['Date'] = series_data['Date'].dt.strftime('%d/%m/%Y')
            series_data = series_data.sort_values(['Date', 'Set'], ascending=[False, True])
            series_data.columns = ['Data', 'Série', 'Peso (kg)', 'Repetições', 'Volume (kg)']
            
            st.dataframe(series_data, use_container_width=True)
    
    with tab3:
        st.header("🏋️ Compare Dois Exercícios")
        st.markdown("*Veja lado a lado como você está progredindo em exercícios diferentes*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            exercise1 = st.selectbox(
                "🥇 Primeiro exercício:",
                options=sorted(filtered_df['Exercise'].unique()),
                key="comp_ex1"
            )
        
        with col2:
            exercise2 = st.selectbox(
                "🥈 Segundo exercício:",
                options=sorted(filtered_df['Exercise'].unique()),
                key="comp_ex2"
            )
        
        if exercise1 != exercise2:
            comparison_chart = create_comparison_chart(filtered_df, exercise1, exercise2)
            st.plotly_chart(comparison_chart, use_container_width=True)
            
            # Métricas de comparação
            st.subheader("📊 Comparação Detalhada")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### 🥇 {exercise1}")
                ex1_data = filtered_df[filtered_df['Exercise'] == exercise1]
                if not ex1_data.empty:
                    st.metric("Peso Máximo Atingido", f"{ex1_data['Weight'].max():.1f} kg")
                    st.metric("Força Máxima Estimada", f"{ex1_data['Estimated_1RM'].max():.1f} kg")
                    st.metric("Volume Total Acumulado", f"{ex1_data['Volume'].sum():.0f} kg")
                    st.metric("Séries Realizadas", len(ex1_data))
            
            with col2:
                st.markdown(f"### 🥈 {exercise2}")
                ex2_data = filtered_df[filtered_df['Exercise'] == exercise2]
                if not ex2_data.empty:
                    st.metric("Peso Máximo Atingido", f"{ex2_data['Weight'].max():.1f} kg")
                    st.metric("Força Máxima Estimada", f"{ex2_data['Estimated_1RM'].max():.1f} kg")
                    st.metric("Volume Total Acumulado", f"{ex2_data['Volume'].sum():.0f} kg")
                    st.metric("Séries Realizadas", len(ex2_data))
    
    with tab4:
        # Análise de frequência de treino
        st.header("📅 Seus Padrões de Treino")
        st.markdown("*Descubra quando e como você treina melhor*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Frequência por Dia da Semana")
            st.markdown("*Em quais dias você mais treina?*")
            
            # Frequência por dia da semana
            filtered_df['DayOfWeek'] = filtered_df['Date'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_names_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            
            workout_frequency = filtered_df.groupby('DayOfWeek')['Date'].nunique().reset_index()
            workout_frequency['DayOfWeek'] = workout_frequency['DayOfWeek'].map(dict(zip(day_order, day_names_pt)))
            workout_frequency = workout_frequency[workout_frequency['DayOfWeek'].isin(day_names_pt)]
            
            fig_freq = px.bar(
                workout_frequency,
                x='DayOfWeek',
                y='Date',
                title="Dias da Semana que Mais Treino",
                category_orders={"DayOfWeek": day_names_pt},
                labels={'Date': 'Número de Treinos', 'DayOfWeek': 'Dia da Semana'}
            )
            st.plotly_chart(fig_freq, use_container_width=True)
        
        with col2:
            st.subheader("📈 Volume Mensal")
            st.markdown("*Como seu volume varia mês a mês?*")
            
            # Volume por mês
            filtered_df['Month'] = filtered_df['Date'].dt.to_period('M')
            monthly_volume = filtered_df.groupby('Month')['Volume'].sum().reset_index()
            monthly_volume['Month'] = monthly_volume['Month'].astype(str)
            
            fig_monthly = px.line(
                monthly_volume,
                x='Month',
                y='Volume',
                title="Volume Total por Mês",
                markers=True,
                labels={'Volume': 'Volume Total (kg)', 'Month': 'Mês'}
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Heatmap de atividade
        st.header("🔥 Mapa de Calor da Sua Atividade")
        st.markdown("*Visualize sua consistência de treino - cores mais intensas = mais volume*")
        
        # Preparando dados para o heatmap
        heatmap_data = filtered_df.groupby(['Date'])['Volume'].sum().reset_index()
        heatmap_data['Year'] = heatmap_data['Date'].dt.year
        heatmap_data['Month'] = heatmap_data['Date'].dt.month
        heatmap_data['Day'] = heatmap_data['Date'].dt.day
        
        if not heatmap_data.empty:
            # Criando matriz para heatmap
            pivot_table = heatmap_data.pivot_table(
                values='Volume', 
                index='Month', 
                columns='Day', 
                aggfunc='sum',
                fill_value=0
            )
            
            fig_heatmap = px.imshow(
                pivot_table,
                title="Heatmap: Volume de Treino por Mês e Dia",
                labels=dict(x="Dia do Mês", y="Mês", color="Volume (kg)"),
                aspect="auto",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab5:
        # Tabela de dados recentes
        st.header("📋 Todos os Seus Dados de Treino")
        st.markdown("*Visualize e baixe seus dados completos*")
        
        # Controles para a tabela
        col1, col2 = st.columns(2)
        
        with col1:
            show_records = st.selectbox(
                "📊 Quantos registros mostrar:",
                options=[20, 50, 100, 200, "Todos"],
                index=0
            )
        
        with col2:
            sort_by = st.selectbox(
                "📈 Ordenar por:",
                options=['Data (Mais Recente)', 'Data (Mais Antiga)', 'Volume (Maior)', 'Peso (Maior)'],
                index=0
            )
        
        # Preparando dados para exibição
        display_df = filtered_df.copy()
        
        if sort_by == 'Data (Mais Recente)':
            display_df = display_df.sort_values('DateTime', ascending=False)
        elif sort_by == 'Data (Mais Antiga)':
            display_df = display_df.sort_values('DateTime', ascending=True)
        elif sort_by == 'Volume (Maior)':
            display_df = display_df.sort_values('Volume', ascending=False)
        elif sort_by == 'Peso (Maior)':
            display_df = display_df.sort_values('Weight', ascending=False)
        
        if show_records != "Todos":
            display_df = display_df.head(int(show_records))
        
        # Selecionando colunas para exibição
        columns_to_show = ['Date', 'Time', 'Routine', 'Exercise', 'Set', 'Weight', 'Reps', 'Volume', 'Estimated_1RM']
        table_data = display_df[columns_to_show].copy()
        table_data['Date'] = table_data['Date'].dt.strftime('%d/%m/%Y')
        
        # Renomeando colunas para português
        table_data.columns = ['Data', 'Hora', 'Tipo de Treino', 'Exercício', 'Série', 'Peso (kg)', 'Repetições', 'Volume (kg)', '1RM Estimado (kg)']
        
        # Formatando valores numéricos
        numeric_cols = ['Peso (kg)', 'Volume (kg)', '1RM Estimado (kg)']
        for col in numeric_cols:
            if col in table_data.columns:
                table_data[col] = table_data[col].round(1)
        
        st.dataframe(table_data, use_container_width=True, height=600)
        
        # Opção para download
        if st.button("📥 Baixar Dados Filtrados (CSV)"):
            csv = table_data.to_csv(index=False, sep=';')
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"meus_treinos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
