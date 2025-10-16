import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Tweet Analytics - Service Client",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1DA1F2;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1DA1F2;
    }
    .alert-critical {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .alert-warning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Données simulées
@st.cache_data
def load_sample_data():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=500, freq='H')
    
    sentiments = ['Positif', 'Négatif', 'Neutre']
    categories = ['Question Produit', 'Réclamation', 'Demande SAV', 'Compliment', 'Livraison', 'Remboursement']
    statuts = ['En attente', 'En cours', 'Répondu', 'Escaladé']
    
    data = {
        'date': dates,
        'tweet_id': [f"TWT{i:06d}" for i in range(500)],
        'auteur': [f"@user{np.random.randint(1, 100)}" for _ in range(500)],
        'contenu': [f"Tweet exemple {i}..." for i in range(500)],
        'sentiment': np.random.choice(sentiments, 500, p=[0.3, 0.4, 0.3]),
        'categorie': np.random.choice(categories, 500),
        'statut': np.random.choice(statuts, 500, p=[0.2, 0.3, 0.4, 0.1]),
        'priorite': np.random.choice(['Haute', 'Moyenne', 'Basse'], 500, p=[0.2, 0.5, 0.3]),
        'temps_reponse': np.random.randint(5, 300, 500),
        'score_urgence': np.random.uniform(0, 1, 500)
    }
    
    return pd.DataFrame(data)

# Navigation
def main():
    st.sidebar.markdown('<p class="main-header">🐦 Tweet Analytics</p>', unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard Principal", 
         "🔍 Monitoring Temps Réel", 
         "📈 Analyse & Insights",
         "🎫 Gestion des Tickets",
         "💬 Réponse aux Tweets",
         "⚙️ Configuration"]
    )
    
    # Statistiques sidebar
    df = load_sample_data()
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Statistiques Globales")
    st.sidebar.metric("Tweets Aujourd'hui", len(df[df['date'].dt.date == datetime.now().date()]))
    st.sidebar.metric("En Attente", len(df[df['statut'] == 'En attente']))
    st.sidebar.metric("Temps Moyen", f"{df['temps_reponse'].mean():.0f} min")
    
    # Affichage de la page sélectionnée
    if page == "📊 Dashboard Principal":
        show_dashboard(df)
    elif page == "🔍 Monitoring Temps Réel":
        show_monitoring(df)
    elif page == "📈 Analyse & Insights":
        show_analytics(df)
    elif page == "🎫 Gestion des Tickets":
        show_tickets(df)
    elif page == "💬 Réponse aux Tweets":
        show_response(df)
    elif page == "⚙️ Configuration":
        show_config()

