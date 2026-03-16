import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
 

# Importar módulos locais
from data import load_data, read_uploaded_file, merge_datasets, save_dataset, calculate_volume, calculate_1rm, calculate_trend
from forecasting import forecast_1rm_series
from mappings import (
    map_exercise_to_group, alias_name
)
from charts import create_comparison_chart
from metrics import generate_alerts, calculate_basic_metrics, calculate_exercise_stats

# Configuração da página
st.set_page_config(
    page_title="GymRun Dashboard",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("💪 GymRun Dashboard - Análise de Progresso na Academia")
    st.markdown("### 📊 Visualização simples e direta do seu treino")
    st.markdown("---")

    # Explicação do Volume
    with st.expander("❓ O que é Volume de Treino?"):
        st.markdown(
            """
            **Volume = Peso levantado × Número de repetições**\n\n
            Exemplos:\n
            - Supino: 80kg × 12 repetições = 960kg de volume\n
            - Leg Press: 100kg × 15 repetições = 1.500kg de volume\n
            - Rosca: 15kg × 10 repetições = 150kg de volume
            """
        )
    # Carrega dados locais (base consolidada)
    df_local = load_data()

    # Upload de dados pela Sidebar logo no início
    st.sidebar.header("📂 Importação de Dados")
    uploaded_file = st.sidebar.file_uploader(
        "Upload da Exportação (.csv, .eml)", 
        type=['csv', 'eml'], 
        help="Faça o upload do backup exportado do GymRun para atualizar os dados permanentemente."
    )
    
    if uploaded_file is not None and uploaded_file.name != st.session_state.get('last_uploaded_file'):
        try:
            new_df = read_uploaded_file(uploaded_file)
            if not new_df.empty:
                old_exercises = set(df_local['Exercise'].dropna().unique()) if not df_local.empty else set()
                new_exercises = set(new_df['Exercise'].dropna().unique())
                
                # Apenas exercícios que surgiram no novo dataset que não existiam no local
                diff_exercises = sorted(list(new_exercises - old_exercises)) if old_exercises else []
                
                if diff_exercises:
                    st.sidebar.warning("Novos exercícios detectados. Veja a área principal.")
                    st.warning("⚠️ **Novos exercícios encontrados!** A sua base importada tem exercícios que não existem no histórico atual.")
                    with st.expander("📝 Mapear Novos Nomes (Resolver para Continuar)", expanded=True):
                        st.markdown("Se você renomeou algum exercício no GymRun, escolha o nome antigo abaixo para não dividir seu histórico em dois gráficos separados. Se for um exercício totalmente novo, basta deixar na opção padrão.")
                        
                        user_mappings = {}
                        opts = ['(Manter como Novo)'] + sorted(list(old_exercises))
                        
                        for new_ex in diff_exercises:
                            ans = st.selectbox(f"Mesclar '{new_ex}' com:", options=opts, key=f"map_{new_ex}")
                            if ans != '(Manter como Novo)':
                                user_mappings[new_ex] = ans
                                
                        if st.button("Confirmar e Mesclar 🚀"):
                            if user_mappings:
                                new_df['Exercise'] = new_df['Exercise'].replace(user_mappings)
                                
                            combined_df = merge_datasets(df_local, new_df)
                            save_dataset(combined_df, "gymrun_database.csv")
                            
                            st.session_state['last_uploaded_file'] = uploaded_file.name
                            st.cache_data.clear()
                            st.rerun()
                            
                    # Interrompe o fluxo normal enquanto o usuário não resolver o mapeamento
                    return
                else:
                    # Fluxo normal, mescla direto se não há exercícios desconhecidos
                    combined_df = merge_datasets(df_local, new_df)
                    save_dataset(combined_df, "gymrun_database.csv")
                    
                    st.session_state['last_uploaded_file'] = uploaded_file.name
                    st.cache_data.clear()
                    st.sidebar.success("✅ Histórico mesclado com sucesso!")
                    st.rerun()
        except Exception as e:
            st.sidebar.error(f"Erro ao processar arquivo: {e}")
            
    st.sidebar.divider()
    
    # Reset de Dados
    st.sidebar.header("⚠️ Reset de Dados")
    with st.sidebar.expander("Apagar Histórico"):
        st.warning("Esta ação apagará todos os treinos registrados no sistema atualmente.")
        if st.button("🗑️ Zerar Base de Dados", use_container_width=True, type="primary"):
            empty_df = pd.DataFrame(columns=['Date', 'Time', 'Exercise', 'Set', 'Weight', 'Reps', 'Duration', 'Distance'])
            # Usar o save_dataset para garantir o mesmo padrão UTF-8 e separador de sempre
            save_dataset(empty_df, "gymrun_database.csv")
            
            st.session_state['last_uploaded_file'] = None
            st.cache_data.clear()
            st.rerun()

    st.sidebar.divider()

    # Define o df geral a ser usado se não fomos interrompidos pelo mapeamento
    df = df_local
    
    if df.empty:
        st.warning("Nenhum dado encontrado. Faça o upload do arquivo de exportação (CSV ou EML) do GymRun no menu lateral ou certifique-se de que há um arquivo padrão na pasta.")
        return

    # Métricas básicas
    df = calculate_volume(df)
    df['Estimated_1RM'] = df.apply(lambda row: calculate_1rm(row['Weight'], row['Reps']), axis=1)
    df['MuscleGroup'] = df['Exercise'].astype(str).apply(map_exercise_to_group)

    # Sidebar – filtros e navegação simplificada
    st.sidebar.header("Navegação")
    page = st.sidebar.radio("Ir para:", ["Visão Geral", "Exercícios"], index=0)

    st.sidebar.header("Filtros")
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date = st.sidebar.date_input("📅 Data Inicial", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("📅 Data Final", value=max_date, min_value=min_date, max_value=max_date)

    routines = ['Todas'] + sorted(df['Routine'].dropna().unique().tolist())
    selected_routine = st.sidebar.selectbox("🏋️ Rotina", routines)

    # Aplica filtros globais
    filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))].copy()
    if selected_routine != 'Todas':
        filtered_df = filtered_df[filtered_df['Routine'] == selected_routine]

    # Página 1: Visão Geral
    if page == "Visão Geral":
        # Calcular métricas básicas
        basic_metrics = calculate_basic_metrics(filtered_df)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🗓️ Dias de Treino", basic_metrics['dias_treino'])
        with col2:
            st.metric("💪 Exercícios Diferentes", basic_metrics['exercicios_diferentes'])
        with col3:
            st.metric("🔢 Séries", basic_metrics['series_total'])
        with col4:
            st.metric("⚖️ Volume Médio/Série", f"{basic_metrics['volume_medio']:.0f} kg")

        st.subheader("📈 Evolução do Volume")
        daily_volume = filtered_df.groupby('Date')['Volume'].sum().reset_index()
        daily_volume['Trend'] = calculate_trend(daily_volume, 'Volume')
        fig_v = go.Figure()
        fig_v.add_trace(go.Scatter(x=daily_volume['Date'], y=daily_volume['Volume'], mode='lines+markers', name='Volume'))
        fig_v.add_trace(go.Scatter(x=daily_volume['Date'], y=daily_volume['Trend'], mode='lines', name='Tendência', line=dict(color='red')))
        fig_v.update_layout(xaxis_title='Data', yaxis_title='Volume (kg)')
        st.plotly_chart(fig_v, use_container_width=True)

        colA, colB = st.columns(2)
        with colA:
            st.subheader("🏆 Top Exercícios por Volume")
            topx = filtered_df.groupby('Exercise')['Volume'].sum().sort_values(ascending=False).head(10)
            st.plotly_chart(px.bar(x=topx.values, y=topx.index, orientation='h', labels={'x':'Volume (kg)', 'y':'Exercício'}), use_container_width=True)
        with colB:
            st.subheader("🎯 Rotinas")
            rc = filtered_df['Routine'].value_counts()
            if not rc.empty:
                st.plotly_chart(px.pie(values=rc.values, names=rc.index), use_container_width=True)
            else:
                st.info("Sem dados de rotina para o período.")

        st.subheader("🔥 Consistência (Mapa de Calor)")
        cal = filtered_df.groupby('Date')['Volume'].sum().reset_index()
        if not cal.empty:
            # Converter Period para string para evitar erro de serialização no Plotly/Streamlit
            cal['Month'] = cal['Date'].dt.to_period('M').astype(str)
            cal['Day'] = cal['Date'].dt.day
            pivot = cal.pivot_table(values='Volume', index='Month', columns='Day', aggfunc='sum', fill_value=0)
            st.plotly_chart(px.imshow(pivot, aspect='auto', labels=dict(x='Dia', y='Mês', color='Volume')), use_container_width=True)
        else:
            st.info("Sem treinos no período selecionado.")

    # Página 2: Explorar Exercícios
    else:
        st.subheader("🔎 Explorar e Analisar Exercícios")
        left, right = st.columns([1, 2])

        with left:
            st.markdown("#### Selecione o Exercício")
            
            # Filtro opcional de grupo muscular para facilitar a busca
            group_options = ['Todos'] + sorted(filtered_df['MuscleGroup'].dropna().unique().tolist())
            sel_grp = st.selectbox("Filtrar por Grupo (opcional)", options=group_options, index=0)

            base = filtered_df if sel_grp == 'Todos' else filtered_df[filtered_df['MuscleGroup'] == sel_grp]
            ex_opts = sorted(base['Exercise'].dropna().unique().tolist())

            if not ex_opts:
                st.info("Nenhum exercício encontrado.")
                return

            # Selectbox já possui busca embutida no Streamlit, simplificando imensamente a UX
            selected_ex = st.selectbox("Exercício Principal", options=ex_opts, index=0)
            
            compare = st.checkbox("Comparar com outro exercício")
            selected_ex2 = None
            if compare:
                other_list = [e for e in ex_opts if e != selected_ex]
                if other_list:
                    selected_ex2 = st.selectbox("Segundo exercício", options=other_list, index=0)
                else:
                    st.info("Não há outro exercício aplicável para comparar.")
        with right:
            # Análise do exercício principal
            ex_df = filtered_df[filtered_df['Exercise'] == selected_ex]
            if ex_df.empty:
                st.info("Sem dados para o exercício selecionado no período.")
            else:
                # Resumo no topo
                c1, c2, c3 = st.columns(3)
                with c1:
                    max_weight = ex_df['Weight'].max()
                    max_w_str = f"{max_weight:.1f} kg" if not pd.isna(max_weight) else "0.0 kg"
                    st.metric("Peso Máx.", max_w_str)
                with c2:
                    max_1rm = ex_df['Estimated_1RM'].max()
                    max_1rm_str = f"{max_1rm:.1f} kg" if not pd.isna(max_1rm) else "0.0 kg"
                    st.metric("1RM Est. Máx.", max_1rm_str)
                with c3:
                    st.metric("Volume Total", f"{ex_df['Volume'].sum():.0f} kg")

                # Abas de análise
                tabs = st.tabs(["Peso", "1RM", "Volume", "Previsão 1RM", "Tabela", "Alertas"]) 

                # Peso
                with tabs[0]:
                    mx = ex_df.groupby('Date')['Weight'].max().reset_index()
                    mx['Trend'] = calculate_trend(mx, 'Weight')
                    fig_w = go.Figure()
                    fig_w.add_trace(go.Scatter(x=mx['Date'], y=mx['Weight'], mode='lines+markers', name='Peso Máx.'))
                    fig_w.add_trace(go.Scatter(x=mx['Date'], y=mx['Trend'], mode='lines', name='Tendência', line=dict(color='red', dash='dash')))
                    fig_w.update_layout(title=f"Peso Máximo — {selected_ex}")
                    st.plotly_chart(fig_w, use_container_width=True)

                # 1RM
                with tabs[1]:
                    if not ex_df['Estimated_1RM'].isna().all():
                        m1 = ex_df.groupby('Date')['Estimated_1RM'].max().reset_index()
                        m1['Trend'] = calculate_trend(m1, 'Estimated_1RM')
                        fig_1 = go.Figure()
                        fig_1.add_trace(go.Scatter(x=m1['Date'], y=m1['Estimated_1RM'], mode='lines+markers', name='1RM Est.'))
                        fig_1.add_trace(go.Scatter(x=m1['Date'], y=m1['Trend'], mode='lines', name='Tendência', line=dict(color='red', dash='dash')))
                        fig_1.update_layout(title=f"1RM Estimado — {selected_ex}")
                        st.plotly_chart(fig_1, use_container_width=True)
                    else:
                        st.info("Sem dados suficientes para 1RM.")

                # Volume
                with tabs[2]:
                    vol = ex_df.groupby('Date')['Volume'].sum().reset_index()
                    vol['Trend'] = calculate_trend(vol, 'Volume')
                    fig_v2 = go.Figure()
                    fig_v2.add_trace(go.Bar(x=vol['Date'], y=vol['Volume'], name='Volume'))
                    fig_v2.add_trace(go.Scatter(x=vol['Date'], y=vol['Trend'], name='Tendência', mode='lines', line=dict(color='red')))
                    fig_v2.update_layout(title=f"Volume — {selected_ex}")
                    st.plotly_chart(fig_v2, use_container_width=True)

                # Previsão 1RM
                with tabs[3]:
                    m1 = ex_df.groupby('Date')['Estimated_1RM'].max().sort_index()
                    if not m1.empty:
                        m1.index = pd.to_datetime(m1.index)
                        fc = forecast_1rm_series(m1)
                        if fc is not None:
                            hist_weekly = m1.resample('W').max().dropna().reset_index()
                            fig_fc = go.Figure()
                            fig_fc.add_trace(go.Scatter(x=hist_weekly['Date'], y=hist_weekly['Estimated_1RM'], mode='lines+markers', name='Hist Semanal'))
                            fig_fc.add_trace(go.Scatter(x=fc['Date'], y=fc['Forecast'], mode='lines+markers', name='Previsão', line=dict(color='green')))
                            if 'Lower' in fc.columns and 'Upper' in fc.columns:
                                fig_fc.add_trace(go.Scatter(x=pd.concat([fc['Date'], fc['Date'][::-1]]),
                                                            y=pd.concat([fc['Upper'], fc['Lower'][::-1]]),
                                                            fill='toself',
                                                            fillcolor='rgba(0,128,0,0.15)',
                                                            line=dict(color='rgba(0,0,0,0)'),
                                                            name='IC'))
                            fig_fc.update_layout(title=f"Previsão Semanal de 1RM — {selected_ex}")
                            st.plotly_chart(fig_fc, use_container_width=True)
                        else:
                            st.info("Dados insuficientes para prever 1RM (necessário histórico semanal).")
                    else:
                        st.info("Sem dados de 1RM para prever.")

                # Tabela
                with tabs[4]:
                    sd = ex_df[['Date', 'Set', 'Weight', 'Reps', 'Volume']].copy()
                    sd['Date'] = sd['Date'].dt.strftime('%d/%m/%Y')
                    sd = sd.sort_values(['Date', 'Set'], ascending=[False, True])
                    sd.columns = ['Data', 'Série', 'Peso (kg)', 'Repetições', 'Volume (kg)']
                    st.dataframe(sd, use_container_width=True, height=350)

                # Alertas
                with tabs[5]:
                    alerts = generate_alerts(ex_df, filtered_df, selected_ex)
                    if alerts:
                        for a in alerts:
                            st.warning(a)
                    else:
                        st.success("Sem alertas no momento.")

                # Comparação lado a lado
                if selected_ex2:
                    st.markdown("---")
                    st.subheader("Comparação")
                    comp_fig = create_comparison_chart(filtered_df, selected_ex, selected_ex2)
                    st.plotly_chart(comp_fig, use_container_width=True)

                    colm1, colm2 = st.columns(2)
                    with colm1:
                        d1 = filtered_df[filtered_df['Exercise'] == selected_ex]
                        st.metric("Peso Máx.", f"{d1['Weight'].max():.1f} kg")
                        st.metric("1RM Est. Máx.", f"{d1['Estimated_1RM'].max():.1f} kg")
                        st.metric("Volume Total", f"{d1['Volume'].sum():.0f} kg")
                    with colm2:
                        d2 = filtered_df[filtered_df['Exercise'] == selected_ex2]
                        st.metric("Peso Máx.", f"{d2['Weight'].max():.1f} kg")
                        st.metric("1RM Est. Máx.", f"{d2['Estimated_1RM'].max():.1f} kg")
                        st.metric("Volume Total", f"{d2['Volume'].sum():.0f} kg")

if __name__ == "__main__":
    main()
