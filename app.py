import streamlit as st # type: ignore
import pandas as pd # type: ignore
from mplsoccer import VerticalPitch,Pitch, Sbopen # type: ignore
import matplotlib.pyplot as plt # type: ignore
from utils.data_prep import get_tournament_data,team_of_the_tournament,preprocess_data
from utils.attackstats import most_goals,most_assist,most_successful_dribbles,most_successful_passes
from utils.defensestats import most_blocks,most_clearance,most_interceptions,most_tackels_won
from utils.goalkeepingstats import save_percentage,most_clean_sheets,most_saves
from utils.charts import most_dangerous_attacking_players,plot_shots,passes_assisted_shot,plot_xg_vs_goals,shot_accuracy,plot_possession_share,create_attacker_radar,fouls_and_cards,pressing_zones,duels_won_percent,most_dangerous_defensive_players,create_def_radar,create_gk_radar

# ======================= PAGE CONFIGURATION =======================
st.set_page_config(
    page_title="Euro 2024 Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================= CUSTOM CSS STYLING =======================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* ========== GLOBAL STYLES ========== */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #fafafa 0%, #f4f4f5 100%);
        min-height: 100vh;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container */
    .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* ========== HEADER STYLING ========== */
    .main-header {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(79, 70, 229, 0.25);
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-title {
        color: #ffffff;
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .main-subtitle {
        color: #e0e7ff;
        font-size: 1.3rem;
        font-weight: 400;
        margin-top: 0.75rem;
        opacity: 0.95;
        letter-spacing: 0.01em;
    }
    
    /* ========== CARD STYLING ========== */
    .stat-card {
        background: #ffffff;
        border: 1px solid #e4e4e7;
        border-radius: 16px;
        padding: 1.75rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4f46e5, #06b6d4);
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 35px rgba(79, 70, 229, 0.15);
        border-color: #4f46e5;
    }
    
    .stat-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #71717a;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    .stat-value {
        font-size: 2.25rem;
        font-weight: 800;
        color: #4f46e5;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .stat-player {
        font-size: 1.125rem;
        font-weight: 600;
        color: #18181b;
        margin: 0.75rem 0;
        line-height: 1.4;
    }
    
    .stat-team {
        font-size: 0.9375rem;
        color: #71717a;
        font-weight: 500;
    }
    
    /* ========== AWARD CARDS ========== */
    .award-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
        border-radius: 20px;
        padding: 2rem;
        margin: 0.75rem 0;
        box-shadow: 0 8px 30px rgba(245, 158, 11, 0.25);
        text-align: center;
        color: #18181b;
        position: relative;
        overflow: hidden;
    }
    
    .award-card::before {
        content: '🏆';
        position: absolute;
        top: -15px;
        right: -15px;
        font-size: 5rem;
        opacity: 0.15;
    }
    
    .award-title {
        font-size: 1.125rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #92400e;
    }
    
    .award-player {
        font-size: 1.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
        color: #18181b;
    }
    
    /* ========== SECTION HEADERS ========== */
    .section-header {
        background: linear-gradient(135deg, #18181b 0%, #27272a 100%);
        color: white;
        padding: 1.75rem;
        border-radius: 16px;
        margin: 2.5rem 0 1.5rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(24, 24, 27, 0.2);
        border: 1px solid #3f3f46;
    }
    
    .section-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.01em;
    }
    
    .section-subtitle {
        font-size: 1.0625rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        color: #d4d4d8;
    }
    
    /* ========== TAB STYLING ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: #fafafa;
        padding: 0.75rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #e4e4e7;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border-radius: 10px;
        padding: 1rem 1.75rem;
        font-weight: 600;
        font-size: 1rem;
        color: #52525b;
        border: 2px solid transparent;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f4f4f5;
        border-color: #4f46e5;
        color: #4f46e5;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border-color: #4f46e5 !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    /* ========== CHART CONTAINER ========== */
    .chart-container {
        background: #ffffff;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        margin: 1.5rem 0;
        border: 1px solid #e4e4e7;
    }
    
    .chart-title {
        font-size: 1.375rem;
        font-weight: 700;
        color: #18181b;
        margin-bottom: 1.5rem;
        text-align: center;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f4f4f5;
        letter-spacing: -0.01em;
    }
    
    /* ========== SELECTBOX STYLING (CRITICAL FIX) ========== */
    
    /* Label above selectbox */
    div[data-testid="stSelectbox"] label,
    .stSelectbox label {
        font-size: 1.0625rem !important;
        font-weight: 600 !important;
        color: #18181b !important;
        margin-bottom: 0.75rem !important;
        letter-spacing: 0.01em !important;
    }
    
    /* Main selectbox container */
    div[data-testid="stSelectbox"] > div > div,
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 2px solid #d4d4d8 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }
    
    /* Selectbox on hover */
    div[data-testid="stSelectbox"] > div > div:hover,
    .stSelectbox > div > div:hover {
        border-color: #4f46e5 !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
    }
    
    /* Text inside selectbox */
    div[data-testid="stSelectbox"] input,
    .stSelectbox input {
        color: #18181b !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    /* Selectbox display value */
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #18181b !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    /* Dropdown arrow */
    div[data-testid="stSelectbox"] svg,
    .stSelectbox svg {
        fill: #18181b !important;
    }
    
    /* Focus state */
    div[data-testid="stSelectbox"] [data-baseweb="select"]:focus-within,
    .stSelectbox [data-baseweb="select"]:focus-within {
        border-color: #4f46e5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
    }
    
    /* Dropdown menu */
    ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 2px solid #e4e4e7 !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15) !important;
        padding: 0.5rem !important;
    }
    
    /* Dropdown menu items */
    ul[role="listbox"] li {
        color: #18181b !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        padding: 0.875rem 1rem !important;
        border-radius: 8px !important;
        margin: 0.25rem 0 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Dropdown menu items on hover */
    ul[role="listbox"] li:hover {
        background-color: #f4f4f5 !important;
        color: #4f46e5 !important;
    }
    
    /* Selected item in dropdown */
    ul[role="listbox"] li[aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* ========== HEADERS STYLING ========== */
    h1 {
        color: #18181b !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -0.02em !important;
    }
    
    h2 {
        color: #18181b !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        letter-spacing: -0.01em !important;
    }
    
    h3 {
        color: #27272a !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* ========== DIVIDER STYLING ========== */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #4f46e5, #06b6d4, transparent);
        margin: 3rem 0;
        opacity: 0.6;
    }
    
    /* ========== SIDEBAR STYLING ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fafafa 0%, #f4f4f5 100%);
        padding: 2rem 1.5rem;
        border-right: 1px solid #e4e4e7;
    }
    
    [data-testid="stSidebar"] h1 {
        font-size: 1.5rem !important;
        color: #18181b !important;
        border-bottom: 2px solid #4f46e5;
        padding-bottom: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    /* ========== METRIC STYLING ========== */
    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #e4e4e7;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    
    [data-testid="stMetric"] label {
        color: #71717a !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #4f46e5 !important;
        font-weight: 700 !important;
    }
    
    /* ========== BUTTON STYLING ========== */
    .stButton button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4);
    }
    
    /* ========== INFO/WARNING/ERROR BOXES ========== */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
    }
    
    /* Info boxes */
    [data-baseweb="notification"][kind="info"] {
        background-color: #dbeafe !important;
        border-left-color: #3b82f6 !important;
    }
    
    /* Success boxes */
    [data-baseweb="notification"][kind="success"] {
        background-color: #d1fae5 !important;
        border-left-color: #10b981 !important;
    }
    
    /* Warning boxes */
    [data-baseweb="notification"][kind="warning"] {
        background-color: #fef3c7 !important;
        border-left-color: #f59e0b !important;
    }
    
    /* Error boxes */
    [data-baseweb="notification"][kind="error"] {
        background-color: #fee2e2 !important;
        border-left-color: #ef4444 !important;
    }
    
    /* ========== RESPONSIVE DESIGN ========== */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        .main-subtitle {
            font-size: 1.125rem;
        }
        .stat-card {
            margin: 0.5rem 0;
            padding: 1.25rem;
        }
        .block-container {
            padding: 1.5rem 1rem;
        }
        h1 {
            font-size: 2rem !important;
        }
        h2 {
            font-size: 1.5rem !important;
        }
    }
    
    /* ========== SCROLLBAR STYLING ========== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f4f4f5;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #4f46e5, #6366f1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #4338ca, #4f46e5);
    }
</style>
""", unsafe_allow_html=True)

# ======================= HEADER SECTION =======================
st.markdown("""
<div class="main-header">
    <h1 class="main-title">⚽ Euro 2024 Analytics Dashboard</h1>
    <p class="main-subtitle">Comprehensive Tournament Analysis & Player Statistics</p>
</div>
""", unsafe_allow_html=True)

# ======================= DATA LOADING =======================
@st.cache_data
def load_tournament_data():
    return get_tournament_data(competition_id=55, season_id=282)

euro_df = load_tournament_data()

@st.cache_data
def get_all_stats(df):
    return {
        "attack": {
            "Most Goals": most_goals(df),
            "Most Assists": most_assist(df),
            "Most Successful Passes": most_successful_passes(df),
            "Most Successful Dribbles": most_successful_dribbles(df)
        },
        "defense": {
            "Most Tackles": most_tackels_won(df),
            "Most Blocks": most_blocks(df),
            "Most Clearance": most_clearance(df),
            "Most Interceptions": most_interceptions(df)
        },
        "goalkeeping_stats": {
            "Most Clean Sheets": most_clean_sheets(df),
            "Most Saves": most_saves(df),
            "Highest Save %": save_percentage(df)
        }
    }

all_stats = get_all_stats(euro_df)
attack_stats = all_stats["attack"]
defense_stats = all_stats["defense"]
goalkeeping_stats = all_stats["goalkeeping_stats"]

# ======================= TEAM LOGOS =======================
team_logos = {
    "Albania": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Albania.png",
    "Austria": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Austria.png",
    "Belgium": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Belgium.png",
    "Croatia": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Croatia.png",
    "Czech_Republic": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Czech_Republic.png",
    "Denmark": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Denmark.png",
    "England": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/England.png",
    "France": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/France.png",
    "Georgia": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Georgia.png",
    "Germany": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Germany.png",
    "Hungary": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Hungary.png",
    "Italy": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Italy.png",
    "Netherlands": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Netherlands.png",
    "Poland": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Poland.png",
    "Portugal": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Portugal.png",
    "Romania": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Romania.png",
    "Scotland": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Scotland.png",
    "Serbia": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Serbia.png",
    "Slovakia": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Slovakia.png",
    "Slovenia": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Slovenia.png",
    "Spain": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Spain.png",
    "Switzerland": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Switzerland.png",
    "Turkey": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Turkey.png",
    "Ukraine": "https://raw.githubusercontent.com/DhavalPatel511/Euro_2024/main/flags/Ukraine.png"
}

@st.cache_data
def best_performers():
    return {
        "Player of the Tournament": {"player": "Rodri", "team": "Spain"},
        "Young Player of the Tournament": {"player": "Lamine Yamal", "team": "Spain"},
        "Golden Glove": {"player": "Mike Maignan", "team": "France"}
    }

expanded_stats = {
    "Player of the Tournament": {
        "Minutes played": "521", "Goals": "1", "Assists": "0", 
        "Passes attempted": "439", "Passes completed": "411", "Passing accuracy": "92.84%"
    },
    "Young Player of the Tournament": {"Minutes played": "507", "Goals": "1", "Assists": "4"},
    "Golden Glove": {"Clean Sheets": "4"}
}

performers = best_performers()

# ======================= TOURNAMENT AWARDS SECTION =======================
def display_tournament_awards(stats):
    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">🏆 Tournament Awards</h2>
        <p class="section-subtitle">Recognizing the standout performers of Euro 2024</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]

    for idx, (award_name, award_data) in enumerate(stats.items()):
        player = award_data['player']
        team = award_data['team']
        team_logo = team_logos.get(team, "")

        with columns[idx]:
            st.markdown(f"""
            <div class="award-card">
                <div class="award-title">{award_name}</div>
                <div class="award-player">{player}</div>
                {f'<img src="{team_logo}" width="50" style="margin: 10px 0;">' if team_logo else ""}
                <div style="font-weight: 600; font-size: 1rem;">{team}</div>
            </div>
            """, unsafe_allow_html=True)

    # Detailed stats in expandable sections
    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]
    
    for idx, (award_name, _) in enumerate(stats.items()):
        with columns[idx]:
            if award_name in expanded_stats:
                with st.expander(f"📊 {award_name} Stats", expanded=False):
                    for stat, value in expanded_stats[award_name].items():
                        st.markdown(f"**{stat}:** {value}")

display_tournament_awards(performers)

# ======================= STATISTICS SECTIONS =======================
def display_stats_section(title, emoji, stats, description):
    st.markdown(f"""
    <div class="section-header">
        <h2 class="section-title">{emoji} {title}</h2>
        <p class="section-subtitle">{description}</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns([1, 1, 1])
    
    for idx, (stat_name, stat_data) in enumerate(stats.items()):
        team = stat_data["team"]
        player = stat_data["player"]
        
        # Determine value and label
        value_mapping = {
            "goals_scored": ("Goals", "goals_scored"),
            "assists": ("Assists", "assists"),
            "total_passes": ("Passes", "total_passes"),
            "dribbles": ("Dribbles", "dribbles"),
            "tackles": ("Tackles", "tackles"),
            "blocks": ("Blocks", "blocks"),
            "clearances": ("Clearances", "clearances"),
            "interceptions": ("Interceptions", "interceptions"),
            "clean_sheets": ("Clean Sheets", "clean_sheets"),
            "saves": ("Saves", "saves"),
            "save_percent": ("Save %", "save_percent")
        }
        
        value_label = ""
        value = ""
        for key, (label, data_key) in value_mapping.items():
            if data_key in stat_data:
                value_label = label
                if data_key == "save_percent":
                    value = f"{stat_data[data_key]:.1f}%"
                else:
                    value = str(stat_data[data_key])
                break
        
        team_logo = team_logos.get(team, "")
        
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-title">{stat_name}</div>
                <div class="stat-value">{value}</div>
                <div class="stat-player">{player}</div>
                {f'<img src="{team_logo}" width="40" style="margin: 8px 0;">' if team_logo else ""}
                <div class="stat-team">{team}</div>
            </div>
            """, unsafe_allow_html=True)

# Display all statistics sections
display_stats_section(
    "Attack Statistics", "⚽", attack_stats,
    "Leading goal scorers, assist providers, and creative players of the tournament"
)

display_stats_section(
    "Defense Statistics", "🛡️", defense_stats,
    "Top defensive performers including tackles, blocks, and interceptions"
)

display_stats_section(
    "Goalkeeping Statistics", "🧤", goalkeeping_stats,
    "Outstanding goalkeeper performances measured by saves and clean sheets"
)

# ======================= TEAM OF THE TOURNAMENT =======================
st.markdown("""
<div class="section-header">
    <h2 class="section-title">🌟 Team of the Tournament</h2>
    <p class="section-subtitle">The best XI players based on their overall performance</p>
</div>
""", unsafe_allow_html=True)
tott = team_of_the_tournament()
col1, col2, col3 = st.columns([0.5,2,0.5])
with col2:
    st.pyplot(tott)


# ======================= DETAILED ANALYSIS TABS =======================
att_list, def_list, gk_list = preprocess_data(euro_df)

st.markdown("""
<div class="section-header" style="margin-top: 3rem;">
    <h2 class="section-title">📊 Detailed Team Analysis</h2>
    <p class="section-subtitle">In-depth performance analysis across attacking, defensive, and goalkeeping metrics</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["⚽ Attacking Analysis", "🛡️ Defensive Analysis", "🧤 Goalkeeping Analysis"])

# ======================= ATTACKING ANALYSIS TAB =======================
with tab1:
    st.markdown("### Team Selection")
    selected_team = st.selectbox(
        "Choose a team to analyze",
        euro_df['team_name'].sort_values().unique(),
        index=0,
        key="att_team"
    )
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
        <h3 style="color: #2e7d32; margin: 0;">🎯 {selected_team} - Attacking Analysis</h3>
        <p style="color: #388e3c; margin: 0.5rem 0 0 0;">
            Explore key attacking metrics including progressive passes, shot accuracy, goal contributions, and xG analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Generate charts
    top_attacking_players = most_dangerous_attacking_players(euro_df, selected_team)
    xg_vs_goals_fig = plot_xg_vs_goals(euro_df, selected_team)
    shots_fig = plot_shots(euro_df, selected_team)
    pass_fig = passes_assisted_shot(euro_df, selected_team)
    poss_fig = plot_possession_share(euro_df, selected_team)
    shot_acc_fig = shot_accuracy(euro_df, selected_team)

    with col1:
        st.markdown('<div class="chart-container"><div class="chart-title">🎯 Top Goal Contributors</div>', unsafe_allow_html=True)
        st.pyplot(top_attacking_players)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container"><div class="chart-title">📈 xG vs. Actual Goals</div>', unsafe_allow_html=True)
        st.pyplot(xg_vs_goals_fig)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container"><div class="chart-title">🎯 Shot Accuracy</div>', unsafe_allow_html=True)
        st.pyplot(shot_acc_fig)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container"><div class="chart-title">🗺️ Team Shot Map</div>', unsafe_allow_html=True)
        st.pyplot(shots_fig)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container"><div class="chart-title">🔑 Key Passes Leading to Goals</div>', unsafe_allow_html=True)
        st.pyplot(pass_fig)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container"><div class="chart-title">⚽ Team Possession Share</div>', unsafe_allow_html=True)
        st.pyplot(poss_fig)
        st.markdown('</div>', unsafe_allow_html=True)

    # Player comparison
    st.markdown("---")
    st.markdown("### 🔄 Player Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox("Select first player", att_list, index=0, key="att_p1")
    with col2:
        player2_options = [player for player in att_list if player != player1]
        player2 = st.selectbox("Select second player", player2_options, index=0, key="att_p2")
    
    player_data = euro_df[euro_df['player_name'].isin([player1, player2])]
    att_radar = create_attacker_radar(player_data, player1, player2)
    
    st.markdown('<div class="chart-container"><div class="chart-title">📊 Attacking Performance Comparison</div>', unsafe_allow_html=True)
    st.pyplot(att_radar)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================= DEFENSIVE ANALYSIS TAB =======================
with tab2:
    st.markdown("### Team Selection")
    selected_team = st.selectbox(
        "Choose a team to analyze",
        euro_df['team_name'].sort_values().unique(),
        index=0,
        key="def_team"
    )
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
        <h3 style="color: #1565c0; margin: 0;">🛡️ {selected_team} - Defensive Analysis</h3>
        <p style="color: #1976d2; margin: 0.5rem 0 0 0;">
            Understanding key defensive metrics like tackles, interceptions, clearances and overall defensive solidity
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Generate charts
    cards_fig = fouls_and_cards(euro_df, selected_team)
    pressing_fig = pressing_zones(euro_df, selected_team)
    duels_fig = duels_won_percent(euro_df, selected_team)
    defensive_player = most_dangerous_defensive_players(euro_df, selected_team)

    with col1:
        st.markdown('<div class="chart-container"><div class="chart-title">🏆 Top Defensive Players</div>', unsafe_allow_html=True)
        st.pyplot(defensive_player)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container"><div class="chart-title">⚠️ Fouls and Cards</div>', unsafe_allow_html=True)
        st.pyplot(cards_fig)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container"><div class="chart-title">💪 Duels Won (Aerial & Ground)</div>', unsafe_allow_html=True)
        st.pyplot(duels_fig)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container"><div class="chart-title">🔥 Pressing Zones</div>', unsafe_allow_html=True)
        st.pyplot(pressing_fig)
        st.markdown('</div>', unsafe_allow_html=True)

    # Player comparison
    st.markdown("---")
    st.markdown("### 🔄 Player Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox("Select first player", def_list, index=0, key="def_p1")
    with col2:
        player2_options = [player for player in def_list if player != player1]
        player2 = st.selectbox("Select second player", player2_options, index=0, key="def_p2")
    
    player_data = euro_df[euro_df['player_name'].isin([player1, player2])]
    def_radar = create_def_radar(player_data, player1, player2)
    
    st.markdown('<div class="chart-container"><div class="chart-title">📊 Defensive Performance Comparison</div>', unsafe_allow_html=True)
    st.pyplot(def_radar)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================= GOALKEEPING ANALYSIS TAB =======================
with tab3:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #fff3e0 0%, #fce4ec 100%); 
                padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
        <h3 style="color: #e65100; margin: 0;">🧤 Goalkeeper Performance Analysis</h3>
        <p style="color: #f57c00; margin: 0.5rem 0 0 0;">
            Comprehensive analysis of goalkeeper performances based on saves, clean sheets, and save percentage
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Player comparison
    st.markdown("### 🔄 Goalkeeper Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox("Select first goalkeeper", gk_list, index=0, key="gk_p1")
    with col2:
        player2_options = [player for player in gk_list if player != player1]
        player2 = st.selectbox("Select second goalkeeper", player2_options, index=0, key="gk_p2")
    
    player_data = euro_df[euro_df['player_name'].isin([player1, player2])]
    gk_radar = create_gk_radar(player_data, player1, player2)
    
    st.markdown('<div class="chart-container"><div class="chart-title">📊 Goalkeeper Performance Comparison</div>', unsafe_allow_html=True)
    st.pyplot(gk_radar)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================= FOOTER =======================
st.markdown("""
---
<div style="text-align: center; padding: 2rem; color: #666; font-style: italic;">
    <p>⚽ Euro 2024 Analytics Dashboard | Data-driven insights into European football excellence</p>
    <p style="font-size: 0.9rem; margin-top: 1rem;">
        Built with Streamlit • Data powered by StatsBomb • Analysis by Football Analytics Team
    </p>
</div>
""", unsafe_allow_html=True)