"""
🎨 INTERFACE WEB STREAMLIT pour SportLLM Chatbot
=================================================

Interface utilisateur web pour interagir avec le graphe de connaissances sportif.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

# Configuration de la page
st.set_page_config(
    page_title="SportLLM Chatbot",
    page_icon="🏇",
    layout="wide"
)

# Charger les variables d'environnement
load_dotenv()

# Titre et description
st.title("🏇 SportLLM Chatbot")
st.markdown("**Assistant intelligent pour notre graphe de connaissances sportif**")

# Charger la clé OpenAI depuis .env
openai_key = os.getenv("OPENAI_API_KEY")

# Initialiser la session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph_initialized" not in st.session_state:
    st.session_state.graph_initialized = False

# Fonction pour initialiser le graphe et la chaîne
@st.cache_resource
def init_graph_chain():
    """Initialise la connexion Neo4j et la chaîne LangChain"""
    try:
        # Configuration Neo4j
        graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_DATABASE", "neo4j")
        )
        
        graph.refresh_schema()
        
        # Modèle OpenAI
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Template personnalisé simplifié
        CYPHER_GENERATION_TEMPLATE = """Tâche : Générer une requête Cypher pour Neo4j.

Schéma : {schema}

Question : {question}

Instructions CRITIQUES - DIRECTIONS DES RELATIONS (NE JAMAIS INVERSER!):
- ASSOCIATEDWITH: (Rider)-[:ASSOCIATEDWITH]->(Horse)
  Exemple: MATCH (r:Rider)-[:ASSOCIATEDWITH]->(h:Horse)
  
- ISATTACHEDTO: (InertialSensors)-[:ISATTACHEDTO]->(Horse) 
  Exemple: MATCH (s:InertialSensors)-[:ISATTACHEDTO]->(h:Horse)
  Note: Les capteurs InertialSensors ont TOUJOURS 2 labels - le 2ème indique la partie du corps
  Exemples: [:InertialSensors:Withers], [:InertialSensors:Sternum], [:InertialSensors:CanonOfForelimb], [:InertialSensors:CanonOfHindlimb]
  
- ISUSEDFOR: (InertialSensors)-[:ISUSEDFOR]->(ExperimentalObjective)
  Exemple: MATCH (s:InertialSensors)-[:ISUSEDFOR]->(eo:ExperimentalObjective)
  Note: Pour "objectif expérimental" d'un capteur → SEULEMENT cette relation (pas TRAINSIN)
  ExperimentalObjective.id peut être: 'GaitClassif_01' (classification allures) ou 'FatigueDetection' (détection fatigue)
  Pour obtenir la partie du corps d'un capteur: utilise labels(s) qui retourne ['InertialSensors', 'Withers'] par exemple
  
- TRAINSIN: (Horse)-[:TRAINSIN]->(PreparationStage|PreCompetitionStage|CompetitionStage|TransitionStage)
  Exemple: MATCH (h:Horse)-[:TRAINSIN]->(t:PreparationStage)
  
- DEPENDSON: (Training)-[:DEPENDSON]->(Event)
  Exemple: MATCH (t:Training)-[:DEPENDSON]->(e:Event)
  
- INVOLVESACTOR: (PreparationStage|PreCompetitionStage|CompetitionStage|TransitionStage)-[:INVOLVESACTOR]->(Rider|Veterinarian|Caretaker)
  Exemple correct: MATCH (p:PreparationStage)-[:INVOLVESACTOR]->(v:Veterinarian)
  Exemple INCORRECT: MATCH (v:Veterinarian)-[:INVOLVESACTOR]->(p:PreparationStage) ❌
  
  Pour comparer les acteurs de phases différentes:
  MATCH (prep:PreparationStage)-[:INVOLVESACTOR]->(actor1)
  MATCH (precomp:PreCompetitionStage)-[:INVOLVESACTOR]->(actor2)
  RETURN COLLECT(DISTINCT actor1.id) AS acteurs_preparation, COLLECT(DISTINCT actor2.id) AS acteurs_precompetition

- INSEASON: (Event)-[:INSEASON]->(CompetitiveSeason)
  Exemple: MATCH (e:ShowJumping)-[:INSEASON]->(s:CompetitiveSeason)
  Note: seasonName = "Saison 2026" (pas "2026")

- PARTICIPATIONS ET CLASSEMENTS:
  (Event)-[:HASPARTICIPATION]->(EventParticipation)-[:HASHORSE]->(Horse)
  (Event)-[:HASPARTICIPATION]->(EventParticipation)-[:HASRIDER]->(Rider)
  EventParticipation a la propriété 'rank' pour le classement
  IMPORTANT: EventParticipation a des relations DIRECTES vers Horse ET Rider
  
  Pour chercher un duo cavalier+cheval (ex: Emma et Dakota):
  - Emma = Rider (cherche avec id: "Rider_Emma" ou id CONTAINS "Emma")
  - Dakota = Horse (cherche avec hasName: "Dakota")
  Exemple: MATCH (e:Event)-[:HASPARTICIPATION]->(p:EventParticipation)
           MATCH (p)-[:HASHORSE]->(h:Horse {{hasName: "Dakota"}})
           MATCH (p)-[:HASRIDER]->(r:Rider)
           WHERE r.id CONTAINS "Emma"
           RETURN r.id, h.hasName, p.rank

PROPRIÉTÉS IMPORTANTES:
- Fréquence d'échantillonnage = hasSensorTime (ex: "200Hz", "250Hz")
- Pour MAX/MIN fréquence → ORDER BY s.hasSensorTime DESC/ASC LIMIT 1
- Classement = propriété 'rank' sur EventParticipation
- Capteurs: Utilise 'id' (ex: "IMU_Withers_01") PAS 'hasSensorID' qui contient des codes différents (ex: "IMU-W-001")
- ExperimentalObjective: Utilise la propriété 'id' (valeurs: 'GaitClassif_01', 'FatigueDetection') - PAS l'uri
- Partie du corps des capteurs: Dans le 2ème label (utilise labels(s)[1] ou labels(s) pour voir tous les labels)

