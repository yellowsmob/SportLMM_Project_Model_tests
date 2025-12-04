from langchain_community.graphs import Neo4jGraph
from langchain.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

class GraphRAGSystem:
    def __init__(self, neo4j_uri, neo4j_user, neo4j_password, model_name="qwen2.5:1.5b"):
        """
        Initialise le système Graph RAG avec Ollama
        
        Args:
            neo4j_uri: URI de connexion Neo4j
            neo4j_user: Nom d'utilisateur Neo4j
            neo4j_password: Mot de passe Neo4j
            model_name: Nom du modèle Ollama (par défaut: qwen2.5:1.5b)
        """
        print("Connexion à Neo4j...")
        self.graph = Neo4jGraph(
            url=neo4j_uri,
            username=neo4j_user,
            password=neo4j_password
        )
        print("Connecté à Neo4j!")
        
        print(f"Chargement du modèle {model_name} via Ollama...")
        self.llm = Ollama(
            model=model_name,
            temperature=0.1
        )
        print("Modèle chargé!")
        
        # Créer le prompt en français
        self.cypher_prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template="""Tu es un expert en bases de données de graphes Neo4j. 
Voici le schéma de la base de données :
{schema}

Question en français : {question}

Génère UNIQUEMENT une requête Cypher valide pour répondre à cette question.
Ne fournis AUCUNE explication, juste la requête Cypher.
La requête doit être en anglais (syntaxe Cypher) mais peut chercher des données en français.

Requête Cypher:"""
        )
        
        # Créer la chaîne GraphCypherQA
        self.qa_chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True,
            return_intermediate_steps=True,
            cypher_prompt=self.cypher_prompt
        )
    
    def get_schema(self):
        """Affiche le schéma du graphe"""
        print("\nSchéma du Graphe Neo4j:")
        print(self.graph.schema)
        return self.graph.schema
    
    def query(self, question):
        """Pose une question au système Graph RAG"""
        print(f"\n Question: {question}")
        print("="*80)
        
        try:
            result = self.qa_chain.invoke({"query": question})
            
            print("\nRésultat:")
            print(f"Réponse: {result['result']}")
            
            if 'intermediate_steps' in result:
                print(f"\n🔍 Requête Cypher générée:")
                print(result['intermediate_steps'][0]['query'])
                
                print(f"\n💾 Résultats de la base:")
                print(result['intermediate_steps'][1])
            
            return result
        
        except Exception as e:
            print(f"Erreur: {str(e)}")
            return {"error": str(e)}
    
    def test_connection(self):
        """Test la connexion à Neo4j"""
        try:
            result = self.graph.query("MATCH (n) RETURN count(n) as count")
            print(f"Connexion réussie! Nombre de nœuds: {result[0]['count']}")
            return True
        except Exception as e:
            print(f"Erreur de connexion: {str(e)}")
            return False


def main():
    # ===== CONFIGURATION =====
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "neo4jamira" 
    MODEL_NAME = "qwen2.5:1.5b"  # Modèle Ollama
    
    # Initialiser le système
    print("Initialisation du système Graph RAG...")
    system = GraphRAGSystem(
        neo4j_uri=NEO4J_URI,
        neo4j_user=NEO4J_USER,
        neo4j_password=NEO4J_PASSWORD,
        model_name=MODEL_NAME
    )
    
    # Tester la connexion
    if not system.test_connection():
        print("Impossible de se connecter à Neo4j.")
        return
    
    # Afficher le schéma
    system.get_schema()
    
    # Questions de test
    questions = [
        "Quel cheval a participé à quelle séance d'entraînement ?",
        "Quelles séances d'entraînement ont inclus des exercices de haute intensité ?",
        "Quelles sont les données collectées durant un entrainement ?",
        "Quels sont les événements de la saison compétitive ?",
        "Quel est la fréquence d'entrainement ?",
        "Quels sont les différents couplage cheval/cavalier ?",
        "Quel est le classement ?",
        "Quelles sont les différents acteurs qui interviennent dans l'entrainement ?",
        "Quel est la race du cheval ?"
    ]
    
    # Tester chaque question
    print("\n" + "="*80)
    print("DÉBUT DES TESTS")
    print("="*80)
    
    for i, question in enumerate(questions, 1):
        print(f"\n\n{'='*80}")
        print(f"TEST {i}/{len(questions)}")
        print(f"{'='*80}")
        
        system.query(question)
        
        input("\nAppuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    main()