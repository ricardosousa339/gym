#!/bin/bash

echo "🏋️ GymRun Dashboard - Execução Simples"
echo "====================================="

# Limpar cache do pip
echo "🧹 Limpando cache..."
pip3 cache purge 2>/dev/null || true

# Remover ambiente virtual anterior se existir
if [ -d "venv" ]; then
    echo "🗑️ Removendo ambiente virtual anterior..."
    rm -rf venv
fi

# Criar novo ambiente virtual
echo "📦 Criando novo ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate
echo "✅ Ambiente virtual ativado"

# Atualizar pip e instalar setuptools
echo "🔧 Atualizando pip e instalando ferramentas base..."
python3 -m pip install --upgrade pip setuptools wheel

# Instalar dependências uma por uma
echo "📦 Instalando numpy..."
pip3 install numpy

echo "📦 Instalando pandas..."
pip3 install pandas

echo "📦 Instalando plotly..."
pip3 install plotly

echo "📦 Instalando streamlit..."
pip3 install streamlit

# Verificar se o arquivo de dados existe (ordem de preferência)
if [ -f "GymRun16out25.csv" ] || [ -f "GymRun_16out25.csv" ] || [ -f "Exportação CSV.eml" ]; then
    :
else
    if [ -f "GymRun Exportação CSV Modelo.eml" ]; then
        echo "📄 Usando dados de exemplo..."
        cp "GymRun Exportação CSV Modelo.eml" "GymRun16out25.csv"
    else
        echo "❌ Nenhum arquivo de dados encontrado!"
        exit 1
    fi
fi

echo "✅ Tudo pronto!"
echo ""
echo "🚀 Iniciando dashboard..."
echo "📊 Acesse: http://localhost:8501"
echo ""

python3 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
