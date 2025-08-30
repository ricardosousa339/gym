import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_comparison_chart(df, exercise1, exercise2):
    """Cria gráfico de comparação entre dois exercícios"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f'{exercise1} - Evolução do Peso', f'{exercise2} - Evolução do Peso'),
        vertical_spacing=0.1
    )
    
    for i, exercise in enumerate([exercise1, exercise2], 1):
        exercise_data = df[df['Exercise'] == exercise].copy()
        if not exercise_data.empty:
            daily_max = exercise_data.groupby('Date')['Weight'].max().reset_index()
            
            fig.add_trace(
                go.Scatter(
                    x=daily_max['Date'],
                    y=daily_max['Weight'],
                    mode='lines+markers',
                    name=exercise,
                    line=dict(width=2)
                ),
                row=i, col=1
            )
    
    fig.update_layout(height=600, showlegend=True)
    fig.update_xaxes(title_text="Data", row=2, col=1)
    fig.update_yaxes(title_text="Peso Máximo (kg)", row=1, col=1)
    fig.update_yaxes(title_text="Peso Máximo (kg)", row=2, col=1)
    return fig
