#!/bin/bash

echo "🏋️ GymRun Dashboard - Execução Direta"
echo "===================================="

# Instalar dependências no sistema (se necessário)
echo "📦 Verificando e instalando dependências..."

python3 -c "import streamlit" 2>/dev/null || pip3 install streamlit
python3 -c "import pandas" 2>/dev/null || pip3 install pandas
python3 -c "import plotly" 2>/dev/null || pip3 install plotly  
python3 -c "import numpy" 2>/dev/null || pip3 install numpy

# Preparar dados
if [ ! -f "Exportação CSV.eml" ] && [ -f "GymRun Exportação CSV Modelo.eml" ]; then
    cp "GymRun Exportação CSV Modelo.eml" "Exportação CSV.eml"
    echo "📄 Usando dados de exemplo"
fi

echo "🚀 Iniciando dashboard..."
echo "📊 Acesse: http://localhost:8501"
echo ""

python3 -m streamlit run app.py --server.port 8501