def show_dashboard(df):
    st.markdown('<p class="main-header">📊 Dashboard Principal</p>', unsafe_allow_html=True)
    st.markdown("Vue d'ensemble de l'activité du service client Twitter")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        periode = st.selectbox("Période", ["Aujourd'hui", "7 derniers jours", "30 derniers jours", "Tout"])
    with col2:
        sentiment_filter = st.multiselect("Sentiment", df['sentiment'].unique(), default=df['sentiment'].unique())
    with col3:
        categorie_filter = st.multiselect("Catégorie", df['categorie'].unique(), default=df['categorie'].unique())
    
    # Filtrage des données
    df_filtered = df[df['sentiment'].isin(sentiment_filter) & df['categorie'].isin(categorie_filter)]
    
    # KPIs
    st.markdown("### 📈 Indicateurs Clés")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Tweets", len(df_filtered), delta=f"+{np.random.randint(10, 50)} vs hier")
    with col2:
        taux_reponse = (len(df_filtered[df_filtered['statut'] == 'Répondu']) / len(df_filtered) * 100)
        st.metric("Taux de Réponse", f"{taux_reponse:.1f}%", delta=f"+{np.random.uniform(0.5, 2):.1f}%")
    with col3:
        st.metric("Temps Moy. Réponse", f"{df_filtered['temps_reponse'].mean():.0f} min", 
                 delta=f"-{np.random.randint(5, 15)} min", delta_color="inverse")
    with col4:
        tweets_negatifs = len(df_filtered[df_filtered['sentiment'] == 'Négatif'])
        st.metric("Tweets Négatifs", tweets_negatifs, delta=f"-{np.random.randint(1, 10)}", delta_color="inverse")
    with col5:
        tickets_ouverts = len(df_filtered[df_filtered['statut'].isin(['En attente', 'En cours'])])
        st.metric("Tickets Ouverts", tickets_ouverts)
    
    # Graphiques principaux
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Volume de Tweets par Heure")
        df_hourly = df_filtered.groupby(df_filtered['date'].dt.hour).size().reset_index()
        df_hourly.columns = ['Heure', 'Nombre']
        fig = px.bar(df_hourly, x='Heure', y='Nombre', color='Nombre', 
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 😊 Distribution des Sentiments")
        sentiment_counts = df_filtered['sentiment'].value_counts()
        colors = {'Positif': '#4CAF50', 'Négatif': '#f44336', 'Neutre': '#9E9E9E'}
        fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index,
                     color=sentiment_counts.index, color_discrete_map=colors)
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📂 Top Catégories de Demandes")
        cat_counts = df_filtered['categorie'].value_counts().head(6)
        fig = px.bar(x=cat_counts.values, y=cat_counts.index, orientation='h',
                     color=cat_counts.values, color_continuous_scale='Viridis')
        fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### ⏱️ Temps de Réponse par Catégorie")
        temps_cat = df_filtered.groupby('categorie')['temps_reponse'].mean().sort_values(ascending=True)
        fig = px.bar(x=temps_cat.values, y=temps_cat.index, orientation='h',
                     color=temps_cat.values, color_continuous_scale='RdYlGn_r')
        fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Évolution temporelle
    st.markdown("#### 📈 Évolution des Tweets et Réponses")
    df_daily = df_filtered.groupby(df_filtered['date'].dt.date).agg({
        'tweet_id': 'count',
        'statut': lambda x: (x == 'Répondu').sum()
    }).reset_index()
    df_daily.columns = ['Date', 'Total Tweets', 'Tweets Répondus']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_daily['Date'], y=df_daily['Total Tweets'], 
                             name='Total Tweets', line=dict(color='#1DA1F2', width=3)))
    fig.add_trace(go.Scatter(x=df_daily['Date'], y=df_daily['Tweets Répondus'], 
                             name='Répondus', line=dict(color='#4CAF50', width=3)))
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

def show_monitoring(df):
    st.markdown('<p class="main-header">🔍 Monitoring Temps Réel</p>', unsafe_allow_html=True)
    
    # Alertes
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="alert-critical">⚠️ <b>3 tweets critiques</b> nécessitent une réponse urgente</div>', 
                   unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="alert-warning">⏰ <b>12 tweets</b> en attente depuis plus de 2h</div>', 
                   unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtres temps réel
    col1, col2, col3 = st.columns(3)
    with col1:
        urgence = st.selectbox("Urgence", ["Toutes", "Haute", "Moyenne", "Basse"])
    with col2:
        statut = st.selectbox("Statut", ["Tous", "En attente", "En cours", "Répondu"])
    with col3:
        if st.button("🔄 Rafraîchir"):
            st.rerun()
    
    # Tweets en temps réel
    st.markdown("### 📱 Flux de Tweets en Direct")
    
    df_recent = df.sort_values('date', ascending=False).head(20)
    
    for idx, row in df_recent.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                sentiment_emoji = {"Positif": "😊", "Négatif": "😠", "Neutre": "😐"}
                st.markdown(f"**{row['auteur']}** {sentiment_emoji[row['sentiment']]}")
                st.caption(f"{row['contenu']} - {row['date'].strftime('%H:%M:%S')}")
            
            with col2:
                color = {"Haute": "🔴", "Moyenne": "🟡", "Basse": "🟢"}
                st.markdown(f"{color[row['priorite']]} {row['priorite']}")
                st.caption(row['categorie'])
            
            with col3:
                status_color = {"En attente": "🟠", "En cours": "🔵", "Répondu": "🟢", "Escaladé": "🔴"}
                st.markdown(f"{status_color[row['statut']]} {row['statut']}")
                st.caption(f"{row['temps_reponse']} min")
            
            with col4:
                if st.button("👁️ Voir", key=f"view_{idx}"):
                    st.session_state.selected_tweet = row['tweet_id']
                if st.button("✍️ Répondre", key=f"reply_{idx}"):
                    st.session_state.reply_to = row['tweet_id']
            
            st.markdown("---")

