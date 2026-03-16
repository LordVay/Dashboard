import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Model.train_model_crypto import Models  # your Models class file

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Price Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0b0e14;
    color: #e2e8f0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f1420;
    border-right: 1px solid #1e2535;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #111827 0%, #0f1824 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 10px;
}
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    color: #4a90d9;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 24px;
    font-weight: 700;
    color: #e2e8f0;
}
.metric-sub {
    font-size: 12px;
    color: #64748b;
    margin-top: 3px;
}

/* Section header */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #4a90d9;
    margin: 28px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2535;
}

/* Title */
.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #e2e8f0;
    margin-bottom: 2px;
}
.main-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: #4a6fa5;
    margin-bottom: 28px;
}

/* Horizon badge */
.horizon-badge {
    display: inline-block;
    background: #1e3a5f;
    color: #7ab3e0;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    border-radius: 4px;
    padding: 2px 8px;
    margin: 2px;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
div[data-testid="stNumberInput"] label {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    color: #4a90d9 !important;
    text-transform: uppercase;
}

.stButton > button {
    background: linear-gradient(135deg, #1a56a0 0%, #0d3a6e 100%);
    color: #e2e8f0;
    border: 1px solid #2563a8;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.06em;
    padding: 10px 20px;
    width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563a8 0%, #1a4a80 100%);
    border-color: #3b82c4;
}

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Sidebar controls ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="main-title">CRYPTO<br>ORACLE</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">// XGBoost multi-horizon predictor</div>', unsafe_allow_html=True)

    coin = st.selectbox(
        "Coin",
        ["btc", "eth", "ada", "bnb", "doge", "sol", "trx", "usdc", "usdt", "xrp"],
        index=0,
    )

    number_days = st.slider("Lag window (days)", min_value=5, max_value=60, value=30, step=5)

    horizon = st.slider(
        "Prediction horizon to display",
        min_value=1, max_value=15, value=1,
        help="Which Target_N to overlay on the chart",
    )

    train_btn = st.button("⚡  Train model")
    eval_btn  = st.button("📊  Evaluate")

    st.markdown("---")
    st.markdown(
        '<p style="font-family:Space Mono,monospace;font-size:10px;color:#2d4a6e;">'
        'Predictions are for research only.<br>Not financial advice.</p>',
        unsafe_allow_html=True,
    )


# ── Session state ──────────────────────────────────────────────────────────
if "model_obj"  not in st.session_state: st.session_state.model_obj  = None
if "trained"    not in st.session_state: st.session_state.trained    = False
if "eval_df"    not in st.session_state: st.session_state.eval_df    = None
if "y_test"     not in st.session_state: st.session_state.y_test     = None
if "preds"      not in st.session_state: st.session_state.preds      = None
if "X_train"    not in st.session_state: st.session_state.X_train    = None


# ── Helper: build or retrieve Models object ────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_model(coin, number_days):
    return Models(number_days=number_days, name=coin)


def load_data(m: Models):
    X_train, y_train, X_test, y_test = m.clean_dataset()
    return X_train, y_test


# ── Main content ───────────────────────────────────────────────────────────
st.markdown(
    f'<div class="main-title">{coin.upper()} / USD</div>'
    f'<div class="main-subtitle">// lag={number_days}d · horizon=Day+{horizon}</div>',
    unsafe_allow_html=True,
)

# ── Train ──────────────────────────────────────────────────────────────────
if train_btn:
    with st.spinner(f"Training XGBoost on {coin.upper()} …"):
        m = get_model(coin, number_days)
        m.reset_cache()
        m.train_model(tune=False)
        X_train, y_test = load_data(m)
        preds = m.test_model()
        st.session_state.model_obj = m
        st.session_state.trained   = True
        st.session_state.y_test    = y_test
        st.session_state.preds     = preds
        st.session_state.X_train   = X_train
    st.success("Model trained successfully!")

# ── Evaluate ───────────────────────────────────────────────────────────────
if eval_btn:
    if not st.session_state.trained:
        st.warning("Train the model first.")
    else:
        with st.spinner("Evaluating …"):
            m = st.session_state.model_obj
            st.session_state.eval_df = m.eval_summary()


# ── Chart ──────────────────────────────────────────────────────────────────
if st.session_state.trained:
    y_test : pd.DataFrame = st.session_state.y_test
    preds  : pd.DataFrame = st.session_state.preds
    X_train: pd.DataFrame = st.session_state.X_train

    target_col = f"Target_{horizon}"
    y_actual   = y_test[target_col]
    y_pred     = preds[target_col]

    # Historical close = first lag column of X_train + first lag of test
    # We reconstruct a rough "historical" series for visual context using
    # the close_lag_1 feature (which equals Close shifted by 1).
    lag_col = "close_lag_1" if "close_lag_1" in X_train.columns else X_train.columns[0]
    hist_series = pd.concat([
        X_train[lag_col],
        y_test[target_col].rename(lag_col),  # placeholder — replaced below
    ])

    # Use y_test Target_1 as a proxy for "actual test close" when available
    actual_close = y_test["Target_1"] if "Target_1" in y_test.columns else y_actual

    # ── Build Plotly figure ────────────────────────────────────────────
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.75, 0.25],
        shared_xaxes=True,
        vertical_spacing=0.04,
    )

    # 1. Historical training prices
    fig.add_trace(go.Scatter(
        x=X_train.index,
        y=X_train[lag_col],
        mode="lines",
        name="Historical (train)",
        line=dict(color="#334155", width=1.5),
        hovertemplate="%{x|%Y-%m-%d}<br>Close: %{y:,.2f}<extra></extra>",
    ), row=1, col=1)

    # 2. Actual test prices (ground truth)
    fig.add_trace(go.Scatter(
        x=y_actual.index,
        y=y_actual.values,
        mode="lines",
        name=f"Actual Day+{horizon}",
        line=dict(color="#22d3ee", width=2),
        hovertemplate="%{x|%Y-%m-%d}<br>Actual: %{y:,.2f}<extra></extra>",
    ), row=1, col=1)

    # 3. Predicted prices
    fig.add_trace(go.Scatter(
        x=y_pred.index,
        y=y_pred.values,
        mode="lines",
        name=f"Predicted Day+{horizon}",
        line=dict(color="#f97316", width=2, dash="dot"),
        hovertemplate="%{x|%Y-%m-%d}<br>Predicted: %{y:,.2f}<extra></extra>",
    ), row=1, col=1)

    # 4. Shaded region between actual & predicted
    fig.add_trace(go.Scatter(
        x=pd.concat([y_actual, y_pred[::-1]]).index,
        y=pd.concat([y_actual, y_pred[::-1]]).values,
        fill="toself",
        fillcolor="rgba(249,115,22,0.07)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Error band",
        showlegend=False,
        hoverinfo="skip",
    ), row=1, col=1)

    # 5. Vertical split line
    split_date = y_actual.index[0]
    fig.add_vline(
        x=split_date,
        line=dict(color="#1e3a5f", width=1.5, dash="dash"),
        row=1, col=1,
    )
    fig.add_annotation(
        x=split_date, y=1, yref="paper",
        text="train / test",
        showarrow=False,
        font=dict(family="Space Mono, monospace", size=10, color="#4a6fa5"),
        bgcolor="#0b0e14",
        borderpad=4,
    )

    # 6. Residuals bar chart (bottom panel)
    residuals = y_actual.values - y_pred.values
    colors_res = ["#22d3ee" if r >= 0 else "#f97316" for r in residuals]
    fig.add_trace(go.Bar(
        x=y_actual.index,
        y=residuals,
        name="Residual",
        marker_color=colors_res,
        opacity=0.7,
        hovertemplate="%{x|%Y-%m-%d}<br>Residual: %{y:,.2f}<extra></extra>",
    ), row=2, col=1)

    fig.add_hline(y=0, line=dict(color="#334155", width=1), row=2, col=1)

    # ── Layout ────────────────────────────────────────────────────────
    fig.update_layout(
        height=620,
        paper_bgcolor="#0b0e14",
        plot_bgcolor="#0b0e14",
        font=dict(family="Space Mono, monospace", color="#94a3b8", size=11),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left",   x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0f1824",
            bordercolor="#1e3a5f",
            font=dict(family="Space Mono, monospace", size=11, color="#e2e8f0"),
        ),
    )
    fig.update_xaxes(
        showgrid=True, gridcolor="#1a2535", gridwidth=1,
        zeroline=False,
        tickfont=dict(family="Space Mono, monospace", size=10),
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="#1a2535", gridwidth=1,
        zeroline=False,
        tickfont=dict(family="Space Mono, monospace", size=10),
        tickformat=",.0f",
    )
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1,
                     title_font=dict(size=11, color="#4a6fa5"))
    fig.update_yaxes(title_text="Residual",    row=2, col=1,
                     title_font=dict(size=11, color="#4a6fa5"))

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Quick metrics row ──────────────────────────────────────────────
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

    r2   = r2_score(y_actual, y_pred)
    mae  = mean_absolute_error(y_actual, y_pred)
    rmse = np.sqrt(mean_squared_error(y_actual, y_pred))
    mape = np.mean(np.abs((y_actual.values - y_pred.values) / (y_actual.values + 1e-9))) * 100

    actual_dir = np.sign(np.diff(y_actual.values))
    pred_dir   = np.sign(np.diff(y_pred.values))
    da         = np.mean(actual_dir == pred_dir) * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, fmt, note in [
        (c1, "R²",   r2,   "{:.4f}", "↑ higher better"),
        (c2, "MAE",  mae,  "{:,.2f}", "↓ lower better"),
        (c3, "RMSE", rmse, "{:,.2f}", "↓ lower better"),
        (c4, "MAPE", mape, "{:.2f}%", "↓ lower better"),
        (c5, "DIR. ACC.", da, "{:.1f}%", "> 50% = skill"),
    ]:
        col.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{fmt.format(val)}</div>'
            f'<div class="metric-sub">{note}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Eval summary table ─────────────────────────────────────────────────────
