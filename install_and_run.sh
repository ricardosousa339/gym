#!/bin/bash

echo "🏋️ GymRun Dashboard - Instalação Robusta"
echo "========================================"

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor, instale o Python3."
    exit 1
fi

# Verificar se o pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Por favor, instale o pip3."
    exit 1
fi

echo "✅ Python3 e pip3 encontrados"

# Criar e ativar ambiente virtual
if [ -d "venv" ]; then
    echo "📁 Removendo ambiente virtual antigo..."
    rm -rf venv
fi

echo "📦 Criando novo ambiente virtual..."
python3 -m venv venv

echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️ Atualizando pip..."
python3 -m pip install --upgrade pip

# Instalar setuptools primeiro (para Python 3.12+)
echo "🔧 Instalando setuptools..."
pip3 install setuptools

# Instalar dependências uma por uma
echo "📦 Instalando dependências..."

echo "  📈 Instalando numpy..."
pip3 install numpy

echo "  📊 Instalando pandas..."
pip3 install pandas

echo "  📉 Instalando plotly..."
pip3 install plotly

echo "  🌐 Instalando streamlit..."
pip3 install streamlit

echo "✅ Todas as dependências instaladas com sucesso!"

# Verificar se o arquivo de dados existe
if [ ! -f "Exportação CSV.eml" ]; then
    if [ -f "GymRun Exportação CSV Modelo.eml" ]; then
        echo "📄 Copiando arquivo de exemplo..."
        cp "GymRun Exportação CSV Modelo.eml" "Exportação CSV.eml"
        echo "✅ Arquivo de exemplo copiado"
    else
        echo "⚠️ Nenhum arquivo de dados encontrado!"
        echo "Coloque o arquivo 'Exportação CSV.eml' na pasta atual"
        exit 1
    fi
fi

echo "✅ Arquivo de dados encontrado"

echo ""
echo "🎉 Configuração completa!"
echo "🚀 Iniciando o dashboard..."
echo ""
echo "📊 Dashboard disponível em: http://localhost:8501"
echo "🛑 Para parar: Ctrl+C"
echo ""

# Executar usando python3 explicitamente
python3 -m streamlit run app.py --server.port 8501