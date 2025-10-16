#!/bin/bash

echo "🏋️ GymRun Dashboard - Execução Direta"
echo "===================================="

# Instalar dependências no sistema (se necessário)
echo "📦 Verificando e instalando dependências..."

# 1) Tentar usar pip do sistema
PIP_CMD="python3 -m pip"
PYTHON_CMD="python3"

if ! $PIP_CMD --version >/dev/null 2>&1; then
    echo "🛠 Tentando instalar pip (ensurepip)..."
    python3 -m ensurepip --upgrade >/dev/null 2>&1 || true
fi

# 2) Se ainda não houver pip, criar um venv local como fallback
if ! $PIP_CMD --version >/dev/null 2>&1; then
    echo "📦 Criando ambiente virtual local (fallback)..."
    if python3 -m venv .qr-venv >/dev/null 2>&1; then
        # Ativar venv
        . ./.qr-venv/bin/activate
        PYTHON_CMD="python"
        PIP_CMD="python -m pip"
        # Bootstrap pip dentro do venv
        python -m ensurepip --upgrade >/dev/null 2>&1 || true
    else
        echo "❌ Não foi possível criar venv e 'pip' não está disponível."
        echo "   Instale com (Debian/Ubuntu): sudo apt-get install -y python3-pip python3-venv"
        echo "   Ou (Fedora): sudo dnf install -y python3-pip python3-virtualenv"
        echo "   Ou (Arch): sudo pacman -S python-pip python-virtualenv"
        exit 1
    fi
fi

# 3) Atualizar ferramentas base (silencioso)
$PIP_CMD install --upgrade pip setuptools wheel >/dev/null 2>&1 || true

# 4) Instalar dependências apenas se faltarem
$PYTHON_CMD -c "import streamlit" 2>/dev/null || $PIP_CMD install streamlit
$PYTHON_CMD -c "import pandas" 2>/dev/null || $PIP_CMD install pandas
$PYTHON_CMD -c "import plotly" 2>/dev/null || $PIP_CMD install plotly
$PYTHON_CMD -c "import numpy" 2>/dev/null || $PIP_CMD install numpy

# Preparar dados
if [ ! -f "GymRun16out25.csv" ] && [ ! -f "GymRun_16out25.csv" ] && [ ! -f "Exportação CSV.eml" ]; then
    if [ -f "GymRun Exportação CSV Modelo.eml" ]; then
        cp "GymRun Exportação CSV Modelo.eml" "GymRun16out25.csv"
        echo "📄 Usando dados de exemplo (copiado para GymRun16out25.csv)"
    fi
fi

echo "🚀 Iniciando dashboard..."
echo "📊 Acesse: http://localhost:8501"
echo ""

$PYTHON_CMD -m streamlit run app.py --server.port 8501
