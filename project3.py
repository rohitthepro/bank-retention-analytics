import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Bank Customer Retention Strategy",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# UNIVERSAL CSS: Adapts to Day/Dark mode, keeps the sidebar blue, and ensures ALL text is visible
st.markdown("""
    <style>
    /* Hide default Streamlit menus */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Global Font applied ONLY to text elements */
    html, body, .stMarkdown, div, h1, h2, h3, h4, h5, h6, p, label {
        font-family: 'Georgia', serif !important;
    }

    /* SIDEBAR STYLING: Force Blue Gradient & Legible Elements */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1A365D 0%, #2B6CB0 100%) !important;
    }
    
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] label p,
    [data-testid="stSidebar"] .stMarkdown p {
        color: #FFFFFF !important;
    }

    /* FOOLPROOF INPUT FIXES FOR LIGHT/DARK MODE */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #F7FAFC !important;
        border: 2px solid #CBD5E0 !important;
    }
    [data-testid="stSidebar"] .stButton > button * {
        color: #1A365D !important;
        font-weight: 900 !important;
    }
    
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #F7FAFC !important;
        color: #1A365D !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #1A365D !important;
        font-weight: bold !important;
    }

    /* Bulletproof fix for the Collapse/Expand Arrow Button */
    [data-testid="collapsedControl"] button, 
    [data-testid="stSidebarCollapseButton"] button {
        background-color: rgba(26, 54, 93, 0.4) !important; 
        border-radius: 4px !important;
    }
    [data-testid="collapsedControl"] svg, 
    [data-testid="stSidebarCollapseButton"] svg,
    button[kind="header"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
    }

    /* Style Metric Cards with a clean, adaptive border */
    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3182CE;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    [data-testid="stMetricLabel"] { font-size: 14px !important; font-weight: 800 !important; }
    [data-testid="stMetricValue"] { font-size: 32px !important; font-weight: 900 !important; }

    /* Custom Insight Cards with high-contrast Navy/Blue gradient */
    .insight-card {
        background: linear-gradient(135deg, #1A365D 0%, #2B6CB0 100%);
        color: #FFFFFF;
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        border-left: 6px solid #63B3ED;
    }
    .insight-card h4 {
        color: #FFFFFF !important;
        margin-top: 0;
        margin-bottom: 8px;
        font-size: 16px !important;
        font-weight: bold;
        text-transform: uppercase;
        border-bottom: 1px solid rgba(255,255,255,0.2);
        padding-bottom: 4px;
    }
    .insight-card p {
        color: #F7FAFC !important;
        margin: 0;
        font-size: 14px !important;
        line-height: 1.5;
    }
    .alert-stat { color: #FEB2B2; font-weight: bold; font-size: 1.1em; }
    .highlight-stat { color: #9AE6B4; font-weight: bold; font-size: 1.1em; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_engineer_data():
    df = pd.read_csv('European_Bank.csv')
    
    # 1. Engagement Classification Profiles
    conditions = [
        (df['IsActiveMember'] == 1) & (df['NumOfProducts'] >= 2),
        (df['IsActiveMember'] == 1) & (df['NumOfProducts'] == 1),
        (df['IsActiveMember'] == 0) & (df['Balance'] > df['Balance'].median()),
        (df['IsActiveMember'] == 0) & (df['Balance'] <= df['Balance'].median())
    ]
    choices = ['Highly Engaged (Active, Multi-Product)', 'Active, Single-Product', 'Premium Disengaged (Inactive, High Balance)', 'Low Engagement (Inactive, Low Balance)']
    df['Engagement_Profile'] = np.select(conditions, choices, default='Other')
    
    # 2. Relationship Strength Index (RSI - Scored out of 100)
    # Active: 40pts | Credit Card: 10pts | Tenure: up to 20pts | Products (Ideal=2): up to 30pts
    df['RSI_Active'] = df['IsActiveMember'] * 40
    df['RSI_Card'] = df['HasCrCard'] * 10
    df['RSI_Tenure'] = (df['Tenure'] / df['Tenure'].max()) * 20
    df['RSI_Products'] = df['NumOfProducts'].map({1: 15, 2: 30, 3: 5, 4: 0}) # 2 products is the sticky sweet-spot
    df['Relationship_Strength_Index'] = df['RSI_Active'] + df['RSI_Card'] + df['RSI_Tenure'] + df['RSI_Products']
    
    return df

df = load_and_engineer_data()

# TRANSPARENT CHART THEME (Adapts perfectly to Day/Dark mode)
def style_chart(fig, title_text, height=350):
    fig.update_layout(
        title=dict(text=f"<b>{title_text}</b>", x=0.02, y=0.95, font=dict(size=18)),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=40, l=40, r=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=height,
        hovermode="x unified"
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)', zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)', zeroline=False)
    return fig

# --- SIDEBAR CONTROL PANEL ---
default_geo = df['Geography'].unique().tolist()

def reset_filters():
    st.session_state['geo_filter'] = default_geo
    st.session_state['status_filter'] = "All"
    st.session_state['balance_filter'] = 0

with st.sidebar:
    st.markdown("<h2 style='text-align: center; font-weight: 900; font-size: 24px;'>CONTROL PANEL</h2>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.button("🔄 Reset View", use_container_width=True, on_click=reset_filters)
    st.markdown("<br>", unsafe_allow_html=True)
        
    geo_filter = st.multiselect(
        "🌍 Geography", 
        options=default_geo, 
        default=default_geo,
        key="geo_filter"
    )
    
    status_filter = st.selectbox(
        "⚡ Activity Status", 
        options=["All", "Active", "Inactive"],
        key="status_filter"
    )
    
    min_balance = st.slider(
        "💰 Minimum Balance Requirement", 
        min_value=0, 
        max_value=int(df['Balance'].max()), 
        step=10000, 
        value=0,
        key="balance_filter"
    )

# Filter Application
filtered_df = df[df['Geography'].isin(geo_filter)]
if status_filter == "Active":
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 1]
elif status_filter == "Inactive":
    filtered_df = filtered_df[filtered_df['IsActiveMember'] == 0]
filtered_df = filtered_df[filtered_df['Balance'] >= min_balance]

if filtered_df.empty:
    st.warning("No records match the selected filters. Please adjust the sidebar controls.")
    st.stop()

# --- HEADER & METHODOLOGY ---
st.markdown("<h1 style='text-align: center; font-weight: 900; font-size: 38px; line-height: 1.2; margin-bottom: 15px;'>CUSTOMER ENGAGEMENT & PRODUCT RETENTION STRATEGY</h1>", unsafe_allow_html=True)

with st.expander("ℹ️ Analytical Methodology & Project KPIs (Unified Mentor)", expanded=False):
    st.markdown("""
    **Core Strategy:** Shifting retention analysis from pure demographics to behavioral relationship strength.
    *   **Engagement Retention Ratio:** Compares the churn probability of inactive users versus active users.
    *   **Product Depth Index:** Identifies the structural "sweet spot" of product utilization (e.g., 2 products) vs. the flight risk of 3+ products.
    *   **Relationship Strength Index (RSI):** A proprietary 100-point composite score weighting Active Status (40), Product Depth (30), Tenure (20), and Card Ownership (10).
    """)

st.markdown("<hr>", unsafe_allow_html=True)

# --- KPI METRICS CALCULATION ---
total_customers = len(filtered_df)
overall_churn = filtered_df['Exited'].mean()

active_churn = filtered_df[filtered_df['IsActiveMember'] == 1]['Exited'].mean()
inactive_churn = filtered_df[filtered_df['IsActiveMember'] == 0]['Exited'].mean()
engagement_ratio = inactive_churn / active_churn if active_churn > 0 else 0

prod_churn = filtered_df.groupby('NumOfProducts')['Exited'].mean()
optimal_prod_retention = 1 - prod_churn.get(2, 0) # Retention rate for 2 products

premium_disengaged_churn = filtered_df[(filtered_df['IsActiveMember'] == 0) & (filtered_df['Balance'] > filtered_df['Balance'].median())]['Exited'].mean()

avg_rsi = filtered_df['Relationship_Strength_Index'].mean()

# --- KPI LAYOUT ---
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1: st.metric("TOTAL TARGET SEGMENT", f"{total_customers:,}")
with k2: st.metric("SEGMENT CHURN RATE", f"{overall_churn * 100:.1f}%")
with k3: st.metric("ENGAGEMENT RETENTION RATIO", f"{engagement_ratio:.1f}x", help="Inactive users churn at this multiple compared to active users.")
with k4: st.metric("OPTIMAL PRODUCT RETENTION", f"{optimal_prod_retention * 100:.1f}%", help="Retention rate of customers holding exactly 2 products (the structural sweet spot).")
with k5: st.metric("PREMIUM DISENGAGED CHURN", f"{premium_disengaged_churn * 100:.1f}%", help="Churn rate of inactive customers holding above-average balances.")
with k6: st.metric("AVG RELATIONSHIP STRENGTH", f"{avg_rsi:.1f} / 100")

st.markdown("<hr>", unsafe_allow_html=True)

# --- CHARTS & INSIGHTS ---
charts_col, insights_col = st.columns([3.2, 1], gap="large")

with charts_col:
    row1_c1, row1_c2 = st.columns(2)
    
    with row1_c1:
        # 1. Product Depth vs Churn Risk
        prod_data = filtered_df.groupby('NumOfProducts')['Exited'].mean().reset_index()
        fig_prod = px.bar(prod_data, x='NumOfProducts', y='Exited', text=prod_data['Exited'].apply(lambda x: f"{x*100:.1f}%"),
                          color='Exited', color_continuous_scale=['#38A169', '#E53E3E'])
        fig_prod = style_chart(fig_prod, "Flight Risk by Product Depth")
        fig_prod.update_layout(xaxis_title="Number of Products Held", yaxis_title="Churn Probability", coloraxis_showscale=False)
        st.plotly_chart(fig_prod, use_container_width=True)

    with row1_c2:
        # 2. Premium Disengaged Detector
        inactive_premium = df[(df['IsActiveMember'] == 0) & (df['Balance'] > 0)]
        fig_scatter = px.scatter(inactive_premium, x='EstimatedSalary', y='Balance', color=inactive_premium['Exited'].astype(str),
                                 color_discrete_map={"0": "rgba(49, 130, 206, 0.4)", "1": "#E53E3E"}, opacity=0.7)
        fig_scatter = style_chart(fig_scatter, "Premium Disengaged Flight Risk")
        fig_scatter.update_layout(xaxis_title="Estimated Salary", yaxis_title="Account Balance", legend_title="Churned (1=Yes)")
        st.plotly_chart(fig_scatter, use_container_width=True)

    row2_c1, row2_c2 = st.columns(2)
    
    with row2_c1:
        # 3. RSI Distribution
        fig_rsi = px.histogram(filtered_df, x="Relationship_Strength_Index", color="Exited", barmode="overlay",
                               color_discrete_map={0: "#38A169", 1: "#E53E3E"}, opacity=0.7, nbins=20)
        fig_rsi = style_chart(fig_rsi, "Relationship Strength Index (RSI) Distribution")
        fig_rsi.update_layout(xaxis_title="RSI Score (0-100)", yaxis_title="Number of Customers", legend_title="Exited")
        st.plotly_chart(fig_rsi, use_container_width=True)

    with row2_c2:
        # 4. Engagement Profile Churn
        eng_data = filtered_df.groupby('Engagement_Profile')['Exited'].mean().reset_index().sort_values('Exited')
        fig_eng = px.bar(eng_data, y='Engagement_Profile', x='Exited', orientation='h',
                         text=eng_data['Exited'].apply(lambda x: f"{x*100:.1f}%"), color='Exited', color_continuous_scale=['#3182CE', '#E53E3E'])
        fig_eng = style_chart(fig_eng, "Churn Risk by Engagement Profile")
        fig_eng.update_layout(xaxis_title="Churn Rate", yaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(fig_eng, use_container_width=True)

with insights_col:
    st.markdown("<h3 style='font-weight: 900; font-size: 20px; margin-top: 15px;'>STRATEGIC INSIGHTS</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 0px; margin-bottom: 15px;'>", unsafe_allow_html=True)
    
    ch_1prod = prod_data[prod_data['NumOfProducts']==1]['Exited'].values[0]*100 if 1 in prod_data['NumOfProducts'].values else 0
    ch_2prod = prod_data[prod_data['NumOfProducts']==2]['Exited'].values[0]*100 if 2 in prod_data['NumOfProducts'].values else 0
    ch_3prod = prod_data[prod_data['NumOfProducts']==3]['Exited'].values[0]*100 if 3 in prod_data['NumOfProducts'].values else 0

    st.markdown(f"""
        <div class='insight-card'>
            <h4>⚖️ The "2-Product" Sweet Spot</h4>
            <p>Customers with 1 product churn at <span class='alert-stat'>{ch_1prod:.1f}%</span>. Cross-selling a 2nd product dramatically boosts retention, lowering churn to <span class='highlight-stat'>{ch_2prod:.1f}%</span>.</p>
        </div>
        
        <div class='insight-card'>
            <h4>🚨 Over-Selling Flight Risk</h4>
            <p>Aggressive cross-selling causes friction. Customers pushed into holding 3 products experience a massive churn spike of <span class='alert-stat'>{ch_3prod:.1f}%</span>.</p>
        </div>
        
        <div class='insight-card'>
            <h4>💸 Premium Silent Churn</h4>
            <p>The Premium Disengaged segment (inactive but holding high balances) represents a severe capital flight risk. High balances alone <b>do not</b> guarantee loyalty without regular engagement.</p>
        </div>
        
        <div class='insight-card' style='border: 1px solid rgba(255,255,255,0.2); border-left: 6px solid #805AD5;'>
            <h4 style='color: #D6BCFA !important;'>🎯 Action Plan for Unified Mentor</h4>
            <p><b>1. Targeted Cross-Sell:</b> Shift single-product customers to 2 products, but explicitly avoid pushing them into 3+ tiers.</p>
            <p style='margin-top: 8px;'><b>2. VIP Re-engagement:</b> Trigger automated VIP check-in calls for customers who drop below a <b>40-point RSI</b> while holding above-median balances.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    import sys
    import streamlit as st
    from streamlit.web import cli as stcli

    if not st.runtime.exists():
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())