def show_analytics(df):
    st.markdown('<p class="main-header">📈 Analyse & Insights</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue Globale", "🎯 Analyse Sentiments", "🔍 Insights Avancés", "📑 Rapports"])
    
    with tab1:
        st.markdown("### 📊 Statistiques Détaillées")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### 📈 Performance")
            perf_data = pd.DataFrame({
                'Métrique': ['Tweets traités', 'Taux résolution', 'Satisfaction client', 'SLA respecté'],
                'Valeur': ['8,542', '87.3%', '4.2/5', '94.1%'],
                'Évolution': ['+12%', '+3.2%', '+0.3', '+1.8%']
            })
            st.dataframe(perf_data, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("#### ⏱️ Temps de Traitement")
            temps_data = pd.DataFrame({
                'Segment': ['< 30 min', '30-60 min', '60-120 min', '> 120 min'],
                'Pourcentage': ['45%', '32%', '18%', '5%']
            })
            st.dataframe(temps_data, hide_index=True, use_container_width=True)
        
        with col3:
            st.markdown("#### 🏆 Top Agents")
            agent_data = pd.DataFrame({
                'Agent': ['Marie L.', 'Thomas D.', 'Sophie M.', 'Alex R.'],
                'Réponses': [342, 318, 287, 265],
                'Satisfaction': ['4.8⭐', '4.7⭐', '4.6⭐', '4.5⭐']
            })
            st.dataframe(agent_data, hide_index=True, use_container_width=True)
        
        # Tendances
        st.markdown("### 📈 Tendances et Patterns")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 Volume par Jour de la Semaine")
            jours = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
            volumes = [850, 920, 880, 910, 890, 650, 520]
            fig = px.bar(x=jours, y=volumes, color=volumes, 
                        color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🕐 Distribution Horaire")
            heures = list(range(24))
            activite = [20, 15, 10, 8, 12, 25, 45, 78, 95, 88, 92, 85, 
                       90, 87, 95, 102, 98, 85, 72, 65, 55, 45, 35, 28]
            fig = px.line(x=heures, y=activite, markers=True)
            fig.update_traces(line_color='#1DA1F2', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 😊 Analyse Détaillée des Sentiments")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📊 Évolution des Sentiments")
            df_sentiment_time = df.groupby([df['date'].dt.date, 'sentiment']).size().reset_index()
            df_sentiment_time.columns = ['Date', 'Sentiment', 'Count']
            fig = px.line(df_sentiment_time, x='Date', y='Count', color='Sentiment',
                         color_discrete_map={'Positif': '#4CAF50', 'Négatif': '#f44336', 'Neutre': '#9E9E9E'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 💡 Insights Clés")
            st.info("📈 Hausse de 15% des sentiments positifs cette semaine")
            st.warning("⚠️ Pic de sentiments négatifs le mardi (problème livraison)")
            st.success("✅ Amélioration de 8% de la satisfaction globale")
        
        # Corrélation sentiment / catégorie
        st.markdown("#### 🔗 Sentiments par Catégorie")
        sentiment_cat = pd.crosstab(df['categorie'], df['sentiment'], normalize='index') * 100
        fig = px.bar(sentiment_cat, barmode='stack',
                     color_discrete_map={'Positif': '#4CAF50', 'Négatif': '#f44336', 'Neutre': '#9E9E9E'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 🔍 Insights Avancés (IA/LLM)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Thèmes Émergents Détectés")
            themes = pd.DataFrame({
                'Thème': ['Retard de livraison', 'Qualité produit', 'Service client', 'Prix élevés', 'Bug application'],
                'Occurrences': [145, 98, 87, 56, 43],
                'Tendance': ['📈 +23%', '📉 -5%', '📈 +12%', '→ stable', '📈 +34%']
            })
            st.dataframe(themes, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("#### 🚨 Alertes Automatiques")
            st.error("🔴 **Alerte Critique**: Augmentation soudaine des plaintes sur les livraisons (+40% en 24h)")
            st.warning("🟡 **Attention**: Mention récurrente de problèmes techniques sur l'app mobile")
            st.info("🔵 **Info**: Nouveau produit génère beaucoup d'intérêt positif")
        
        st.markdown("#### 💬 Analyse Sémantique des Requêtes")
        st.markdown("**Top mots-clés négatifs:** remboursement (234), retard (198), déçu (156), problème (142)")
        st.markdown("**Top mots-clés positifs:** satisfait (189), rapide (167), merci (154), excellent (98)")
        
        # Recommandations IA
        st.markdown("#### 🤖 Recommandations IA")
        st.success("✅ Augmenter les ressources sur les demandes de livraison (charge +30%)")
        st.success("✅ Créer une FAQ automatique sur les retours/remboursements (demandes répétitives)")
        st.success("✅ Former les agents sur les nouveaux produits (confusion détectée)")
    
    with tab4:
        st.markdown("### 📑 Génération de Rapports")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            type_rapport = st.selectbox("Type de rapport", 
                                       ["Rapport Journalier", "Rapport Hebdomadaire", "Rapport Mensuel", "Rapport Personnalisé"])
        with col2:
            format_export = st.selectbox("Format", ["PDF", "Excel", "CSV", "PowerPoint"])
        with col3:
            st.markdown("####  ")
            if st.button("📥 Générer Rapport", use_container_width=True):
                st.success("✅ Rapport généré avec succès!")
                st.download_button("📥 Télécharger", data="Rapport fictif", file_name="rapport.pdf")

def show_tickets(df):
    st.markdown('<p class="main-header">🎫 Gestion des Tickets SAV</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tickets Ouverts", 87, delta="+5")
    with col2:
        st.metric("Tickets en Cours", 34, delta="-2")
    with col3:
        st.metric("Tickets Résolus (24h)", 156, delta="+12")
    
    st.markdown("---")
    
    # Filtres
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filtre_priorite = st.multiselect("Priorité", ["Haute", "Moyenne", "Basse"], default=["Haute"])
    with col2:
        filtre_statut = st.multiselect("Statut", df['statut'].unique(), default=df['statut'].unique())
    with col3:
        filtre_categorie = st.selectbox("Catégorie", ["Toutes"] + list(df['categorie'].unique()))
    with col4:
        st.markdown("#### ")
        if st.button("➕ Créer Ticket Manuel"):
            st.session_state.create_ticket = True
    
    # Backlog de tickets
    st.markdown("### 📋 Backlog de Tickets")
    
    df_tickets = df[df['priorite'].isin(filtre_priorite) & df['statut'].isin(filtre_statut)].head(15)
    
    for idx, row in df_tickets.iterrows():
        with st.expander(f"🎫 {row['tweet_id']} - {row['categorie']} | {row['priorite']} priorité | {row['statut']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Auteur:** {row['auteur']}")
                st.markdown(f"**Date:** {row['date'].strftime('%d/%m/%Y %H:%M')}")
                st.markdown(f"**Contenu:** {row['contenu']}")
                st.markdown(f"**Sentiment:** {row['sentiment']}")
                
                st.markdown("**Actions:**")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button("✅ Résoudre", key=f"resolve_{idx}"):
                        st.success("Ticket résolu!")
                with col_b:
                    if st.button("⬆️ Escalader", key=f"escalate_{idx}"):
                        st.warning("Ticket escaladé au manager")
                with col_c:
                    if st.button("💬 Répondre", key=f"resp_{idx}"):
                        st.info("Redirection vers réponse...")
            
            with col2:
                st.markdown("**Détails Ticket:**")
                st.metric("Temps écoulé", f"{row['temps_reponse']} min")
                st.metric("Score urgence", f"{row['score_urgence']:.2f}")
                
                agent_assigne = st.selectbox("Agent assigné", 
                                            ["Non assigné", "Marie L.", "Thomas D.", "Sophie M."], 
                                            key=f"agent_{idx}")
                
                notes = st.text_area("Notes internes", key=f"notes_{idx}", height=80)
    
    # Stats tickets
    st.markdown("---")
    st.markdown("### 📊 Statistiques Tickets")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Distribution par Statut")
        statut_counts = df['statut'].value_counts()
        fig = px.pie(values=statut_counts.values, names=statut_counts.index, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Tickets par Priorité")
        prio_counts = df['priorite'].value_counts()
        colors = {'Haute': '#f44336', 'Moyenne': '#ff9800', 'Basse': '#4CAF50'}
        fig = px.bar(x=prio_counts.index, y=prio_counts.values,
                    color=prio_counts.index, color_discrete_map=colors)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("#### Temps de Résolution Moyen")
        temps_prio = df.groupby('priorite')['temps_reponse'].mean()
        fig = px.bar(x=temps_prio.index, y=temps_prio.values,
                    color=temps_prio.values, color_continuous_scale='RdYlGn_r')
        st.plotly_chart(fig, use_container_width=True)

def show_response(df):
    st.markdown('<p class="main-header">💬 Réponse aux Tweets</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Composer une Réponse")
        
        # Sélection du tweet
        tweets_pending = df[df['statut'] == 'En attente'].head(10)
        selected_tweet = st.selectbox(
            "Sélectionner un tweet à traiter",
            options=tweets_pending['tweet_id'].tolist(),
            format_func=lambda x: f"{x} - {tweets_pending[tweets_pending['tweet_id']==x]['auteur'].values[0]}"
        )
        
        if selected_tweet:
            tweet_data = tweets_pending[tweets_pending['tweet_id'] == selected_tweet].iloc[0]
            
            # Affichage du tweet original
            st.markdown("#### 📱 Tweet Original")
            st.info(f"""
            **{tweet_data['auteur']}** - {tweet_data['date'].strftime('%d/%m/%Y %H:%M')}
            
            {tweet_data['contenu']}
            
            📊 **Catégorie:** {tweet_data['categorie']} | **Sentiment:** {tweet_data['sentiment']} | **Priorité:** {tweet_data['priorite']}
            """)
            
            # Suggestions IA
            st.markdown("#### 🤖 Suggestions de Réponses (IA)")
            
            suggestions = [
                "Bonjour ! Nous sommes désolés pour ce désagrément. Pouvez-vous nous envoyer votre numéro de commande en DM pour que nous puissions vous aider rapidement ? 😊",
                "Merci pour votre message. Notre équipe est mobilisée pour résoudre ce problème dans les plus brefs délais. Nous vous tiendrons informé.",
                "Nous comprenons votre frustration et nous excusons pour cette situation. Un membre de notre équipe va vous contacter sous 24h pour trouver une solution."
            ]
            
            for i, suggestion in enumerate(suggestions, 1):
                col_sug, col_btn = st.columns([4, 1])
                with col_sug:
                    st.text_area(f"Suggestion {i}", suggestion, height=80, key=f"sug_{i}", disabled=True)
                with col_btn:
                    st.markdown("#### ")
                    if st.button("✅ Utiliser", key=f"use_sug_{i}"):
                        st.session_state.response_text = suggestion
            
            # Zone de réponse
            st.markdown("#### ✍️ Votre Réponse")
            response_text = st.text_area(
                "Composer votre réponse",
                value=st.session_state.get('response_text', ''),
                height=150,
                max_chars=280,
                help="Maximum 280 caractères (limite Twitter)"
            )
            
            col_char, col_tone = st.columns(2)
            with col_char:
                char_count = len(response_text)
                color = "🟢" if char_count <= 280 else "🔴"
                st.caption(f"{color} {char_count}/280 caractères")
            
            with col_tone:
                tone = st.selectbox("Ton de la réponse", ["Professionnel", "Amical", "Formel", "Empathique"])
            
            # Actions
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📤 Envoyer Réponse", use_container_width=True, type="primary"):
                    st.success("✅ Réponse envoyée avec succès!")
                    st.balloons()
            
            with col2:
                if st.button("💾 Sauvegarder Brouillon", use_container_width=True):
                    st.info("💾 Brouillon sauvegardé")
            
            with col3:
                if st.button("⏭️ Passer au Suivant", use_container_width=True):
                    st.rerun()
            
            with col4:
                if st.button("🚫 Ignorer", use_container_width=True):
                    st.warning("Tweet ignoré")
    
    with col2:
        st.markdown("### 📊 Statistiques de Réponse")
        
        st.metric("Réponses Aujourd'hui", 42, delta="+8")
        st.metric("Temps Moy. Réponse", "18 min", delta="-5 min", delta_color="inverse")
        st.metric("Satisfaction", "4.5/5", delta="+0.2")
        
        st.markdown("---")
        st.markdown("### 📚 Modèles de Réponse")
        
        modeles = {
            "Réclamation Livraison": "Nous sommes désolés pour ce retard. Pouvez-vous nous communiquer votre n° de commande en MP ?",
            "Question Produit": "Merci pour votre intérêt ! Vous trouverez toutes les informations sur notre site. Besoin d'aide ?",
            "Compliment": "Merci beaucoup pour vos encouragements ! 😊 Toute l'équipe est ravie de vous satisfaire !",
            "Remboursement": "Nous comprenons votre demande. Notre équipe SAV va traiter votre dossier rapidement."
        }
        
        for nom, texte in modeles.items():
            if st.button(f"📋 {nom}", use_container_width=True):
                st.session_state.response_text = texte
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎯 File d'Attente")
        st.metric("En attente", len(tweets_pending))
        st.progress(len(tweets_pending) / 100)
        
        st.markdown("### ⏱️ Temps Restant Estimé")
        temps_estime = len(tweets_pending) * 18  # 18 min par tweet
        st.metric("Estimation", f"{temps_estime} min")

def show_config():
    st.markdown('<p class="main-header">⚙️ Configuration</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Paramètres Généraux", "🤖 Configuration LLM", "👥 Gestion Équipe", "🔔 Alertes"])
    
    with tab1:
        st.markdown("### 🔧 Paramètres Généraux")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🐦 Configuration Twitter")
            compte_twitter = st.text_input("Compte Twitter à monitorer", value="@VotreEntreprise")
            refresh_rate = st.slider("Fréquence de rafraîchissement (min)", 1, 60, 5)
            auto_reponse = st.checkbox("Activer les réponses automatiques", value=True)
            
            st.markdown("#### 📊 Préférences d'Affichage")
            langue = st.selectbox("Langue", ["Français", "English", "Español"])
            theme = st.selectbox("Thème", ["Clair", "Sombre", "Auto"])
            timezone = st.selectbox("Fuseau horaire", ["Europe/Paris", "America/New_York", "Asia/Tokyo"])
        
        with col2:
            st.markdown("#### ⏱️ SLA et Objectifs")
            sla_reponse = st.number_input("SLA Temps de réponse (min)", min_value=5, value=60)
            sla_resolution = st.number_input("SLA Résolution (heures)", min_value=1, value=24)
            objectif_satisfaction = st.slider("Objectif satisfaction client", 1.0, 5.0, 4.5, 0.1)
            
            st.markdown("#### 📧 Notifications")
            notif_email = st.checkbox("Notifications par email", value=True)
            notif_slack = st.checkbox("Notifications Slack", value=False)
            notif_critique = st.checkbox("Alertes tweets critiques", value=True)
        
        if st.button("💾 Sauvegarder Configuration", type="primary"):
            st.success("✅ Configuration sauvegardée avec succès!")
    
    with tab2:
        st.markdown("### 🤖 Configuration du Modèle LLM")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🧠 Modèle d'IA")
            llm_model = st.selectbox("Modèle LLM", 
                                    ["GPT-4", "Claude 3 Opus", "Claude 3 Sonnet", "Mistral Large"])
            temperature = st.slider("Température (créativité)", 0.0, 1.0, 0.7, 0.1)
            max_tokens = st.number_input("Tokens maximum", min_value=50, max_value=500, value=280)
            
            st.markdown("#### 🎯 Classification")
            st.checkbox("Détection de sentiment", value=True)
            st.checkbox("Classification par intention", value=True)
            st.checkbox("Extraction d'entités", value=True)
            st.checkbox("Détection de langue", value=True)
        
        with col2:
            st.markdown("#### 📝 Génération de Réponses")
            reponse_auto_seuil = st.slider("Seuil confiance réponse auto", 0.0, 1.0, 0.85, 0.05)
            ton_default = st.selectbox("Ton par défaut", 
                                      ["Professionnel", "Amical", "Formel", "Empathique"])
            
            st.markdown("#### 🔍 Analyse Avancée")
            detect_urgence = st.checkbox("Détection d'urgence automatique", value=True)
            analyse_semantique = st.checkbox("Analyse sémantique avancée", value=True)
            detection_themes = st.checkbox("Détection de thèmes émergents", value=True)
        
        st.markdown("---")
        st.markdown("#### 🧪 Test du Modèle")
        test_text = st.text_area("Texte de test", 
                                 "Bonjour, je n'ai toujours pas reçu ma commande #12345 passée il y a 10 jours. C'est inadmissible!")
        
        if st.button("🧪 Analyser avec le LLM"):
            with st.spinner("Analyse en cours..."):
                st.success("✅ Analyse terminée")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sentiment", "😠 Négatif", delta="Confiance: 94%")
                with col2:
                    st.metric("Catégorie", "Réclamation Livraison", delta="Confiance: 89%")
                with col3:
                    st.metric("Urgence", "🔴 Haute", delta="Score: 0.87")
                
                st.markdown("**Réponse suggérée:**")
                st.info("Bonjour, nous sommes sincèrement désolés pour ce retard. Nous allons vérifier le statut de votre commande #12345 immédiatement. Un membre de notre équipe va vous contacter dans l'heure. Merci de votre patience.")
    
    with tab3:
        st.markdown("### 👥 Gestion de l'Équipe")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 👤 Membres de l'Équipe")
            
            equipe = pd.DataFrame({
                'Agent': ['Marie Lambert', 'Thomas Dubois', 'Sophie Martin', 'Alex Richard'],
                'Rôle': ['Manager', 'Agent Senior', 'Agent', 'Agent'],
                'Statut': ['✅ En ligne', '✅ En ligne', '🟡 Absent', '🔴 Hors ligne'],
                'Tweets/jour': [45, 38, 32, 28],
                'Satisfaction': ['4.8⭐', '4.7⭐', '4.6⭐', '4.5⭐']
            })
            
            st.dataframe(equipe, hide_index=True, use_container_width=True)
            
            if st.button("➕ Ajouter un Agent"):
                st.info("Formulaire d'ajout d'agent...")
        
        with col2:
            st.markdown("#### 📊 Performance Équipe")
            st.metric("Agents Actifs", "3/4")
            st.metric("Charge Moyenne", "35 tweets/jour")
            st.metric("Satisfaction Moy.", "4.65⭐")
            
            st.markdown("---")
            st.markdown("#### 🎯 Objectifs")
            st.progress(0.87, text="Objectif quotidien: 87%")
            st.progress(0.94, text="SLA respecté: 94%")
    
    with tab4:
        st.markdown("### 🔔 Configuration des Alertes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⚠️ Seuils d'Alerte")
            alerte_tweets_attente = st.number_input("Tweets en attente", min_value=1, value=10)
            alerte_temps_reponse = st.number_input("Temps réponse max (min)", min_value=5, value=120)
            alerte_sentiment_negatif = st.slider("% Sentiment négatif", 0, 100, 50)
            alerte_pic_volume = st.slider("Augmentation volume (%)", 0, 200, 50)
        
        with col2:
            st.markdown("#### 📬 Canaux de Notification")
            canal_email = st.multiselect("Email", ["manager@entreprise.com", "sav@entreprise.com"])
            canal_slack = st.text_input("Canal Slack", "#customer-support-alerts")
            canal_sms = st.checkbox("Notifications SMS (urgence)", value=False)
        
        st.markdown("---")
        st.markdown("#### 📋 Règles d'Alerte Actives")
        
        regles = pd.DataFrame({
            'Règle': ['Tweet critique non traité', 'SLA dépassé', 'Pic de volume', 'Sentiment très négatif'],
            'Statut': ['🟢 Active', '🟢 Active', '🟢 Active', '🟡 Pause'],
            'Dernière alerte': ['Il y a 2h', 'Il y a 5h', 'Aucune aujourd\'hui', 'Il y a 1 jour']
        })
        
        st.dataframe(regles, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    if 'response_text' not in st.session_state:
        st.session_state.response_text = ''
    
    main()