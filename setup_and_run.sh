#!/bin/bash

echo "🏋️ GymRun Dashboard - Setup e Execução"
echo "======================================"

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

# Verificar se estamos em um ambiente virtual, se não, criar um
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    
    # Ativar ambiente virtual
    source venv/bin/activate
    echo "✅ Ambiente virtual ativado"
else
    echo "✅ Usando ambiente virtual existente: $VIRTUAL_ENV"
fi

# Atualizar pip primeiro
echo "🔄 Atualizando pip..."
python3 -m pip install --upgrade pip

# Para Python 3.12+, instalar setuptools primeiro (resolve problema do distutils)
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ $(echo "$python_version >= 3.12" | bc -l) -eq 1 ]]; then
    echo "🔧 Python $python_version detectado. Instalando setuptools..."
    pip3 install setuptools
fi

# Instalar dependências com versões mais flexíveis
echo "📦 Instalando dependências..."

# Instalar numpy primeiro (pode resolver conflitos de dependência)
echo "📦 Instalando numpy..."
pip3 install "numpy>=1.21.0"

# Instalar pandas
echo "📦 Instalando pandas..."
pip3 install "pandas>=2.0.0"

# Instalar plotly
echo "📦 Instalando plotly..."
pip3 install "plotly>=5.0.0"

# Instalar streamlit
echo "📦 Instalando streamlit..."
pip3 install "streamlit>=1.30.0"

echo "✅ Todas as dependências foram instaladas"

# Verificar se o streamlit foi instalado e funciona
echo "🔍 Verificando instalação do Streamlit..."
if python3 -c "import streamlit" 2>/dev/null; then
    echo "✅ Streamlit instalado e funcionando"
    STREAMLIT_CMD="python3 -m streamlit"
else
    echo "❌ Erro na instalação do Streamlit"
    exit 1
fi

# Verificar se o arquivo de dados existe
if [ ! -f "Exportação CSV.eml" ]; then
    echo "⚠️  Arquivo 'Exportação CSV.eml' não encontrado!"
    echo "Por favor, coloque seu arquivo de exportação do GymRun na pasta atual."
    echo ""
    echo "Como alternativa, você pode testar com os dados de exemplo do arquivo 'GymRun Exportação CSV Modelo.eml'"
    
    if [ -f "GymRun Exportação CSV Modelo.eml" ]; then
        echo "🔄 Usando arquivo de exemplo para demonstração..."
        cp "GymRun Exportação CSV Modelo.eml" "Exportação CSV.eml"
        echo "✅ Arquivo de exemplo copiado"
    else
        echo "❌ Nenhum arquivo de dados encontrado!"
        exit 1
    fi
fi

echo "✅ Arquivo de dados encontrado"

# Executar a aplicação
echo ""
echo "🚀 Iniciando dashboard..."
echo "📊 Acesse: http://localhost:8501"
echo "⏹️  Para parar o servidor, pressione Ctrl+C"
echo ""

$STREAMLIT_CMD run app.py --server.port 8501 --server.address 0.0.0.0