if st.session_state.eval_df is not None:
    st.markdown('<div class="section-header">Evaluation — All 15 Horizons</div>', unsafe_allow_html=True)

    eval_df: pd.DataFrame = st.session_state.eval_df

    # Color-code R² column
    def color_r2(val):
        if val > 0.9:   return "color:#22d3ee; font-weight:700"
        elif val > 0.7: return "color:#86efac"
        elif val > 0.4: return "color:#fde68a"
        else:           return "color:#f97316"

    def color_da(val):
        if val > 70:   return "color:#22d3ee; font-weight:700"
        elif val > 55: return "color:#86efac"
        elif val > 50: return "color:#fde68a"
        else:          return "color:#f97316"

    styled = (
        eval_df.style
        .applymap(color_r2, subset=["R²"])
        .applymap(color_da, subset=["DA%"])
        .format({"R²": "{:.4f}", "MAE": "{:,.2f}", "RMSE": "{:,.2f}", "MAPE%": "{:.2f}", "DA%": "{:.1f}"})
        .set_table_styles([{
            "selector": "th",
            "props": [
                ("background", "#0f1420"),
                ("color", "#4a90d9"),
                ("font-family", "Space Mono, monospace"),
                ("font-size", "11px"),
                ("letter-spacing", "0.08em"),
                ("border-bottom", "1px solid #1e2535"),
                ("padding", "8px 14px"),
            ]
        }, {
            "selector": "td",
            "props": [
                ("background", "#0b0e14"),
                ("font-family", "Space Mono, monospace"),
                ("font-size", "12px"),
                ("border-bottom", "1px solid #111827"),
                ("padding", "6px 14px"),
            ]
        }])
    )
    st.write(styled.to_html(), unsafe_allow_html=True)


# ── Empty state ────────────────────────────────────────────────────────────
if not st.session_state.trained:
    st.markdown("""
    <div style="
        text-align: center;
        margin-top: 80px;
        padding: 60px;
        border: 1px dashed #1e2535;
        border-radius: 16px;
        background: rgba(15,20,32,0.5);
    ">
        <div style="font-size:48px; margin-bottom:16px;">📡</div>
        <div style="font-family:'Syne',sans-serif; font-size:20px; font-weight:800; color:#e2e8f0; margin-bottom:8px;">
            Select a coin and click Train
        </div>
        <div style="font-family:'Space Mono',monospace; font-size:12px; color:#334155;">
            Historical prices · Predicted vs Actual · Residuals · All metrics
        </div>
    </div>
    """, unsafe_allow_html=True)

