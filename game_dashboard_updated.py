
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------
# PAGE SETUP
# --------------------------
st.set_page_config(
    page_title="Roblox Game Dashboard",
    page_icon="🎮",
    layout="wide"
)

# Set style
plt.style.use('seaborn-v0_8-whitegrid')

# --------------------------
# LOAD DATA
# --------------------------
def load_data():
    df = pd.read_csv("ROBLOX_BUSINESS_DASHBOARD_FINAL.csv")
    
    # Clean MAPE for plotting
    def clean_mape(x):
        try:
            return float(str(x).replace('%', ''))
        except:
            return None
    
    df['MAPE_All_Num'] = df['MAPE_All'].apply(clean_mape)
    return df

df = load_data()

# --------------------------
# AUTOMATIC RETENTION COLUMN DETECTION
# --------------------------
retention_columns = [col for col in df.columns if 'Retention' in col or 'retention' in col]
has_retention_data = len(retention_columns) > 0

# --------------------------
# HEADER
# --------------------------
st.title("🎮 Roblox Game Portfolio Dashboard")
st.markdown("### Business-Friendly Game Prioritization")
if has_retention_data:
    st.markdown("*Recommendation score now includes retention metrics*")
st.divider()

# --------------------------
# SIDEBAR FILTERS
# --------------------------
st.sidebar.header("Filters")

# Game search
game_search = st.sidebar.text_input("Search Game Name", "")
if game_search:
    df = df[df['Game'].str.contains(game_search, case=False)]

# Tier filter
tiers = df['Business_Tier'].unique()
selected_tiers = st.sidebar.multiselect(
    "Select Business Tiers",
    options=tiers,
    default=tiers
)
df_filtered = df[df['Business_Tier'].isin(selected_tiers)]

# --------------------------
# KEY METRICS
# --------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Games", len(df_filtered))

with col2:
    tier_a = len(df_filtered[df_filtered['Business_Tier'] == 'A - HIGH POTENTIAL'])
    st.metric("Tier A Games", tier_a)

with col3:
    avg_score = df_filtered['Recommendation_Score'].mean()
    st.metric("Avg. Recommendation Score", f"{avg_score:.1f}")

with col4:
    median_mape = df_filtered['MAPE_All_Num'].median()
    st.metric("Median MAPE", f"{median_mape:.1f}%")

st.divider()

# --------------------------
# CHARTS
# --------------------------
col1, col2 = st.columns(2)

# Tier Distribution
with col1:
    st.subheader("Business Tier Distribution")
    tier_counts = df_filtered['Business_Tier'].value_counts()
    
    tier_color_map = {
        'A - HIGH POTENTIAL': '#2E8B57',
        'B - GOOD POTENTIAL': '#FFD700',
        'C - WATCH & MONITOR': '#FFA500',
        'D - LOW PRIORITY': '#DC143C'
    }
    colors = [tier_color_map[tier] for tier in tier_counts.index]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(tier_counts, labels=tier_counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
    ax.set_title("Game Distribution by Business Tier")
    st.pyplot(fig)

# Score Distribution
with col2:
    st.subheader("Recommendation Score Distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df_filtered['Recommendation_Score'], bins=20, kde=True, ax=ax, color='#4CAF50')
    ax.set_xlabel("Recommendation Score (0-100)")
    ax.set_ylabel("Number of Games")
    ax.set_title("Distribution of Recommendation Scores")
    st.pyplot(fig)

st.divider()

# Score vs MAPE
st.subheader("Recommendation Score vs Prediction Accuracy (MAPE)")
fig, ax = plt.subplots(figsize=(12, 8))
scatter = sns.scatterplot(
    data=df_filtered,
    x='Recommendation_Score',
    y='MAPE_All_Num',
    hue='Business_Tier',
    palette=tier_color_map,
    s=100,
    alpha=0.8,
    ax=ax
)
ax.set_xlabel("Recommendation Score (Higher = Better)")
ax.set_ylabel("MAPE (Lower = Better)")
ax.set_title("Higher Score = Lower Prediction Error")
plt.legend(title='Business Tier')
st.pyplot(fig)

st.divider()

# --------------------------
# DATA TABLE
# --------------------------
st.subheader("Game Portfolio Details")

columns_to_show = [
    'Game',
    'Peak_CCU',
    'Pred_Days_Available',
    'MAPE_30d',
    'Growth_Score',
    'Stability_Score',
    'Recommendation_Score',
    'Business_Tier'
] + retention_columns

df_table = df_filtered[columns_to_show]

st.dataframe(
    df_table.sort_values('Recommendation_Score', ascending=False),
    width='stretch',
    hide_index=True
)

# --------------------------
# SCORING METHODOLOGY DISPLAY
# --------------------------
st.divider()
st.subheader("Scoring Methodology")

if has_retention_data:
    st.markdown("**Recommendation Score =**")
    st.markdown("* 30% Prediction Confidence")
    st.markdown("* 30% Growth Strength")
    st.markdown("* 20% Traffic Stability")
    st.markdown(f"* 20% Retention ({', '.join(retention_columns)})")
else:
    st.markdown("**No retention data found in CSV**")
    st.markdown("**Recommendation Score =**")
    st.markdown("* 40% Prediction Confidence")
    st.markdown("* 35% Growth Strength")
    st.markdown("* 25% Traffic Stability")
