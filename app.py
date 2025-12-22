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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        text-align: center;
    }
    
    .main-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        color: #e3f2fd;
        font-size: 1.3rem;
        font-weight: 400;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Card Styling */
    .stat-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: none;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
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
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    .stat-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #37474f;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1565c0;
        margin: 0.5rem 0;
    }
    
    .stat-player {
        font-size: 1.1rem;
        font-weight: 600;
        color: #263238;
        margin: 0.5rem 0;
    }
    
    .stat-team {
        font-size: 0.9rem;
        color: #546e7a;
        font-weight: 500;
    }
    
    /* Award Cards */
    .award-card {
        background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 0.5rem 0;
        box-shadow: 0 10px 30px rgba(255,193,7,0.3);
        text-align: center;
        color: #1a1a1a;
        position: relative;
        overflow: hidden;
    }
    
    .award-card::before {
        content: '🏆';
        position: absolute;
        top: -10px;
        right: -10px;
        font-size: 4rem;
        opacity: 0.1;
    }
    
    .award-title {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .award-player {
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #37474f 0%, #546e7a 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0 1rem 0;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .section-title {
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
    }
    
    .section-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px;
        padding: 1rem 2rem;
        font-weight: 600;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #e3f2fd;
        border-color: #1976d2;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
        color: white !important;
    }
    
    /* Chart Container */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .chart-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #37474f;
        margin-bottom: 1rem;
        text-align: center;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    /* Selectbox Styling */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        font-weight: 500;
    }
    
    /* Divider Styling */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 3rem 0;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        .main-subtitle {
            font-size: 1.1rem;
        }
        .stat-card {
            margin: 0.3rem 0;
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ======================= HEADER SECTION =======================
st.markdown("""
<div class="main-header">
    <h1 class="main-title">⚽ Euro 2024 Analytics Dashboard</h1>
    <p class="main-subtitle">Comprehensive statistical analysis of Europe's premier football tournament</p>
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
    "Albania": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Albania.png",
    "Austria": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Austria.png",
    "Belgium": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Belgium.png",
    "Croatia": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Croatia.png",
    "Czech_Republic": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Czech_Republic.png",
    "Denmark": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Denmark.png",
    "England": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/England.png",
    "France": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/France.png",
    "Georgia": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Georgia.png",
    "Germany": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Germany.png",
    "Hungary": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Hungary.png",
    "Italy": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Italy.png",
    "Netherlands": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Netherlands.png",
    "Poland": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Poland.png",
    "Portugal": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Portugal.png",
    "Romania": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Romania.png",
    "Scotland": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Scotland.png",
    "Serbia": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Serbia.png",
    "Slovakia": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Slovakia.png",
    "Slovenia": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Slovenia.png",
    "Spain": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Spain.png",
    "Switzerland": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Switzerland.png",
    "Turkey": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Turkey.png",
    "Ukraine": "https://raw.githubusercontent.com/DhavalPatel511/Streamlit_app/main/flags/Ukraine.png"
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
with st.container():
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.pyplot(tott)
    st.markdown('</div>', unsafe_allow_html=True)

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