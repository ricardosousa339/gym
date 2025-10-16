# 💪 GymRun Dashboard

Dashboard interativo para análise de dados de treino da academia usando dados exportados do GymRun.

## 🚀 Como usar

### 1. Instalação das dependências
```bash
pip install -r requirements.txt
```

### 2. Executar a aplicação
```bash
streamlit run app.py
```

Ou use um dos scripts:
```bash
./quick_run.sh         # execução direta
./install_and_run.sh   # cria venv e instala
./setup_and_run.sh     # alternativa com checagens
```

### 3. Acesse no navegador
Abra: http://localhost:8501

## 📊 Funcionalidades

- **Métricas Gerais**: Total de treinos, exercícios únicos, séries e volume médio
- **Evolução do Volume**: Gráfico temporal do volume de treino
- **Progresso por Exercício**: Análise detalhada de peso máximo e 1RM estimado
- **Análise de Frequência**: Treinos por dia da semana e top exercícios
- **Heatmap de Atividade**: Visualização da consistência de treinos
- **Filtros Avançados**: Por data, rotina e exercício

## 📁 Estrutura de Dados

O dashboard espera um arquivo `GymRun16out25.csv` (separado por `;`) com as seguintes colunas:
- Date (formato: DD.MM.YYYY)
- Time (formato: HH:MM:SS)
- Routine
- Exercise
- Set
- Weight
- Reps
- Duration
- Distance
- Note

## 🛠️ Tecnologias

- **Streamlit**: Interface web interativa
- **Plotly**: Gráficos interativos
- **Pandas**: Manipulação de dados
- **NumPy**: Cálculos numéricos
