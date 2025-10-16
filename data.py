import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    """Carrega os dados do arquivo CSV.

    Ordem de busca do arquivo (primeiro que existir):
    - GymRun16out25.csv (novo padrão)
    - GymRun_16out25.csv (variação comum)
    - Exportação CSV.eml (legado)
    """
    candidates = [
        "GymRun16out25.csv",
        "GymRun_16out25.csv",
        "Exportação CSV.eml",
    ]
    file_path = next((p for p in candidates if os.path.exists(p)), None)

    if not file_path:
        expected = ", ".join(candidates)
        st.error(f"Nenhum arquivo de dados encontrado. Coloque um dos arquivos: {expected} na pasta do projeto.")
        return pd.DataFrame()
    
    try:
        # Lendo o arquivo CSV com separador ponto e vírgula (locale PT)
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

def calculate_volume(df):
    """Calcula o volume de treino (Weight x Reps)"""
    df['Volume'] = df['Weight'] * df['Reps']
    return df

def calculate_1rm(weight, reps):
    """Calcula 1RM usando a fórmula de Epley"""
    if pd.isna(weight) or pd.isna(reps) or reps == 0:
        return None
    return weight * (1 + reps / 30.0)

def calculate_trend(df, column, periods=5):
    """Calcula a tendência usando média móvel"""
    return df[column].rolling(window=periods, min_periods=1).mean()
