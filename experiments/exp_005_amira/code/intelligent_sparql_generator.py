# intelligent_sparql_generator.py
"""
Intelligent SPARQL Generator - Equestrian Knowledge Graph
Generates SPARQL queries dynamically using LLM with Few-Shot Learning
Updated for new ontology structure
"""

import json
import re
from typing import Dict, Any
from config import ONTOLOGY_NAMESPACE, get_sparql_prefixes


class IntelligentSPARQLGenerator:
    """Generates SPARQL queries using LLM intelligence and ontology awareness"""
    
    def __init__(self, llm_client):
        """
        Initialize SPARQL generator
        
        Args:
            llm_client: LLM client for generating queries
        """
        self.llm = llm_client
        self.namespace = ONTOLOGY_NAMESPACE
        
        # Create detailed ontology summary from your actual data
        self.ontology_summary = self._create_ontology_summary()
    
    def _create_ontology_summary(self):
        """
        Create comprehensive ontology summary for LLM
        This is based on your actual ontology.owl structure
        """
        return f"""
# ONTOLOGIE ÉQUESTRE - STRUCTURE COMPLÈTE

## NAMESPACE:
{self.namespace}

## CLASSES PRINCIPALES:

### 1. Horse (Cheval)
Description: Représente un cheval
Propriétés:
  - hasName (string) : Nom du cheval (ex: "Dakota")
  - hasPuce (integer) : Numéro de puce électronique
  - hasRace (string) : Race du cheval
  - hasRobe (string) : Couleur de la robe
  - hasHeight (float) : Taille du cheval
Exemple: Horse1 avec hasName "Dakota"

### 2. Rider (Cavalier)
Description: Représente un cavalier
Propriétés:
  - hasName (string) : Nom du cavalier

### 3. Training (Entraînement)
Description: Séances d'entraînement
Sous-classes:
  - PreparationStage : Préparation avant compétition
  - PreCompetitionStage : Entraînement pré-compétitif
  - CompetitionStage : Phase de compétition
  - TransitionStage : Phase de transition/récupération

Propriétés:
  - Frequency (integer) : Fréquence d'entraînement (ex: 4 fois par semaine)
  - Intensity (string) : Intensité (Moderate, High, Peak, Low)
  - Volume (string) : Durée (ex: "45min", "60min")

Exemples d'instances:
  - Training_Preparation_SJ_01 (Intensity: "Moderate", Frequency: 4)
  - Training_PreCompetition_SJ_01 (Intensity: "High", Frequency: 3)
  - Training_Competition_SJ_01 (Intensity: "Peak", Frequency: 1)
  - Training_Transition_SJ_01 (Intensity: "Low", Frequency: 2)

### 4. SportingEvent (Événement sportif)
Description: Compétitions équestres
Sous-classes:
  - ShowJumping (CSO - Saut d'obstacles)
  - Dressage (Dressage)
  - Cross (Cross-country/CCE)

Propriétés:
  - hasDate (date)
  - hasLocation (string)
  - hasName (string)

Exemples d'instances:
  - Event_SJ_2026_01 (type: ShowJumping)
  - Event_Dressage_2026_01 (type: Dressage)
  - Event_Cross_2026_01 (type: Cross)

### 5. ExperimentalDevices (Dispositifs expérimentaux)
Description: Capteurs et équipements de mesure
Sous-classes:
  - InertialSensors : Capteurs inertiels
  - Camera : Caméras
  - Video : Vidéos
  - Images : Images

Propriétés:
  - hasSensorID (string) : ID du capteur
  - hasFormat (string) : Format de fichier
  - hasFileSize (integer) : Taille du fichier
  - hasCamView (string) : Vue de la caméra
  - ImageName (string) : Nom de l'image

### 6. Studies (Études)
Description: Projets de recherche
Exemples: BienetreSaumur, HappyAthlete, CognitionEquine

### 7. Topic (Thématiques)
Description: Thèmes de recherche
Exemples: HorseRiding, IndicateurPerformance, IndicateurBienetre

### 8. IndicateurPerformance (Indicateurs de performance)
Sous-classes:
  - FacteurPhysique : Facteurs physiques
  - FacteurMental : Facteurs mentaux
  - FacteurTechnique : Facteurs techniques

### 9. IndicateurBienetre (Indicateurs de bien-être)
Sous-classes:
  - Alimentation : Nutrition
  - Comportement : Comportement
  - Hebergement : Hébergement
  - HealthStatus : État de santé

## RELATIONS PRINCIPALES (Object Properties):

### CompetesIn
Domaine: Horse → Range: SportingEvent
Description: Le cheval participe à un événement sportif
Propriété: Transitive
Exemple: Horse1 CompetesIn Event_SJ_2026_01

### TrainsIn
Domaine: Horse → Range: Training
Description: Le cheval s'entraîne
Propriété: Transitive
Exemple: Horse1 TrainsIn Training_Preparation_SJ_01

### dependsOn
Domaine: Training → Range: SportingEvent
Description: L'entraînement dépend d'un événement
Propriété: Transitive
Exemple: Training_Preparation_SJ_01 dependsOn Event_SJ_2026_01

### hasParticipatedTo
Sous-propriété de: dependsOn
Description: Participation à un événement/étude
Exemple: Training_Competition_SJ_01 hasParticipatedTo Event_SJ_2026_01

### AssociatedWith
Description: Association entre entités (ex: Horse ↔ Rider)
Propriété: Transitive
Exemple: Horse1 AssociatedWith Rider1

### isAttachedTo
Domaine: Horse → Range: Sensor
Description: Capteur attaché au cheval
Propriété: Functional, Transitive
Exemple: Horse1 isAttachedTo Sensor123

### isUsedFor
Domaine: ExperimentalDevices → Range: ExperimentalObjectif
Sous-propriété de: TrainsIn
Description: Dispositif utilisé pour un objectif
Exemple: Camera1 isUsedFor Study_BienetreSaumur

### hasThematique
Domaine: Event/Study → Range: Topic
Description: Thématique d'un événement ou étude
Propriété: Functional, Transitive
Exemple: Event_SJ_2026_01 hasThematique HorseRiding

## PROPRIÉTÉS DE DONNÉES (Data Properties):

### Horse Properties:
- hasName (string) : Nom
- hasPuce (integer) : Numéro de puce
- hasRace (string) : Race
- hasRobe (string) : Couleur
- hasHeight (float) : Taille

### Training Properties:
- Frequency (integer) : Fréquence (nombre de fois)
- Intensity (string) : Intensité (Moderate/High/Peak/Low)
- Volume (string) : Durée (ex: "45min")

### Sensor Properties:
- hasSensorID (string) : ID capteur
- hasFormat (string) : Format
- hasFileSize (integer) : Taille fichier

### Image Properties:
- ImageName (string) : Nom image
- hasCamView (string) : Vue caméra
- hasDate (date) : Date
- hasLocation (string) : Lieu

## STRUCTURE DES DONNÉES ACTUELLES:

Cheval:
  - Horse1 (nom: "Dakota")
    → CompetesIn: Event_SJ_2026_01, Event_Dressage_2026_01, Event_Cross_2026_01
    → TrainsIn: Training_Preparation_SJ_01, Training_PreCompetition_SJ_01, 
                Training_Competition_SJ_01, Training_Transition_SJ_01

Événements:
  - Event_SJ_2026_01 (ShowJumping)
  - Event_Dressage_2026_01 (Dressage)
  - Event_Cross_2026_01 (Cross)

Entraînements (tous pour ShowJumping):
  - Training_Preparation_SJ_01: Frequency=4, Intensity="Moderate", Volume="45min"
  - Training_PreCompetition_SJ_01: Frequency=3, Intensity="High", Volume="60min"
  - Training_Competition_SJ_01: Frequency=1, Intensity="Peak", Volume="30min"
  - Training_Transition_SJ_01: Frequency=2, Intensity="Low", Volume="30min"

## POINTS IMPORTANTS POUR GÉNÉRER DES REQUÊTES:

1. **PAS de clause GRAPH**: Toutes les données sont dans le graphe par défaut
   Mauvais: WHERE {{ GRAPH <...> {{ ?s ?p ?o }} }}
   Correct: WHERE {{ ?s ?p ?o }}

2. **Utiliser OPTIONAL** pour propriétés qui peuvent ne pas exister
   Exemple: OPTIONAL {{ ?horse horses:hasRace ?race }}

3. **Filtres pour valeurs**:
   - Fréquence: FILTER(?frequency > 3)
   - Intensité: FILTER(?intensity = "High")
   - Texte: FILTER(CONTAINS(?name, "Dakota"))

4. **Types de requêtes courantes**:
   - Lister chevaux: ?horse a horses:Horse
   - Lister entraînements: ?training a horses:Training
   - Événements: ?event a horses:SportingEvent
   - Relations: ?horse horses:TrainsIn ?training

5. **Hiérarchies de classes**:
   - Training a des sous-classes (PreparationStage, etc.)
   - SportingEvent a des sous-classes (ShowJumping, etc.)
   - Utiliser rdfs:subClassOf* pour inclure les sous-classes
"""
    
    def generate_sparql(self, question: str, language: str = "fr", debug: bool = False) -> Dict[str, Any]:
        """
        Generate SPARQL query from natural language question
        
        Args:
            question: User's question in natural language
            language: Language (fr/en)
            debug: If True, print raw LLM response
            
        Returns:
            Dictionary with sparql_query, entities_used, relations_used, explanation
        """
        prompt = self._build_generation_prompt(question, language)
        llm_response = self.llm.generate(prompt)
        
        # Debug: show raw response
        if debug:
            print("\n🔍 DEBUG - Réponse brute du LLM:")
            print("=" * 80)
            print(llm_response[:500])
            print("=" * 80 + "\n")
        
        result = self._parse_llm_response(llm_response)
        
        return result
    
    def _build_generation_prompt(self, question: str, language: str) -> str:
        """Build prompt for LLM to generate SPARQL"""
        
        prefixes = get_sparql_prefixes()
        
        # Few-Shot Learning Examples from your 10 questions
        prompt = f"""Tu es un expert en génération de requêtes SPARQL pour une ontologie équestre.

{self.ontology_summary}

QUESTION DE L'UTILISATEUR: {question}

TÂCHE: Génère une requête SPARQL pour répondre à cette question.

RÈGLES CRITIQUES:
1. PAS de clause GRAPH - les données sont dans le graphe par défaut
2. Utiliser ces préfixes:{prefixes}
3. Utiliser OPTIONAL pour propriétés qui peuvent ne pas exister
4. Utiliser FILTER pour conditions (ex: intensity = "High", frequency > 3)
5. Pour sous-classes, utiliser: ?x a/rdfs:subClassOf* horses:Training

EXEMPLES FEW-SHOT (Apprends de ces exemples):

═══════════════════════════════════════════════════════════════

EXEMPLE 1 - Lister les chevaux et leurs entraînements:
Question: "Quel cheval a participé à quelle séance d'entraînement?"

Analyse:
- Classes: Horse, Training
- Relations: TrainsIn
- Propriétés: hasName (optionnel)

SPARQL:
PREFIX horses: <{self.namespace}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?horse ?horseName ?training
WHERE {{
  ?horse rdf:type horses:Horse .
  ?horse horses:TrainsIn ?training .
  ?training rdf:type horses:Training .
  OPTIONAL {{ ?horse horses:hasName ?horseName . }}
}}

═══════════════════════════════════════════════════════════════

EXEMPLE 2 - Filtrer par intensité d'entraînement:
Question: "Quelles séances d'entraînement ont inclus des exercices de haute intensité?"

Analyse:
- Classe: Training
- Propriété: Intensity
- Filtre: Intensity = "High" ou "Peak"

SPARQL:
PREFIX horses: <{self.namespace}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?training ?intensity ?frequency ?volume
WHERE {{
  ?training rdf:type horses:Training .
  ?training horses:Intensity ?intensity .
  FILTER(?intensity = "High" || ?intensity = "Peak")
  OPTIONAL {{ ?training horses:Frequency ?frequency . }}
  OPTIONAL {{ ?training horses:Volume ?volume . }}
}}

═══════════════════════════════════════════════════════════════

EXEMPLE 3 - Couplages cheval-cavalier:
Question: "Quels sont les différents couplages cheval/cavalier?"

Analyse:
- Classes: Horse, Rider
- Relation: AssociatedWith
- Propriétés: hasName pour les deux

SPARQL:
PREFIX horses: <{self.namespace}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?horse ?horseName ?rider ?riderName
WHERE {{
  ?horse rdf:type horses:Horse .
  ?rider rdf:type horses:Rider .
  ?horse horses:AssociatedWith ?rider .
  OPTIONAL {{ ?horse horses:hasName ?horseName . }}
  OPTIONAL {{ ?rider horses:hasName ?riderName . }}
}}

═══════════════════════════════════════════════════════════════

EXEMPLE 4 - Propriétés d'un cheval:
Question: "Quel est la race du cheval?"

Analyse:
- Classe: Horse
- Propriété: hasRace (optionnel), hasName

SPARQL:
PREFIX horses: <{self.namespace}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?horse ?horseName ?race
WHERE {{
  ?horse rdf:type horses:Horse .
  OPTIONAL {{ ?horse horses:hasName ?horseName . }}
  OPTIONAL {{ ?horse horses:hasRace ?race . }}
}}

═══════════════════════════════════════════════════════════════

EXEMPLE 5 - Événements sportifs:
Question: "Quels sont les évènements de la saison compétitive?"

Analyse:
- Classe: SportingEvent (inclut ShowJumping, Dressage, Cross)
- Utiliser sous-classes

SPARQL:
PREFIX horses: <{self.namespace}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?event ?type
WHERE {{
  ?event a ?type .
  ?type rdfs:subClassOf* horses:SportingEvent .
}}

═══════════════════════════════════════════════════════════════

EXEMPLE 6 - Fréquence d'entraînement:
Question: "Quel est la fréquence d'entrainement?"

Analyse:
- Classe: Training
- Propriété: Frequency

SPARQL:
PREFIX horses: <{self.namespace}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?training ?frequency ?intensity
WHERE {{
  ?training rdf:type horses:Training .
  ?training horses:Frequency ?frequency .
  OPTIONAL {{ ?training horses:Intensity ?intensity . }}
}}
ORDER BY DESC(?frequency)

═══════════════════════════════════════════════════════════════

EXEMPLE 7 - Capteurs attachés:
Question: "Quels capteurs sont attachés aux chevaux?"

Analyse:
- Classes: Horse, Sensor (ExperimentalDevices)
- Relation: isAttachedTo

SPARQL:
PREFIX horses: <{self.namespace}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?horse ?horseName ?sensor ?sensorID
WHERE {{
  ?horse rdf:type horses:Horse .
  ?sensor rdf:type horses:InertialSensors .
  ?horse horses:isAttachedTo ?sensor .
  OPTIONAL {{ ?horse horses:hasName ?horseName . }}
  OPTIONAL {{ ?sensor horses:hasSensorID ?sensorID . }}
}}

═══════════════════════════════════════════════════════════════

EXEMPLE 8 - Événements et entraînements liés:
Question: "Quels entraînements dépendent de quel événement?"

Analyse:
- Classes: Training, SportingEvent
- Relation: dependsOn

SPARQL:
PREFIX horses: <{self.namespace}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?training ?event ?intensity
WHERE {{
  ?training rdf:type horses:Training .
  ?event rdf:type horses:SportingEvent .
  ?training horses:dependsOn ?event .
  OPTIONAL {{ ?training horses:Intensity ?intensity . }}
}}

═══════════════════════════════════════════════════════════════

MAINTENANT, génère une requête SPARQL pour: "{question}"

ANALYSE:
- Quelles classes sont nécessaires?
- Quelles propriétés?
- Quelles relations?
- Quels filtres?

Réponds UNIQUEMENT avec un objet JSON valide (PAS de texte avant ou après, PAS de ```json):

{{
  "sparql_query": "PREFIX horses: <{self.namespace}>\\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\\n\\nSELECT ?variable\\nWHERE {{\\n  ?variable rdf:type horses:ClassName .\\n}}",
  "entities_used": ["Horse", "Training"],
  "relations_used": ["TrainsIn", "hasName"],
  "explanation": "Explication courte en français de ce que fait la requête"
}}

RÈGLES JSON:
- NE génère QUE le JSON, rien d'autre
- Utilise \\n pour les retours à ligne
- Utilise {{{{ et }}}} pour les accolades dans SPARQL
- Le JSON doit être parsable directement
- RAPPEL: PAS de clause GRAPH dans la requête!
"""
        
        return prompt
    
    def _parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response to extract SPARQL"""
        try:
            # Clean response
            cleaned = llm_response.strip()
            
            # Remove markdown if present
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            result = json.loads(cleaned)
            
            # Unescape newlines and tabs
            if "sparql_query" in result and isinstance(result["sparql_query"], str):
                result["sparql_query"] = result["sparql_query"].replace("\\n", "\n")
                result["sparql_query"] = result["sparql_query"].replace("\\t", "\t")
            
            # Validate required fields
            if "sparql_query" not in result or not result["sparql_query"].strip():
                print(" Pas de requête SPARQL dans JSON, extraction manuelle...")
                result["sparql_query"] = self._extract_sparql_fallback(llm_response)
            
            if "entities_used" not in result:
                result["entities_used"] = []
            
            if "relations_used" not in result:
                result["relations_used"] = []
            
            if "explanation" not in result:
                result["explanation"] = "Requête générée"
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Erreur parsing JSON: {e}")
            print("Extraction manuelle de la requête SPARQL...")
            return {
                "sparql_query": self._extract_sparql_fallback(llm_response),
                "entities_used": [],
                "relations_used": [],
                "explanation": "Requête extraite (JSON invalide)"
            }
    
    def _extract_sparql_fallback(self, text: str) -> str:
        """Extract SPARQL from unstructured text as fallback"""
        # Try to find SPARQL pattern
        patterns = [
            r'(PREFIX.*?SELECT.*?WHERE\s*\{.*?\})',
            r'(SELECT.*?WHERE\s*\{.*?\})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                # Unescape if needed
                query = query.replace("\\n", "\n").replace("\\t", "\t")
                return query
        
        # Return basic fallback query
        return f"""
PREFIX horses: <{self.namespace}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?subject ?predicate ?object
WHERE {{
  ?subject ?predicate ?object .
}}
LIMIT 10
"""


if __name__ == "__main__":
    print("Intelligent SPARQL Generator loaded (updated for new equestrian KG)")
    print(f"   Namespace: {ONTOLOGY_NAMESPACE}")
    print("   Features: Few-Shot Learning, No Named Graphs, 8 Examples")
