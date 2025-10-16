# GymRun Dashboard — Copilot Instructions

These notes make AI coding agents productive in this repo quickly. Keep guidance specific to this project’s patterns and workflows.

## Big picture
- Python + Streamlit app for analyzing GymRun exports. Primary entrypoint: `app.py` (two pages: "Visão Geral" and "Exercícios").
- Data is loaded from a local semicolon-separated CSV file named `GymRun16out25.csv` (Portuguese locale). Backward compatible with `GymRun_16out25.csv` and legacy `Exportação CSV.eml`.
- Architecture is modular:
  - `data.py`: `load_data()` (cached), `calculate_volume()`, `calculate_1rm()` (Epley), `calculate_trend()` (rolling mean)
  - `metrics.py`: `calculate_basic_metrics()`, `calculate_exercise_stats()`, `generate_alerts()`
  - `forecasting.py`: `forecast_1rm_series()` (uses optional `pmdarima` via importlib, then falls back to linear regression), `detect_plateau()`
  - `mappings.py`: `map_exercise_to_group()`, `alias_name()`, emoji/icon helpers with graceful fallbacks
  - `charts.py`: `create_comparison_chart()`

## Run workflows
- Quick run (no venv): `./quick_run.sh`
- Full setup (venv + install): `./install_and_run.sh` or `./setup_and_run.sh`
- Manual: `pip install -r requirements.txt` then `streamlit run app.py --server.port 8501`
- Access: http://localhost:8501. Scripts auto-copy sample `GymRun Exportação CSV Modelo.eml` to `GymRun16out25.csv` if none of the expected files are present.

## Data expectations and flow
- Expected columns: `Date (DD.MM.YYYY)`, `Time (HH:MM:SS)`, `Routine`, `Exercise`, `Set`, `Weight`, `Reps`, `Duration`, `Distance`, `Note`.
- `load_data()` reads with `sep=';'`, coerces numeric cols, creates `DateTime`, caches via `@st.cache_data`. If file missing/parse error, returns empty DataFrame and surface message in UI.
- In `app.py`: after load, compute `Volume` and `Estimated_1RM`, map `MuscleGroup`, then global filters (date range, routine) feed charts/metrics.

## Conventions and patterns (project-specific)
- UI text, variable names, and labels are in Portuguese; keep new labels consistent (e.g., "Visão Geral", "Exercícios").
- Keep the input filename `GymRun16out25.csv` and semicolon separator unless you also update `load_data()` and docs. The loader accepts `GymRun_16out25.csv` and legacy `Exportação CSV.eml` as fallbacks.
- Don’t hard-require extra dependencies in forecasting. Maintain try/except import for `pmdarima` with linear-regression fallback.
- Charts are Plotly-based, commonly using `graph_objects`; trends via `calculate_trend()`; weekly aggregates use `.resample('W')`.
- Exercise display uses short labels via `alias_name()`; selection persistence via `st.session_state['exercise_primary'|'exercise_secondary']`.
- Heatmap uses `Period` to string conversion to avoid Plotly/Streamlit serialization issues—preserve this pattern.

## Extending the app (copy these patterns)
- New metric on "Visão Geral": add to `metrics.calculate_basic_metrics()` and display using `st.metric(...)` in `app.py`.
- New exercise mapping: extend keyword lists in `mappings.map_exercise_to_group()`; prefer broad, lowercase Portuguese keywords.
- New analysis tab for an exercise: follow the tab pattern in `app.py` (group by `Date`, compute trend, plot with GO traces). Use existing column names.
- Forecasting tweaks: improve `forecast_1rm_series()` but preserve optional dependency and returned DataFrame shape: `Date`, `Forecast`, optional `Lower`/`Upper`.
- Comparison features: reuse `charts.create_comparison_chart()` signature: `(df, exercise1, exercise2)`.

## Gotchas and debugging
- No data shown? Ensure `GymRun16out25.csv` exists and is correctly formatted (semicolon-separated). Scripts will copy the sample automatically if no expected file is found.
- Python 3.12: use the provided scripts—they install `setuptools` first and avoid `distutils` issues. Requirements are minimal and flexible.
- If charts error on dates, verify `Date` is `datetime64` and `Period` values are converted to strings before plotting.
- Cache: `@st.cache_data` may keep stale data; instruct users to rerun/clear cache in Streamlit if needed after changing the file.

## File reference
- Entrypoint: `app.py`
- Modules: `data.py`, `metrics.py`, `forecasting.py`, `mappings.py`, `charts.py`
- Scripts: `install_and_run.sh`, `quick_run.sh`, `setup_and_run.sh`, `run_simple.sh`
- Docs: `README.md`, `INSTALL.md`, `REFACTORING_SUMMARY.md`
