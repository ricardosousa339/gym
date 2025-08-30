# Refatoração do GymRun Dashboard

## Resumo da Modularização

O código monolítico `app.py` foi refatorado e dividido em módulos especializados, mantendo todas as funcionalidades originais intactas.

## Estrutura dos Módulos

### 1. `data.py` - Manipulação de Dados
- `load_data()` - Carrega dados do CSV com cache
- `calculate_volume()` - Calcula volume de treino (Weight × Reps)
- `calculate_1rm()` - Calcula 1RM usando fórmula de Epley
- `calculate_trend()` - Calcula tendência com média móvel

### 2. `forecasting.py` - Análise Preditiva
- `forecast_1rm_series()` - Previsão de 1RM semanal (ARIMA + fallback linear)
- `detect_plateau()` - Detecção de platôs na evolução

### 3. `mappings.py` - Mapeamentos e Utilitários
- `map_exercise_to_group()` - Mapeia exercícios para grupos musculares
- `alias_name()` - Cria aliases curtos para exercícios
- `get_group_emoji()` / `get_exercise_emoji()` - Emojis para UI
- `get_group_icon_path()` / `get_exercise_icon_path()` - Caminhos de ícones

### 4. `charts.py` - Visualizações
- `create_comparison_chart()` - Gráficos de comparação entre exercícios

### 5. `metrics.py` - Cálculos e Alertas
- `calculate_basic_metrics()` - Métricas básicas da visão geral
- `calculate_exercise_stats()` - Estatísticas por exercício para atalhos
- `generate_alerts()` - Sistema de alertas automáticos

### 6. `app.py` - Interface Principal (Refatorado)
- Interface Streamlit principal
- Importa e usa as funções dos módulos especializados
- Mantém toda a lógica de UI e navegação

## Benefícios da Modularização

✅ **Separação de Responsabilidades**: Cada módulo tem um propósito específico
✅ **Facilidade de Manutenção**: Mudanças em funcionalidades específicas ficam isoladas
✅ **Reutilização**: Funções podem ser importadas em outros projetos
✅ **Testabilidade**: Cada módulo pode ser testado independentemente
✅ **Legibilidade**: Código mais organizado e fácil de entender
✅ **Compatibilidade**: Mantém 100% das funcionalidades originais

## Como Executar

O comando para executar permanece o mesmo:
```bash
streamlit run app.py
```

## Estrutura de Arquivos

```
gym/
├── app.py              # Interface principal (refatorado)
├── data.py             # Manipulação de dados
├── forecasting.py      # Análises preditivas
├── mappings.py         # Mapeamentos e utilitários
├── charts.py           # Visualizações
├── metrics.py          # Métricas e alertas
├── requirements.txt    # Dependências
└── Exportação CSV.eml  # Dados de entrada
```

Todas as funcionalidades originais foram preservadas:
- Dashboard com visão geral e exploração de exercícios
- Cálculo de volume, 1RM e tendências
- Previsões com ARIMA/regressão linear
- Sistema de alertas para platôs
- Comparação entre exercícios
- Interface com atalhos e filtros
- Mapeamento automático de grupos musculares
