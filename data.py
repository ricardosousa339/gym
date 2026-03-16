import streamlit as st
import pandas as pd
import os

def _process_dataframe(df):
    """Auxiliar para aplicar a mesma conversão de tipos em DataFrames lidos."""
    try:
        df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
        df['DateTime'] = pd.to_datetime(df['Date'].dt.strftime('%Y-%m-%d') + ' ' + df['Time'])
        numeric_columns = ['Weight', 'Reps', 'Duration', 'Distance']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro ao formatar ou processar dados: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_data():
    """Carrega os dados do arquivo CSV local.

    Busca por (nesta ordem):
    - GymRun16out25.csv (novo padrão)
    - GymRun_16out25.csv (este é onde os uploads são salvos)
    - Exportação CSV.eml (legado)
    """
    candidates = [
        "GymRun16out25.csv",
        "GymRun_16out25.csv",
        "Exportação CSV.eml",
    ]
    file_path = next((p for p in candidates if os.path.exists(p)), None)

    if not file_path:
        return pd.DataFrame()
    
    try:
        # Lendo o arquivo CSV com separador ponto e vírgula (locale PT)
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
    except Exception as e:
        st.error(f"Erro ao carregar arquivo local: {str(e)}")
        return pd.DataFrame()
    
    return _process_dataframe(df)

@st.cache_data
def read_uploaded_file(uploaded_file):
    """Lê temporariamente um arquivo upado como DataFrame sem salvá-lo."""
    try:
        # Pular pro início do buffer caso tenha sido lido antes
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
        return _process_dataframe(df)
    except Exception as e:
        st.error(f"Erro ao ler arquivo recebido: {str(e)}")
        return pd.DataFrame()

def merge_datasets(old_df, new_df):
    """
    Combina dois DataFrames e remove as linhas exatas duplicadas,
    focando em manter o histórico original.
    """
    if old_df.empty:
        return new_df
    if new_df.empty:
        return old_df
        
    combined = pd.concat([old_df, new_df], ignore_index=True)
    
    # Colunas lógicas que definem o mesmo registro específico de treino
    subset = ['Date', 'Time', 'Exercise', 'Set', 'Weight', 'Reps']
    # Mantém os disponíveis neste conjunto de dados
    valid_subset = [c for c in subset if c in combined.columns]
    
    combined = combined.drop_duplicates(subset=valid_subset, keep='last')
    combined = combined.sort_values(by=['Date', 'Time']).reset_index(drop=True)
    
    return combined

def save_dataset(df, file_path="GymRun_16out25.csv"):
    """
    Salva o DataFrame formatado de volta ao formato CSV original que a tela aceita
    """
    df_save = df.copy()
    if 'DateTime' in df_save.columns:
        df_save = df_save.drop(columns=['DateTime'])
        
    if pd.api.types.is_datetime64_any_dtype(df_save['Date']):
        df_save['Date'] = df_save['Date'].dt.strftime('%d.%m.%Y')
        
    df_save.to_csv(file_path, sep=';', index=False, encoding='utf-8')

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