SYNTAXE:
- Pour "Tous les X ont-ils Y?" → MATCH (x:X) OPTIONAL MATCH (y:Y)-[relation]->(x)
- Pour COUNT → utilise COUNT(DISTINCT variable)
- CHEVAUX ont 'hasName' (Dakota, Naya) - CAVALIERS n'ont QUE 'id' (Rider_Emma, Rider_Leo, Rider_Manon)
- Retourne 'id' et 'hasName' (JAMAIS 'uri')
- N'utilise JAMAIS UNION - préfère une seule requête MATCH
- Pour plusieurs types d'événements → MATCH (e) WHERE e:ShowJumping OR e:Dressage OR e:Cross
- Pour GROUPER par objectif → utilise COLLECT() avec le nom de l'objectif
  Exemple: RETURN eo.id as objectif, COLLECT(s.id) as capteurs, COLLECT(labels(s)[1]) as parties_corps
- IMPORTANT: Ne mélange PAS plusieurs sujets dans une seule requête
  * Si la question porte sur les acteurs des phases → SEULEMENT PreparationStage/PreCompetitionStage + INVOLVESACTOR
  * Si la question porte sur les événements → SEULEMENT Event + relations d'événements
  * Si la question porte sur les capteurs → SEULEMENT InertialSensors + ISUSEDFOR/ISATTACHEDTO
- Garde la requête simple et directe - réponds UNIQUEMENT à ce qui est demandé

Requête Cypher:"""
        
        CYPHER_PROMPT = PromptTemplate(
            input_variables=["schema", "question"],
            template=CYPHER_GENERATION_TEMPLATE
        )
        
        # Template pour la réponse finale
        QA_TEMPLATE = """Tu réponds à des questions sur un graphe de connaissances.

Question: {question}
Context: {context}

RÈGLES:
1. Réponds EXACTEMENT avec les informations du context - ne devine pas
2. Noms des chevaux: Horse1=Dakota, Horse2=Naya
3. Noms des cavaliers: Rider_Emma=Emma, Rider_Leo=Leo, Rider_Manon=Manon
4. Acteurs: Vet_DrMartin=Dr Martin (vétérinaire), Caretaker_Sophie=Sophie (soigneuse)
5. Capteurs: IMU_Withers_01 = capteur au garrot, IMU_Sternum_01 = capteur au sternum
6. Objectifs expérimentaux: GaitClassif_01 = classification des allures, FatigueDetection = détection de fatigue
7. IMPORTANT: Dakota et Naya sont des CHEVAUX, pas des cavaliers
8. IMPORTANT: Si le context contient des données GROUPÉES par objectif (ex: GaitClassif_01: [...], FatigueDetection: [...])
   → Respecte EXACTEMENT ces groupes, ne dis JAMAIS que c'est commun aux deux si ce n'est pas le cas
9. Pour les COMPARAISONS explicites (questions avec "comparer", "différence"), fournis une analyse DÉTAILLÉE
   Pour les questions DESCRIPTIVES simples, reste CONCIS et factuel

Réponse:"""
        
        QA_PROMPT = PromptTemplate(
            input_variables=["question", "context"],
            template=QA_TEMPLATE
        )
        
        # Créer la chaîne
        chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=graph,
            verbose=True,
            cypher_prompt=CYPHER_PROMPT,
            qa_prompt=QA_PROMPT,
            return_intermediate_steps=True,
            allow_dangerous_requests=True
        )
        
        return chain, graph
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation : {str(e)}")
        return None, None

# Vérifier la configuration avant d'initialiser
if openai_key:
    # Initialiser le graphe et la chaîne
    with st.spinner("🔄 Connexion au graphe de connaissances..."):
        chain, graph = init_graph_chain()
    
    if chain and graph:
        st.session_state.graph_initialized = True
        
        # Afficher l'historique des messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "cypher" in message:
                    with st.expander("🔍 Détails techniques"):
                        st.code(message["cypher"], language="cypher")
        
        # Zone de saisie de question
        if prompt := st.chat_input("Posez votre question..."):
            # Ajouter le message de l'utilisateur
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Générer la réponse
            with st.chat_message("assistant"):
                with st.spinner("🤔 Réflexion en cours..."):
                    try:
                        result = chain.invoke({"query": prompt})
                        answer = result.get("result", "Désolé, je n'ai pas pu trouver de réponse.")
                        
                        st.markdown(answer)
                        
                        # Option pour voir la requête technique (masquée par défaut)
                        if result.get("intermediate_steps"):
                            cypher_query = result["intermediate_steps"][0].get("query", "N/A")
                            with st.expander("🔍 Détails techniques"):
                                st.code(cypher_query, language="cypher")
                            
                            # Sauvegarder avec la requête Cypher
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer,
                                "cypher": cypher_query
                            })
                        else:
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": answer
                            })
                    
                    except Exception as e:
                        error_msg = f"❌ Erreur : {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
        
        # Informations système (masquées)
        with st.expander("ℹ️ Informations système", expanded=False):
            st.caption("Schéma du graphe :")
            st.code(graph.schema, language="text")
    else:
        st.error("❌ Impossible de se connecter au graphe Neo4j. Vérifiez vos identifiants.")
else:
    st.info("🔑 Veuillez configurer votre clé OpenAI dans la barre latérale pour commencer.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        SportLLM Chatbot | Powered by LangChain, OpenAI & Neo4j
    </div>
    """,
    unsafe_allow_html=True
)
