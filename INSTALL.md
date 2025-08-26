# 💪 GymRun Dashboard - Instruções de Instalação

## Problema resolvido ✅

O erro que você estava enfrentando acontece porque:
1. Python 3.12 não inclui mais o módulo `distutils` por padrão
2. Algumas versões específicas do numpy conflitam com Python 3.12

## Solução - Execute passo a passo:

### Opção 1 - Script Automático (Recomendado):
```bash
./install_and_run.sh
```

### Opção 2 - Execução Rápida (sem ambiente virtual):
```bash
./quick_run.sh
```

### Opção 3 - Manual (se os scripts não funcionarem):

1. **Criar ambiente virtual:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Atualizar pip e instalar ferramentas base:**
```bash
python -m pip install --upgrade pip setuptools wheel
```

3. **Instalar dependências (versões flexíveis):**
```bash
pip install numpy
pip install pandas
pip install plotly
pip install streamlit
```

4. **Copiar dados de exemplo (se necessário):**
```bash
cp "GymRun Exportação CSV Modelo.eml" "Exportação CSV.eml"
```

5. **Executar dashboard:**
```bash
streamlit run app.py --server.port 8501
```

## Acesso:
- Dashboard: http://localhost:8501
- Para parar: Ctrl+C no terminal

## Scripts disponíveis:
- `install_and_run.sh` - Instalação completa com ambiente virtual
- `quick_run.sh` - Execução rápida no sistema
- `setup_and_run.sh` - Script original (pode ter problemas em Python 3.12)

## Dados:
O dashboard está configurado para usar automaticamente o arquivo de exemplo se você não tiver seus próprios dados do GymRun ainda.
