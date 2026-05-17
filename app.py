import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from google import genai
import tools_logic as logic
from datetime import datetime, timezone, timedelta

TZ = ZoneInfo("Africa/Cairo")
now = datetime.now(TZ)




# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OlistIQ — Think Smarter With Your Data",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── MASTER CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
  --bg:        #022076;
  --bg2:       #000033;
  --bg3:       #000041;
  --card:      #000033;
  --border:    #000041;
  --border2:   #E8F0FC;
  --green:     #00FF41;
  --green2:    #2970E8;
  --green-dim: #0D1E45;
  --red:       #FF0000;
  --amber:     #FFD700;
  --blue:      #0000FF;
  --text:      #ffffff;
  --text2:     #7A9BCF;
  --text3:     #e4e1e1;
  --mono:      'JetBrains Mono', monospace;
  --display:   'Bebas Neue', sans-serif;
  --body:      'Outfit', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--body) !important;
}
#MainMenu, footer, header, .stDeployButton,
div[data-testid="stToolbar"] { display: none !important; }

::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

.main .block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── Top bar ── */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; height: 56px;
    background: #000033;
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 32px; z-index: 1000;
}
.brand-name { font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 26px; letter-spacing: 1px; color: #fff; line-height:1; }
.brand-iq   { color: #e44f37; }
.brand-sub  { font-family: 'Outfit', sans-serif; font-weight: 500; font-size: 10px; color: #0b4de5; letter-spacing: 1.5px; margin-top:4px; opacity: 0.8; }.olist-logo {
    height: 10px; width: 10px;
}
.live-dot   { width:6px; height:6px; background:var(--green); border-radius:50%; animation:blink 2s infinite; box-shadow:0 0 6px var(--green); display:inline-block; margin-right:6px; }
.live-text  { font-family:var(--mono); font-size:10px; color:var(--green); letter-spacing:1px; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── Hero ── */
.hero {
    padding: 72px 48px 32px;
    background: linear-gradient(180deg, #011647 0%, var(--bg) 100%);
    border-bottom: 1px solid var(--border);
    position: relative; overflow: hidden;
}
.hero::before {
    content: 'OLIST'; position: absolute; right: -20px; top: -40px;
    font-family: var(--display); font-size: 220px;
    color: rgba(41,112,232,0.05); pointer-events: none; user-select: none;
}
.hero-title { font-family:var(--display); font-size:72px; line-height:0.95; letter-spacing:1px; color:#fff; }
.hero-title span { color:#e44f37; }
.hero-sub { font-family:'outfit'; font-size:15px; color:var(--text); letter-spacing:3px; text-transform:uppercase; margin-top:10px; }

/* ── KPI Strip ── */
.kpi-strip {
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: 1px; background: var(--border);
    border: 1px solid var(--border); border-radius: 12px; overflow: hidden; margin-top: 28px;
}
.kpi-tile { background: var(--card); padding: 20px 22px; transition: background 0.2s; }
.kpi-tile:hover { background: var(--bg3); }
.kpi-icon { font-family:var(--mono); font-size:14px; letter-spacing:2px; text-transform:uppercase; color:#0091fe; margin-bottom:10px; }
.kpi-num  { font-family:var(--display); font-size:32px; letter-spacing:-0.5px; color:#fff; line-height:1; }
.kpi-delta { font-family:var(--mono); font-size:10px; margin-top:6px; }
.kpi-delta.up { color:var(--green); }
.kpi-delta.down { color:var(--red); }
.kpi-delta.warn { color:var(--amber); }
.kpi-delta.neutral { color:var(--text3); }
.kpi-accent-green { border-top: 2px solid var(--green); }
.kpi-accent-blue  { border-top: 2px solid var(--blue); }
.kpi-accent-amber { border-top: 2px solid var(--amber); }
.kpi-accent-red   { border-top: 2px solid var(--red); }
.kpi-accent-dim   { border-top: 2px solid var(--border2); }

/* ── Alert bar ── */
.alert-bar { margin: 20px 48px ; padding: 11px 18px 11px; border-radius: 8px; font-size: 14px; font-family:var(--mono); display:flex; align-items:center; gap:10px; letter-spacing:0.3px; }
.alert-critical { background:#0A0814; border:1px solid #3A0A0A; color:#FF6B6B; border-left:3px solid var(--red); }
.alert-warning  { background:#0A0E1A; border:1px solid #3A2800; color:#FA7305; border-left:3px solid #FA7305; }
.alert-ok       { background:#080D1A; border:1px solid #0A1B4A; color:#82B4FF; border-left:3px solid var(--green); }

/* ── Chart panels ── */
.chart-panel { background:var(--card); padding:24px; }
.panel-title { font-family:var(--display); font-size:18px; letter-spacing:1px; color:#fff; margin-bottom:4px; display:flex; align-items:center; gap:10px; }
.panel-badge { font-family:var(--mono); font-size:8px; letter-spacing:2px; padding:3px 8px; border-radius:4px; background:var(--green-dim); color:var(--green2); text-transform:uppercase; }
.panel-sub { font-family:var(--mono); font-size:9px; color:var(--text3); letter-spacing:2px; text-transform:uppercase; margin-bottom:16px; }

/* ── Seg cards ── */
.seg-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-top:12px; }
.seg-card { background:var(--bg2); border:1px solid var(--border); border-radius:8px; padding:14px 16px; transition:border-color 0.2s; }
.seg-card:hover { border-color:var(--green2); }
.seg-name { font-family:var(--mono); font-size:9px; letter-spacing:2px; text-transform:uppercase; color:var(--text3); margin-bottom:6px; }
.seg-val  { font-family:var(--display); font-size:22px; }
.seg-sub  { font-family:var(--mono); font-size:9px; color:var(--text3); margin-top:3px; }

/* ── Streamlit overrides ── */
.stTextInput>div>div>input {
    background:var(--bg3) !important; border:1px solid var(--border2) !important;
    border-radius:8px !important; color:var(--text) !important;
    font-family:var(--body) !important; font-size:13px !important; padding:10px 14px !important;
}
.stTextInput>div>div>input:focus { border-color:var(--green2) !important; box-shadow:0 0 0 2px rgba(41,112,232,0.15) !important; }
.stTextInput>div>div>input::placeholder { color:var(--text3) !important; }
.stTextInput>div { border:none !important; background:transparent !important; }
.stTextInput label { display:none !important; }

.stButton>button {
    background:linear-gradient(135deg,var(--green2),#1655C0) !important;
    color:#000 !important; border:none !important; border-radius:8px !important;
    font-family:var(--display) !important; font-size:14px !important; letter-spacing:1px !important;
    padding:8px 18px !important; height:40px !important; transition:all 0.2s !important;
}
.stButton>button:hover {
    background:linear-gradient(135deg,#82BFFF,var(--green2)) !important;
    transform:translateY(-1px) !important; box-shadow:0 4px 14px rgba(41,112,232,0.35) !important;
}

.stTabs [data-baseweb="tab-list"] { background:var(--bg2) !important; border-bottom:1px solid var(--border) !important; gap:0 !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:var(--text3) !important; font-family:var(--mono) !important; font-size:10px !important; letter-spacing:2px !important; text-transform:uppercase !important; border:none !important; padding:12px 20px !important; }
.stTabs [aria-selected="true"] { color:var(--green) !important; border-bottom:2px solid var(--green) !important; background:var(--green-dim) !important; }

.stDateInput>div>div>input { background:var(--bg3) !important; border:1px solid var(--border2) !important; color:var(--text) !important; border-radius:8px !important; font-size:12px !important; }
.stSelectbox>div>div { background:var(--bg3) !important; border:1px solid var(--border2) !important; border-radius:8px !important; color:var(--text) !important; }
.stSpinner>div { border-top-color:var(--green2) !important; }
[data-testid="stMetric"] { background:var(--card) !important; border:1px solid var(--border) !important; border-radius:10px !important; padding:16px !important; }
[data-testid="stMetricValue"] { font-family:var(--display) !important; font-size:28px !important; color:#fff !important; }
[data-testid="stMetricDelta"] { font-family:var(--mono) !important; font-size:11px !important; }



/* ── Chat panel ── */
/* Target the st.container(key="chat_container") wrapper */
[data-testid="stVerticalBlock"]:has(div[data-testid="stVerticalBlockBorderWrapper"][data-stale="false"]) div[data-testid="stVerticalBlock"]:has(button[data-testid="stBaseButton-secondary"][kind="secondary"]:first-child) {
    /* fallback - handled by key selector below */
}

/* Primary fix: target the container by its key */
div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="element-container"] button[title="Close Chat"]),
section.main div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stVerticalBlockBorderWrapper"]) {
    position: static !important;
}

/* The actual floating panel — targets our keyed container */
div[data-testid="stVerticalBlock"]:has(> div > div[data-testid="element-container"] > div[data-testid="stVerticalBlockBorderWrapper"]) {
    all: unset !important;
}

#chat_container,
div[data-testid="stVerticalBlock"][id*="chat"] {
    position: fixed !important;
    bottom: 108px !important;
    left: 32px !important;
    width: 430px !important;
    height: 490px !important;
    background: var(--bg2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 16px !important;
    z-index: 999999 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    box-shadow: 0 24px 64px rgba(0,0,0,0.75), 0 0 0 1px rgba(41,112,232,0.08) !important;
    animation: slideUp 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
}

/* Keep .chat-panel for any legacy html still using it */
.chat-panel {
    position: fixed;
    bottom: 108px;
    left: 32px;
    width: 430px;
    height: 490px;
    background: var(--bg2);
    border: 1px solid var(--border2);
    border-radius: 16px;
    z-index: 999999 !important;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 24px 64px rgba(0,0,0,0.75), 0 0 0 1px rgba(41,112,232,0.08);
    animation: slideUp 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
@keyframes slideUp { from{opacity:0;transform:translateY(30px) scale(0.95)} to{opacity:1;transform:translateY(0) scale(1)} }

.chat-hd {
    background:linear-gradient(135deg,#08101E,#080D1A); padding:14px 16px;
    border-bottom:1px solid var(--border); display:flex; align-items:center;
    justify-content:space-between; flex-shrink:0;
}
.tommy-avi  { width:36px; height:36px; background:linear-gradient(135deg,var(--green2),#0D2A6E); border-radius:9px; display:flex; align-items:center; justify-content:center; font-size:17px; box-shadow:0 0 10px rgba(41,112,232,0.3); }
.tommy-nm   { font-family:var(--display); font-size:17px; letter-spacing:1px; color:#fff; }
.tommy-st   { font-family:var(--mono); font-size:9px; color:var(--green2); letter-spacing:1.5px; display:flex; align-items:center; gap:4px; }
.tommy-st::before { content:''; width:5px; height:5px; background:var(--green); border-radius:50%; box-shadow:0 0 4px var(--green); }

.sq-section { padding:10px 12px; border-bottom:1px solid var(--border); flex-shrink:0; background:var(--bg3); }
.sq-label   { font-family:var(--mono); font-size:8px; letter-spacing:2px; color:var(--text3); text-transform:uppercase; margin-bottom:7px; }
.sq-grid    { display:grid; grid-template-columns:1fr 1fr; gap:4px; }
.sq-btn     { background:var(--bg2); border:1px solid var(--border); border-radius:6px; padding:6px 9px; font-size:10.5px; color:var(--text2); cursor:pointer; transition:all 0.15s; text-align:left; font-family:var(--body); line-height:1.3; }
.sq-btn:hover { border-color:var(--green2); color:var(--green); background:var(--green-dim); }

.msgs-area  { flex:1; overflow-y:auto; padding:14px 12px; display:flex; flex-direction:column; gap:30px; }
.msgs-area::-webkit-scrollbar { width:2px; }
.msgs-area::-webkit-scrollbar-thumb { background:var(--border2); }

.msg-user   { display:flex; justify-content:flex-end; gap:10px; }
.msg-tommy  { display:flex; gap:18px; align-items:flex-start; }
.bub-user   { background:linear-gradient(135deg,#0A2818,#080D1A); border:1px solid #0F3520; border-radius:12px 12px 2px 12px; padding:9px 13px; max-width:78%; font-size:13px; color:#A8C8FF; line-height:1.5;margin-bottom: 8px; }
.bub-tommy  { background:var(--bg3); border:1px solid var(--border2); border-radius:2px 12px 12px 12px; padding:9px 13px; max-width:85%; font-size:13px; color:var(--text2); line-height:1.6;margin-bottom: 8px; }
.bub-tommy b, .bub-tommy strong { color:var(--text); }
.mini-avi   { width:25px; height:25px; background:var(--green-dim); border:1px solid var(--border2); border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:12px; flex-shrink:0; margin-top:2px; }

.chat-in-area { padding:10px 12px; border-top:1px solid var(--border); background:var(--bg); flex-shrink:0;gap:18px }

/* typing */
.typing { display:flex; gap:4px; align-items:center; padding:9px 13px; }
.tdot   { width:6px; height:6px; background:var(--green2); border-radius:50%; animation:typePulse 1.2s infinite; }
.tdot:nth-child(2){animation-delay:0.2s} .tdot:nth-child(3){animation-delay:0.4s}
@keyframes typePulse { 0%,60%,100%{transform:translateY(0);opacity:0.4} 30%{transform:translateY(-5px);opacity:1} }

</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in [("chat_open", False), ("messages", []),
             ("pending_q", None), ("health_cache", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Agent ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_gemini_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def init_agent():
    """Create a fresh chat session each time (do NOT cache the chat object)."""
    client = get_gemini_client()
    if not client:
        return None
    PROMPT = (
        "You are Tommy, a proactive Business Intelligence Agent for OlistIQ, "
        "a leading Brazilian E-commerce analytics platform. "
        "CRITICAL: Every NEW conversation → silently run get_business_health_check first. "
        "If [CRITICAL] or [WARNING] found, mention them immediately in your greeting. "
        "Be concise, data-driven, end each response with one clear recommendation. "
        "Format currency $X,XXX. Percentages 1 decimal. Never say 'I cannot' — use tools."
    )
    try:
        return client.chats.create(
            model="gemini-2.5-flash",
            config=genai.types.GenerateContentConfig(
                system_instruction=PROMPT,
                tools=[
                    logic.get_revenue_by_range, logic.Top_selling_products,
                    logic.Detect_sales_anomalies, logic.generate_business_insights,
                    logic.compare_periods, logic.analyze_sales_performance,
                    logic.analyze_marketing_efficiency, logic.analyze_customer_loyalty,
                    logic.get_business_health_check, logic.get_quick_alerts,
                ]
            )
        )
    except Exception:
        return None

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_kpis():
    df = logic.final_gold_file.copy()
    df['month'] = df['order_purchase_timestamp'].dt.to_period('M')
    monthly = df.groupby('month')['payment_value'].sum()
    last_rev  = monthly.iloc[-1];  prev_rev  = monthly.iloc[-2] if len(monthly)>1 else last_rev
    rev_delta = (last_rev-prev_rev)/prev_rev*100 if prev_rev else 0
    monthly_o = df.groupby('month')['order_id'].nunique()
    last_o    = monthly_o.iloc[-1]; prev_o    = monthly_o.iloc[-2] if len(monthly_o)>1 else last_o
    o_delta   = (last_o-prev_o)/prev_o*100 if prev_o else 0
    cs = df.groupby('customer_unique_id')['order_id'].nunique()
    ret = len(cs[cs>1])/len(cs)*100
    return dict(total_rev=df['payment_value'].sum(), last_rev=last_rev, rev_delta=rev_delta,
                total_orders=df['order_id'].nunique(), o_delta=o_delta,
                total_cust=df['customer_unique_id'].nunique(),
                avg_order=df['payment_value'].mean(), retention=ret)

@st.cache_data(ttl=300)
def get_monthly():
    df = logic.final_gold_file.copy()
    df['month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    m = df.groupby('month').agg(revenue=('payment_value','sum'), orders=('order_id','nunique')).reset_index()
    m['growth'] = m['revenue'].pct_change()*100
    m['growth'] = m['growth'].clip(-150, 150)   # cap outliers
    m = m.dropna(subset=['growth'])              # remove first row (no previous month)
    m = m.iloc[1:]                               # skip second month too (ramp-up distortion)
    return m

@st.cache_data(ttl=300)
def get_cats():
    df = logic.final_gold_file.copy()
    c = df.groupby('product_category_name_english')['payment_value'].sum().sort_values(ascending=False).head(10).reset_index()
    c.columns = ['category','revenue']
    return c

@st.cache_data(ttl=300)
def get_rfm_segs():
    return logic._rfm_df.groupby('Segment').agg(count=('Monetary','count'), revenue=('Monetary','sum'), avg_ltv=('Monetary','mean')).reset_index()

# ── Chart theme ───────────────────────────────────────────────────────────────
CL = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
          font=dict(family='Outfit',color='#7A9BCF',size=11),
          margin=dict(l=0,r=0,t=8,b=0),
          xaxis=dict(gridcolor='#0C1A28',showline=False,tickfont=dict(size=10)),
          yaxis=dict(gridcolor='#0C1A28',showline=False,tickfont=dict(size=10)),
          showlegend=False,
          hoverlabel=dict(bgcolor='#0A1220',bordercolor='#162840',font=dict(family='JetBrains Mono',size=11,color='#E8F4FF')))

SEG_C = {'Champions':'#0079FF','Loyal-customer':'#0079FF','New-customer':'#0079FF',
          'At-Risk':'#AC0000','Churned':'#AC0000','Other':'#0079FF'}
# ── TOP BAR ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
  <div style="display:flex;align-items:center;gap:10px">
    <!-- Olist logo SVG (official blue style) -->
    <img src="https://d2r9epyceweg5n.cloudfront.net/apps/2-30-pt_BR-logo-olist.png" alt="Olist Logo" width="150" height="100">
    <div style="width:1px;height:10px;background:var(--border2)"></div>
    <div>
      <div class="brand-name">Olist<span class="brand-iq">IQ</span></div>
      <div class="brand-sub">✦ THINK SMARTER WITH YOUR DATA</div>
    </div>
""", unsafe_allow_html=True)
st.markdown(f"""
<div style="display:flex;align-items:center">
    <span class="live-dot"></span>
    <span class="live-text">LIVE · {now.datetime('%d %b %Y  %H:%M')}</span>
</div>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
try:
    kpi    = get_kpis()
    mdf    = get_monthly()
    cdf    = get_cats()
    rdf    = get_rfm_segs()
    data_ok = True
except Exception as e:
    data_ok = False
    st.error(f"Data error: {e}")

# ── HERO + KPIs ───────────────────────────────────────────────────────────────
if data_ok:
    st.markdown(f"""
    <div class="hero">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div>
          <div class="hero-title">BUSINESS<br><span>INTELLIGENCE</span><br>PLATFORM</div>
          <div class="hero-sub">Olist E-Commerce · AI-Powered · Real-Time Data</div>
        </div>
        <div style="text-align:right;font-family:var(--mono);font-size:11px;color:var(--text3);line-height:1.9">
          <span style="font-family:var(--display);font-size:32px;color:var(--text2);letter-spacing:2px;display:block">{now.strftime('%H:%M')}</span>
          {now.strftime('%A, %B %d %Y')}<br>
          <span style="color:var(--green2)">▲ AUTO-REFRESH ACTIVE</span>
        </div>
      </div>
      <div class="kpi-strip">
        <div class="kpi-tile kpi-accent-green">
          <div class="kpi-icon">Total Revenue</div>
          <div class="kpi-num">${kpi['total_rev']/1e6:.1f}M</div>
          <div class="kpi-delta {'up' if kpi['rev_delta']>=0 else 'down'}">
            {'▲' if kpi['rev_delta']>=0 else '▼'} {abs(kpi['rev_delta']):.1f}% last month
          </div>
        </div>
        <div class="kpi-tile kpi-accent-blue">
          <div class="kpi-icon">Total Orders</div>
          <div class="kpi-num">{kpi['total_orders']:,}</div>
          <div class="kpi-delta {'up' if kpi['o_delta']>=0 else 'down'}">
            {'▲' if kpi['o_delta']>=0 else '▼'} {abs(kpi['o_delta']):.1f}% last month
          </div>
        </div>
        <div class="kpi-tile kpi-accent-amber">
          <div class="kpi-icon">Unique Customers</div>
          <div class="kpi-num">{kpi['total_cust']/1e3:.0f}K</div>
          <div class="kpi-delta neutral">ALL TIME</div>
        </div>
        <div class="kpi-tile kpi-accent-dim">
          <div class="kpi-icon">Avg Order Value</div>
          <div class="kpi-num">${kpi['avg_order']:.0f}</div>
          <div class="kpi-delta neutral">PER ORDER</div>
        </div>
        <div class="kpi-tile kpi-accent-{'green' if kpi['retention']>=10 else 'red'}">
          <div class="kpi-icon">Retention Rate</div>
          <div class="kpi-num">{kpi['retention']:.1f}%</div>
          <div class="kpi-delta {'up' if kpi['retention']>=10 else 'down'}">
            {'HEALTHY' if kpi['retention']>=10 else 'NEEDS WORK'}
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Auto alert
    if st.session_state.health_cache is None:
        try:
            st.session_state.health_cache = logic.get_quick_alerts()
        except:
            st.session_state.health_cache = ""
    if st.session_state.health_cache:
        h = st.session_state.health_cache
        cls = "alert-critical" if "🚨" in h else ("alert-warning" if "⚠️" in h else "alert-ok")
        st.markdown(f'<div class="alert-bar {cls}">{h}</div>', unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Revenue & Trends",
    "🏆  Top Categories",
    "👥  Customer Segments",
    "🔍  Deep Analysis",
])

# ─── Tab 1 ───────────────────────────────────────────────────────────────────
with tab1:
    if data_ok:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">MONTHLY REVENUE <span class="panel-badge">LIVE</span></div><div class="panel-sub">Payment value · all categories</div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=mdf['month'], y=mdf['revenue'],
                fill='tozeroy', fillcolor='rgba(11,77,229,0.3)',
                line=dict(color='#0b4de5',width=2), mode='lines+markers',
                marker=dict(size=4,color='#0b4de5'),
                hovertemplate='<b>%{x}</b><br>$%{y:,.0f}<extra></extra>'))
            fig.update_layout(**CL, height=240)
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig,width='content', config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">GROWTH %</div><div class="panel-sub">Month-over-month change</div>', unsafe_allow_html=True)
            colors_b = ['#0b4de5' if v>=0 else '#AC0000' for v in mdf['growth'].fillna(0)]
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=mdf['month'], y=mdf['growth'].fillna(0),
                marker_color=colors_b, hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>'))
            fig2.add_hline(y=0, line_color='#162840', line_width=1)
            fig2.update_layout(**CL, height=240)
            fig2.update_xaxes(tickangle=-45)
            st.plotly_chart(fig2,width='stretch', config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="chart-panel" style="margin-top:1px">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">ORDER VOLUME <span class="panel-badge">TREND</span></div><div class="panel-sub">Unique orders per month</div>', unsafe_allow_html=True)
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=mdf['month'], y=mdf['orders'],
            fill='tozeroy', fillcolor='rgba(11,77,229,0.3)',
            line=dict(color='#0b4de5',width=2), mode='lines+markers',
            marker=dict(size=4,color='#0b4de5'),
            hovertemplate='<b>%{x}</b><br>%{y:,} orders<extra></extra>'))
        fig3.update_layout(**CL, height=180)
        fig3.update_xaxes(tickangle=-45)
        st.plotly_chart(fig3,width='stretch', config={'displayModeBar':False})
        st.markdown('</div>', unsafe_allow_html=True)

# ─── Tab 2 ───────────────────────────────────────────────────────────────────
with tab2:
    if data_ok:
        c1, c2 = st.columns([3,2])
        with c1:
            st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">TOP 10 CATEGORIES</div><div class="panel-sub">All time · by revenue</div>', unsafe_allow_html=True)
            fig4 = go.Figure(go.Bar(y=cdf['category'], x=cdf['revenue'], orientation='h',
                marker=dict(color=cdf['revenue'], colorscale=[[0,'#E8F0FC'],[1,'#0b4de5']], showscale=False),
                hovertemplate='<b>%{y}</b><br>$%{x:,.0f}<extra></extra>'))
            fig4.update_layout(**CL, height=340)
            fig4.update_yaxes(tickfont=dict(size=10), autorange='reversed')
            st.plotly_chart(fig4,width='content', config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">REVENUE SHARE</div><div class="panel-sub">% of total · top 10</div>', unsafe_allow_html=True)
            pie_c = ['#BBDEFB','#64B5F6','#2196F3','#1976D2','#0D47A1','#032669','#031753','#5C0000','#850000','#AC0000']
            fig5 = go.Figure(go.Pie(labels=cdf['category'], values=cdf['revenue'], hole=0.62,
                marker=dict(colors=pie_c, line=dict(color='#445ab7',width=2)),
                hovertemplate='<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>', textinfo='none'))
            fig5.add_annotation(text=f"${cdf['revenue'].sum()/1e6:.1f}M", x=0.5, y=0.5,
                showarrow=False, font=dict(family='Bebas Neue',size=26,color='#fff'))
            fig5.update_layout(**CL, height=340)
            st.plotly_chart(fig5,width='stretch', config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)

# ─── Tab 3 ───────────────────────────────────────────────────────────────────
with tab3:
    if data_ok:
        c1, c2 = st.columns([2,3])
        with c1:
            st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">SEGMENTS</div><div class="panel-sub">RFM classification</div>', unsafe_allow_html=True)
            st.markdown('<div class="seg-grid">', unsafe_allow_html=True)
            for _, row in rdf.iterrows():
                color = SEG_C.get(row['Segment'],'#455A64')
                st.markdown(f"""
                <div class="seg-card" style="border-left:3px solid {color}">
                  <div class="seg-name">{row['Segment']}</div>
                  <div class="seg-val" style="color:{color}">{int(row['count']):,}</div>
                  <div class="seg-sub">${row['avg_ltv']:,.0f} avg LTV</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">REVENUE BY SEGMENT</div><div class="panel-sub">Total revenue contribution</div>', unsafe_allow_html=True)
            fig6 = go.Figure()
            for _, row in rdf.sort_values('revenue', ascending=True).iterrows():
                fig6.add_trace(go.Bar(y=[row['Segment']], x=[row['revenue']], orientation='h',
                    marker_color=SEG_C.get(row['Segment'],'#455A64'),
                    hovertemplate=f"<b>{row['Segment']}</b><br>$%{{x:,.0f}}<extra></extra>"))
            fig6.update_layout(**CL, height=220)
            st.plotly_chart(fig6,width='stretch', config={'displayModeBar':False})

            st.markdown('<div class="panel-sub" style="margin-top:16px">COUNT vs AVG LTV</div>', unsafe_allow_html=True)
            fig7 = go.Figure(go.Scatter(x=rdf['count'], y=rdf['avg_ltv'],
                mode='markers+text',
                marker=dict(size=rdf['revenue']/rdf['revenue'].max()*60+10,
                    color=[SEG_C.get(s,'#455A64') for s in rdf['Segment']],
                    opacity=0.85, line=dict(color='#0A0E1A',width=2)),
                text=rdf['Segment'], textposition='top center',
                textfont=dict(size=9,color='#7A9BCF'),
                hovertemplate='<b>%{text}</b><br>Count: %{x:,}<br>Avg LTV: $%{y:,.0f}<extra></extra>'))
            fig7.update_layout(**CL, height=200)
            st.plotly_chart(fig7,width='stretch', config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)

# ─── Tab 4 ───────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div style="padding:24px 0">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="panel-title" style="font-size:14px">REVENUE RANGE</div>', unsafe_allow_html=True)
        sd = st.date_input("Start", key="d_s"); ed = st.date_input("End", key="d_e")
        if st.button("Calculate", key="b_rev"):
            with st.spinner(""):
                r = logic.get_revenue_by_range(str(sd), str(ed))
            st.markdown(f'<div class="alert-ok" style="margin-top:8px;font-size:12px">{r}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel-title" style="font-size:14px">TOP CATEGORY</div>', unsafe_allow_html=True)
        ps = st.date_input("Period start", key="p_s"); pe = st.date_input("Period end", key="p_e")
        if st.button("Find Top", key="b_top"):
            with st.spinner(""):
                r = logic.Top_selling_products(str(ps), str(pe))
            st.markdown(f'<div class="alert-ok" style="margin-top:8px;font-size:12px">{r}</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="panel-title" style="font-size:14px">ANOMALY SCANNER</div>', unsafe_allow_html=True)
        td = st.date_input("Target date", key="t_d")
        if st.button("Scan for Spike", key="b_scan"):
            with st.spinner(""):
                r = logic.Detect_sales_anomalies(str(td))
            cls = "alert-warning" if "Spike" in r else "alert-ok"
            st.markdown(f'<div class="{cls}" style="margin-top:8px;font-size:12px">{r}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5 = st.columns(2)
    with c4:
        st.markdown('<div class="panel-title" style="font-size:14px">PERIOD COMPARISON</div>', unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1: cs=st.date_input("Curr start",key="cs"); ce=st.date_input("Curr end",key="ce")
        with cc2: ps2=st.date_input("Prev start",key="ps2"); pe2=st.date_input("Prev end",key="pe2")
        if st.button("Compare", key="b_cmp"):
            with st.spinner(""):
                r = logic.compare_periods(str(cs),str(ce),str(ps2),str(pe2))
            st.code(r, language='text')
    with c5:
        st.markdown('<div class="panel-title" style="font-size:14px">BUSINESS HEALTH CHECK</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Full automated scan</div>', unsafe_allow_html=True)
        if st.button("▶  Run Health Check", key="b_health"):
            with st.spinner("Scanning all metrics..."):
                r = logic.get_business_health_check()
            cls = "alert-critical" if "[CRITICAL]" in r else ("alert-warning" if "[WARNING]" in r else "alert-ok")
            st.markdown(f'<div class="{cls}" style="font-size:12px;line-height:1.8">{r}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════════════════
#  FLOATING CHAT (Tommy Robot)
# ══════════════════════════════════════════════════════════════════════════════
SUGGESTED = [
    ("📊", "What was our total revenue last month?"),
    ("🏆", "Top selling categories this year?"),
    ("📉", "Were there any sales drops recently?"),
    ("👥", "Who are our most valuable customers?"),
    ("⚡", "Detect anomalies in the latest data"),
    ("🔁", "What is our customer retention rate?"),
    ("💰", "How efficient is our marketing spend?"),
    ("📈", "Compare Q1 vs Q2 performance"),
    ("🚨", "Run a full business health check"),
    ("📆", "Show the monthly revenue trends"),
]
 
# ── CSS: Chat panel fixed position ────────────────────────────────────────────────────
st.markdown("""
<style>


/* Make the inner vertical block fill the panel and scroll */
div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    height: 490px !important;
    overflow: hidden !important;
}
/* Remove any default Streamlit padding/margin inside the panel */
div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] > div {
    padding: 0 !important;
}
/* Messages area inside panel — scrollable */
div[data-testid="stVerticalBlockBorderWrapper"] .msgs-area {
    flex: 1 !important;
    overflow-y: auto !important;
    max-height: 220px !important;
}
/* Suggested questions buttons inside panel */
div[data-testid="stVerticalBlockBorderWrapper"] button[kind="secondary"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-size: 10.5px !important;
    color: var(--text2) !important;
    text-align: center !important;
    font-family: var(--body) !important;
    line-height: 1.3 !important;
    padding: 6px 9px !important;
    width: 100% !important;
    height: auto !important;
    white-space: normal !important;
    min-height: unset !important;
    gap:20px !important;
}
/* FAB container handled below */
div[data-testid="stVerticalBlockBorderWrapper"] button[kind="secondary"]:hover {
    border-color: var(--green2) !important;
    color: var(--green) !important;
    background: var(--green-dim) !important;
}
/* Close button & send button inside panel */
div[data-testid="stVerticalBlockBorderWrapper"] button[kind="secondary"][data-testid*="close"],
div[data-testid="stVerticalBlockBorderWrapper"] button[kind="secondary"][data-testid*="snd"] {
    width: auto !important;
}
/* Input inside panel */
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stTextInput"] input {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
</style>
""", unsafe_allow_html=True)



# ── FAB: 

st.markdown('''
<style>
.tommy-fab {
    position:absolute !important;
    bottom: -70px !important;
    left: -10px !important;
    width: 72px !important;
    height: 72px !important;
    min-height: unset !important;
    border-radius: 50% !important;
    overflow: hidden !important;
    pointer-events: none !important;
    z-index: 9998 !important;
    border: 2.5px solid rgba(41,112,232,0.7) !important;
    box-shadow: 0 8px 30px rgba(41,112,232,0.5) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
.tommy-fab img {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    display: block !important;
}

button[title="Chat with Tommy"] {
    position: fixed !important;
    bottom: 44px !important;
    left: 16px !important;
    width: 26px !important;
    height: 40px !important;
    
    opacity: 0 !important;
    z-index: 99999 !important;
    cursor: pointer !important;
    padding: 0 !important;
    margin: 0 !important;
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    transform: none !important;
}
button[title="Chat with Tommy"]:hover + .tommy-fab,
button[title="Chat with Tommy"]:hover ~ .tommy-fab {
    transform: scale(1.08) translateY(-3px) !important;
    box-shadow: 0 16px 40px rgba(41,112,232,0.8) !important;
}


}
</style>
<div class="tommy-fab">
  <img src="https://i.postimg.cc/ydmq2Zdf/bot-logo.jpg" alt="Tommy">
</div>
''', unsafe_allow_html=True)

if st.button("chat", key="fab_btn", help="Chat with Tommy", type="secondary"):
    st.session_state.chat_open = not st.session_state.chat_open
    
# ── Chat panel — все widgets inside st.container so they render inside the fixed box ──
if st.session_state.chat_open:
    with st.container(border=True, key="chat_panel_container"):
        # Header
        st.markdown("""
        <div class="chat-hd">
          <div style="display:flex;align-items:center;gap:11px">
            <div class="tommy-avi"><img src="https://i.postimg.cc/ydmq2Zdf/bot-logo.jpg" style="width:100%;height:100%;object-fit:cover;border-radius:8px;"></div>
            <div>
              <div class="tommy-nm">TOMMY</div>
              <div class="tommy-st">ONLINE · AI AGENT</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("✕", key="close_c", help="Close Chat"):
            st.session_state.chat_open = False
            st.rerun()

        # Suggested questions
        st.markdown("""
        <div class="sq-section">
          <div class="sq-label">Suggested questions</div>
        </div>
        """, unsafe_allow_html=True)

        sq_cols = st.columns(2)
        for i, (icon, q) in enumerate(SUGGESTED):
            with sq_cols[i % 2]:
                if st.button(f"{icon} {q}", key=f"sq_{i}"):
                    st.session_state.pending_q = q
                    st.rerun()

        # Messages
        st.markdown('<div class="msgs-area">', unsafe_allow_html=True)
        if not st.session_state.messages:
            st.markdown("""
            <div class="msg-tommy">
              <div class="mini-avi"><img src="https://i.postimg.cc/ydmq2Zdf/bot-logo.jpg" style="width:100%;height:100%;object-fit:cover;border-radius:5px;"></div>
              <div class="bub-tommy">
                Hi! I'm <b>Tommy</b>, your Olist BI Agent.<br>
                I'm scanning your latest data now — ask me anything or pick a question above.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="msg-user"><div class="bub-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
                else:
                    content = msg["content"].replace("\n", "<br>")
                    st.markdown(f'<div class="msg-tommy"><div class="mini-avi"><img src="https://i.postimg.cc/ydmq2Zdf/bot-logo.jpg" style="width:100%;height:100%;object-fit:cover;border-radius:5px;"></div><div class="bub-tommy">{content}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Input row
        st.markdown('<div class="chat-in-area">', unsafe_allow_html=True)
        col_in, col_snd = st.columns([5, 1])
        with col_in:
            user_in = st.text_input("AI prompt", placeholder="Ask Tommy anything...", key="chat_in", label_visibility="collapsed")
        with col_snd:
            snd = st.button("↑", key="snd")
        st.markdown('</div>', unsafe_allow_html=True)
 
    # Handle query - save to session state BEFORE clearing to avoid race condition
    query = None
    if st.session_state.pending_q:
        query = st.session_state.pending_q
        st.session_state.pending_q = None
    elif snd and user_in.strip():
        # Save the input to session state immediately so rerun doesn't lose it
        st.session_state["_pending_typed"] = user_in.strip()
    
    if "_pending_typed" in st.session_state and st.session_state["_pending_typed"]:
        query = st.session_state.pop("_pending_typed")
 
    if query:
        st.session_state.messages.append({"role":"user","content":query})
        client = get_gemini_client()
        if client:
            with st.spinner("Tommy is thinking..."):
                try:
                    # Build history for context (all previous turns)
                    history = []
                    msgs = st.session_state.messages
                    for m in msgs[:-1]:  # all except the current query
                        role = "user" if m["role"] == "user" else "model"
                        history.append({"role": role, "parts": [{"text": m["content"]}]})
                    
                    # Create fresh agent with history
                    PROMPT = (
                        "You are Tommy, a proactive Business Intelligence Agent for OlistIQ, "
                        "a leading Brazilian E-commerce analytics platform. "
                        "Be concise, data-driven, end each response with one clear recommendation. "
                        "Format currency $X,XXX. Percentages 1 decimal. Never say 'I cannot' — use tools."
                    )
                    agent = client.chats.create(
                        model="gemini-2.5-flash",
                        config=genai.types.GenerateContentConfig(
                            system_instruction=PROMPT,
                            tools=[
                                logic.get_revenue_by_range, logic.Top_selling_products,
                                logic.Detect_sales_anomalies, logic.generate_business_insights,
                                logic.compare_periods, logic.analyze_sales_performance,
                                logic.analyze_marketing_efficiency, logic.analyze_customer_loyalty,
                                logic.get_business_health_check, logic.get_quick_alerts,
                            ]
                        ),
                        history=history if history else None,
                    )
                    reply = agent.send_message(query).text
                except Exception as e:
                    reply = f"⚠️ Error: {e}"
        else:
            reply = "⚠️ GEMINI_API_KEY not found. Check your .env file."
        st.session_state.messages.append({"role":"assistant","content":reply})
        st.rerun()
