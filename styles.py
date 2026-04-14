"""Custom CSS styles for Knowledge Transfer Hub.

Pharmaceutical-grade design: deep navy + teal accents, clean typography,
card-based layout with subtle depth.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --navy-900: #0a1628;
    --navy-800: #0f2140;
    --navy-700: #162d50;
    --navy-600: #1e3a5f;
    --teal-500: #0d9488;
    --teal-400: #2dd4bf;
    --teal-300: #5eead4;
    --slate-100: #f1f5f9;
    --slate-200: #e2e8f0;
    --slate-300: #cbd5e1;
    --slate-400: #94a3b8;
    --slate-500: #64748b;
    --slate-600: #475569;
    --slate-700: #334155;
    --white: #ffffff;
    --amber-400: #fbbf24;
    --amber-500: #f59e0b;
    --rose-400: #fb7185;
    --rose-500: #f43f5e;
    --emerald-400: #34d399;
    --emerald-500: #10b981;
    --blue-400: #60a5fa;
    --blue-500: #3b82f6;
}

/* ── Global ─────────────────────────────────────────── */

.stApp {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #f8fafc 0%, #e8f0fe 50%, #f0fdf4 100%);
}

.stApp > header {
    background: transparent !important;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem !important;
}

/* ── Sidebar ────────────────────────────────────────── */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--navy-900) 0%, var(--navy-800) 100%);
    border-right: 1px solid rgba(45, 212, 191, 0.15);
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--white) !important;
    font-weight: 600;
    letter-spacing: -0.02em;
}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stMarkdown label {
    color: var(--slate-300) !important;
}

section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stRadio label {
    color: var(--slate-300) !important;
}

section[data-testid="stSidebar"] .stRadio > div > label > div > p {
    color: var(--slate-200) !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(45, 212, 191, 0.2);
}

/* ── Headers ────────────────────────────────────────── */

.stMarkdown h1 {
    color: var(--navy-900) !important;
    font-weight: 700 !important;
    font-size: 2rem !important;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin-bottom: 0.5rem !important;
}

.stMarkdown h2 {
    color: var(--navy-800) !important;
    font-weight: 600 !important;
    font-size: 1.4rem !important;
    letter-spacing: -0.02em;
    border-bottom: 2px solid var(--teal-400);
    padding-bottom: 0.4rem;
    margin-top: 1.5rem !important;
}

.stMarkdown h3 {
    color: var(--navy-700) !important;
    font-weight: 600 !important;
    font-size: 1.15rem !important;
}

/* ── Metric cards ───────────────────────────────────── */

div[data-testid="stMetric"] {
    background: var(--white);
    border: 1px solid var(--slate-200);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 1px 3px rgba(10, 22, 40, 0.06),
                0 4px 12px rgba(10, 22, 40, 0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(10, 22, 40, 0.1),
                0 8px 24px rgba(10, 22, 40, 0.06);
}

div[data-testid="stMetric"] label {
    color: var(--slate-500) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 500;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--navy-900) !important;
    font-weight: 700 !important;
    font-size: 1.8rem !important;
}

/* ── Buttons ────────────────────────────────────────── */

.stButton > button {
    background: linear-gradient(135deg, var(--teal-500), #0f766e) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: 0.01em;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 6px rgba(13, 148, 136, 0.3);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0f766e, #115e59) !important;
    box-shadow: 0 4px 12px rgba(13, 148, 136, 0.4) !important;
    transform: translateY(-1px);
}

.stButton > button:active {
    transform: translateY(0);
}

/* ── Form inputs ────────────────────────────────────── */

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 1.5px solid var(--slate-200) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--teal-400) !important;
    box-shadow: 0 0 0 3px rgba(45, 212, 191, 0.15) !important;
}

.stSelectbox > div > div {
    border-radius: 8px !important;
}

/* ── Expander ───────────────────────────────────────── */

.streamlit-expanderHeader {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    color: var(--navy-800) !important;
    background: var(--white);
    border-radius: 8px;
}

/* ── Tabs ───────────────────────────────────────────── */

.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid var(--slate-200);
}

.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500;
    color: var(--slate-500);
    padding: 0.6rem 1.2rem;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}

.stTabs [aria-selected="true"] {
    color: var(--teal-500) !important;
    border-bottom-color: var(--teal-500) !important;
    font-weight: 600;
}

/* ── Success / Info / Warning / Error ───────────────── */

.stAlert {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Dataframe ──────────────────────────────────────── */

.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
}

/* ── Custom card class (via markdown HTML) ──────────── */

.kt-card {
    background: var(--white);
    border: 1px solid var(--slate-200);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(10, 22, 40, 0.06);
    transition: all 0.2s ease;
}

.kt-card:hover {
    border-color: var(--teal-400);
    box-shadow: 0 4px 16px rgba(13, 148, 136, 0.1);
}

.kt-card h4 {
    color: var(--navy-900);
    margin: 0 0 0.5rem 0;
    font-weight: 600;
}

.kt-card .meta {
    color: var(--slate-500);
    font-size: 0.85rem;
}

.kt-card .tag {
    display: inline-block;
    background: linear-gradient(135deg, rgba(13, 148, 136, 0.1), rgba(45, 212, 191, 0.1));
    color: var(--teal-500);
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-right: 0.3rem;
    border: 1px solid rgba(13, 148, 136, 0.15);
}

.kt-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.kt-badge-active {
    background: rgba(16, 185, 129, 0.12);
    color: #059669;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

.kt-badge-completed {
    background: rgba(59, 130, 246, 0.12);
    color: #2563eb;
    border: 1px solid rgba(59, 130, 246, 0.2);
}

.kt-badge-paused {
    background: rgba(245, 158, 11, 0.12);
    color: #d97706;
    border: 1px solid rgba(245, 158, 11, 0.2);
}

/* ── Hero banner ────────────────────────────────────── */

.kt-hero {
    background: linear-gradient(135deg, var(--navy-900) 0%, var(--navy-700) 60%, var(--teal-500) 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.kt-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(45, 212, 191, 0.15) 0%, transparent 70%);
    border-radius: 50%;
}

.kt-hero::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: 10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(96, 165, 250, 0.1) 0%, transparent 70%);
    border-radius: 50%;
}

.kt-hero h1 {
    color: var(--white) !important;
    font-size: 2.2rem !important;
    margin: 0 !important;
    position: relative;
    z-index: 1;
}

.kt-hero p {
    color: var(--slate-300) !important;
    font-size: 1.05rem;
    margin: 0.5rem 0 0 0;
    position: relative;
    z-index: 1;
}

/* ── Progress bar ───────────────────────────────────── */

.kt-progress-bar {
    background: var(--slate-200);
    border-radius: 10px;
    height: 8px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.kt-progress-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, var(--teal-500), var(--teal-400));
    transition: width 0.5s ease;
}

/* ── Checklist ──────────────────────────────────────── */

.kt-checklist-item {
    display: flex;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--slate-100);
    font-size: 0.95rem;
}

.kt-checklist-done {
    color: var(--emerald-500);
    text-decoration: line-through;
    opacity: 0.7;
}

/* ── Scrollbar ──────────────────────────────────────── */

::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: var(--slate-100);
}

::-webkit-scrollbar-thumb {
    background: var(--slate-300);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--slate-400);
}

/* ── Footer ─────────────────────────────────────────── */

.kt-footer {
    text-align: center;
    color: var(--slate-400);
    font-size: 0.8rem;
    padding: 2rem 0 1rem 0;
    border-top: 1px solid var(--slate-200);
    margin-top: 3rem;
}
</style>
"""
