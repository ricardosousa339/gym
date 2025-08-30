import pandas as pd
import numpy as np

def forecast_1rm_series(series: pd.Series, periods_weeks: int = 6):
    """Recebe uma série temporal (index datetime, valores 1RM) e retorna DataFrame com previsões semanais."""
    s = series.dropna().sort_index()
    if s.empty or len(s) < 5:
        return None
    # Reamostrar para semanal (máximo 1RM na semana)
    sw = s.resample('W').max().dropna()
    if len(sw) < 5:
        return None
    try:
        import importlib
        pm = importlib.import_module('pmdarima')
        model = pm.auto_arima(sw, seasonal=False, error_action='ignore', suppress_warnings=True)
        fc, conf = model.predict(n_periods=periods_weeks, return_conf_int=True)
        future_idx = pd.date_range(sw.index[-1] + pd.Timedelta(weeks=1), periods=periods_weeks, freq='W')
        out = pd.DataFrame({'Date': future_idx, 'Forecast': fc, 'Lower': conf[:, 0], 'Upper': conf[:, 1]})
        return out
    except Exception:
        # Fallback: Regressão linear no tempo
        x = np.arange(len(sw))
        y = sw.values
        coef = np.polyfit(x, y, deg=1)  # y = a*x + b
        a, b = coef[0], coef[1]
        x_future = np.arange(len(sw), len(sw) + periods_weeks)
        fc = a * x_future + b
        future_idx = pd.date_range(sw.index[-1] + pd.Timedelta(weeks=1), periods=periods_weeks, freq='W')
        out = pd.DataFrame({'Date': future_idx, 'Forecast': fc})
        out['Lower'] = out['Forecast'] - np.std(y)
        out['Upper'] = out['Forecast'] + np.std(y)
        return out

def detect_plateau(series: pd.Series, lookback_points: int = 8, slope_thresh: float = 0.01):
    """Detecção simples de platô (inclinação ~0 nas últimas semanas)"""
    s = series.dropna().sort_index()
    if len(s) < max(5, lookback_points):
        return False
    tail = s.iloc[-lookback_points:]
    x = np.arange(len(tail))
    y = tail.values
    a, _b = np.polyfit(x, y, deg=1)
    # Normalizar pelo nível médio para threshold relativo
    if np.mean(y) > 0:
        rel_slope = a / np.mean(y)
    else:
        rel_slope = a
    return abs(rel_slope) < slope_thresh
