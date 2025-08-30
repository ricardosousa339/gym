import pandas as pd
import numpy as np

def generate_alerts(exercise_df, filtered_df, exercise_name):
    """Gera alertas para um exercício específico"""
    alerts = []
    
    # Import local da função detect_plateau
    from forecasting import detect_plateau
    
    # Platô em 1RM semanal
    m1 = exercise_df.groupby('Date')['Estimated_1RM'].max().sort_index()
    if not m1.empty:
        plateau = detect_plateau(m1.resample('W').max().dropna())
        if plateau:
            alerts.append("Possível platô em 1RM. Considere deload, trocar variação ou ajustar volume/intensidade.")
    
    # Queda de volume nas últimas semanas
    volw = exercise_df.groupby('Date')['Volume'].sum().resample('W').sum()
    if len(volw.dropna()) >= 4:
        recent = volw.iloc[-2:].mean()
        prev = volw.iloc[-4:-2].mean()
        if prev > 0 and recent < 0.8 * prev:
            alerts.append("Volume recente caiu >20% vs. semanas anteriores. Verifique recuperação/sono/estresse.")
    
    return alerts

def calculate_basic_metrics(filtered_df):
    """Calcula métricas básicas do treino"""
    return {
        'dias_treino': int(filtered_df['Date'].nunique()),
        'exercicios_diferentes': int(filtered_df['Exercise'].nunique()),
        'series_total': int(len(filtered_df)),
        'volume_medio': 0 if filtered_df.empty or filtered_df['Volume'].isna().all() else filtered_df['Volume'].mean()
    }

def calculate_exercise_stats(filtered_df):
    """Calcula estatísticas por exercício para os atalhos"""
    return filtered_df.groupby(['Exercise', 'MuscleGroup']).agg(
        Sessoes=('Date', 'nunique'),
        Volume=('Volume', 'sum'),
        OneRM=('Estimated_1RM', 'max')
    ).reset_index()
