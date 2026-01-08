import json
import sys
import os
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import requests


class RDFLLMPipeline:
    def __init__(self, rdf_file_path, ollama_model="llama3.2"):
        """
        Initialise la pipeline
        
        Args:
            rdf_file_path: Chemin vers le fichier RDF
            ollama_model: Modèle Ollama à utiliser (par défaut: llama3.2)
        """
        self.rdf_file_path = rdf_file_path
        self.ollama_model = ollama_model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.graph = Graph()
        
    def load_rdf(self):
        """Charge le fichier RDF"""
        print(f"📂 Chargement du fichier RDF: {self.rdf_file_path}")
        try:
            self.graph.parse(self.rdf_file_path)
            print(f"✅ Graph chargé avec succès: {len(self.graph)} triples")
            return True
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return False
    
    def get_graph_statistics(self):
        """Obtient des statistiques sur le graph"""
        stats = {
            "total_triples": len(self.graph),
            "subjects": len(set(self.graph.subjects())),
            "predicates": len(set(self.graph.predicates())),
            "objects": len(set(self.graph.objects()))
        }
        return stats
    
    def get_all_classes(self):
        """Extrait toutes les classes du graph"""
        classes = set()
        for s, p, o in self.graph:
            if p == RDF.type:
                classes.add(str(o))
        return list(classes)
    
    def get_all_predicates(self):
        """Extrait tous les prédicats uniques"""
        predicates = set()
        for s, p, o in self.graph:
            predicates.add(str(p))
        return list(predicates)
    
    def extract_triples_sample(self, limit=50):
        """Extrait un échantillon de triples"""
        triples = []
        for i, (s, p, o) in enumerate(self.graph):
            if i >= limit:
                break
            triples.append({
                "subject": str(s),
                "predicate": str(p),
                "object": str(o)
            })
        return triples
    
    def format_triples_for_llm(self, triples):
        """Formate les triples pour le LLM"""
        formatted = []
        for triple in triples:
            # Simplifie les URIs pour plus de lisibilité
            subject = self._simplify_uri(triple["subject"])
            predicate = self._simplify_uri(triple["predicate"])
            obj = self._simplify_uri(triple["object"])
            formatted.append(f"- {subject} --[{predicate}]--> {obj}")
        return "\n".join(formatted)
    
    def _simplify_uri(self, uri):
        """Simplifie une URI pour la rendre plus lisible"""
        if "#" in uri:
            return uri.split("#")[-1]
        elif "/" in uri:
            return uri.split("/")[-1]
        return uri
    
    def query_sparql(self, sparql_query):
        """Exécute une requête SPARQL"""
        try:
            results = self.graph.query(sparql_query)
            return list(results)
        except Exception as e:
            print(f"❌ Erreur SPARQL: {e}")
            return []
    
    def ask_llm(self, prompt, context="", stream=False):
        """Envoie une question au LLM via Ollama"""
        print(f"\n🤖 Interrogation du modèle {self.ollama_model}...")
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        payload = {
            "model": self.ollama_model,
            "prompt": full_prompt,
            "stream": stream
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "Pas de réponse")
        except requests.exceptions.ConnectionError:
            return "❌ Erreur: Impossible de se connecter à Ollama. Assurez-vous qu'Ollama est lancé (ollama serve)"
        except Exception as e:
            return f"❌ Erreur: {e}"
    
    def analyze_graph_with_llm(self, custom_question=None, limit=50):
        """Analyse le graph avec le LLM"""
        stats = self.get_graph_statistics()
        triples_sample = self.extract_triples_sample(limit=limit)
        triples_text = self.format_triples_for_llm(triples_sample)
        
        context = f"""Tu es un assistant spécialisé dans l'analyse de knowledge graphs RDF.

Voici des informations sur le knowledge graph:
- Nombre total de triples: {stats['total_triples']}
- Nombre de sujets uniques: {stats['subjects']}
- Nombre de prédicats uniques: {stats['predicates']}
- Nombre d'objets uniques: {stats['objects']}

Voici un échantillon de {limit} triples du graph:
{triples_text}
"""
        
        if custom_question:
            question = custom_question
        else:
            question = "Analyse ce knowledge graph et donne-moi un résumé des concepts principaux et des relations que tu observes."
        
        response = self.ask_llm(question, context)
        return response
    
    def interactive_mode(self, limit=100):
        """Mode interactif pour poser des questions"""
        stats = self.get_graph_statistics()
        triples_sample = self.extract_triples_sample(limit=limit)
        triples_text = self.format_triples_for_llm(triples_sample)
        
        context = f"""Tu es un assistant spécialisé dans l'analyse de knowledge graphs RDF.

Statistiques du graph:
- Nombre total de triples: {stats['total_triples']}
- Nombre de sujets: {stats['subjects']}
- Nombre de prédicats: {stats['predicates']}

Échantillon de triples:
{triples_text}
"""
        
        print("\n" + "="*60)
        print("🎯 MODE INTERACTIF - Posez vos questions sur le knowledge graph")
        print("Tapez 'quit' ou 'exit' pour quitter")
        print("="*60 + "\n")
        
        while True:
            question = input("\n❓ Votre question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Au revoir!")
                break
            
            if not question:
                continue
            
            response = self.ask_llm(question, context)
            print(f"\n💬 Réponse:\n{response}")
    
    def export_statistics(self, output_file="graph_stats.json"):
        """Exporte les statistiques du graph en JSON"""
        stats = self.get_graph_statistics()
        stats["classes"] = self.get_all_classes()
        stats["predicates"] = self.get_all_predicates()
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Statistiques exportées: {output_file}")
        return stats


def main(rdf_file_path=None, model_name=None):
    """
    Fonction principale
    
    Args:
        rdf_file_path: Chemin vers le fichier RDF (requis)
        model_name: Nom du modèle Ollama à utiliser (optionnel)
    """
    print("="*60)
    print("🚀 Pipeline RDF + LLM avec Ollama")
    print("="*60)
    
    # Vérifier qu'un fichier est fourni
    if rdf_file_path is None:
        print("\n❌ Erreur: Aucun fichier RDF spécifié")
        print("\nUsage:")
        print("  python rdf_llm_pipeline.py mon_fichier.rdf")
        print("  python rdf_llm_pipeline.py mon_fichier.rdf mistral")
        return
    
    rdf_file = rdf_file_path
    print(f"\n📁 Fichier RDF: {rdf_file}")
    
    # Vérifier que le fichier existe
    if not os.path.exists(rdf_file):
        print(f"❌ Erreur: Le fichier '{rdf_file}' n'existe pas")
        return
    
    # Déterminer le modèle
    if model_name is None:
        model = input("🤖 Modèle Ollama à utiliser (défaut: llama3.2): ").strip() or "llama3.2"
    else:
        model = model_name
        print(f"🤖 Modèle Ollama: {model}")
    
    # Initialiser la pipeline
    pipeline = RDFLLMPipeline(rdf_file, model)
    
    # Charger le RDF
    if not pipeline.load_rdf():
        return
    
    # Afficher les statistiques
    stats = pipeline.get_graph_statistics()
    print("\n📊 Statistiques du graph:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    # Menu
    while True:
        print("\n" + "="*60)
        print("Options:")
        print("1. Analyse automatique du graph")
        print("2. Poser une question spécifique")
        print("3. Mode interactif")
        print("4. Afficher un échantillon de triples")
        print("5. Exporter les statistiques (JSON)")
        print("6. Quitter")
        print("="*60)
        
        choice = input("\nVotre choix: ").strip()
        
        if choice == "1":
            print("\n🔍 Analyse en cours...")
            response = pipeline.analyze_graph_with_llm()
            print(f"\n💬 Analyse:\n{response}")
        
        elif choice == "2":
            question = input("\n❓ Votre question: ").strip()
            if question:
                response = pipeline.analyze_graph_with_llm(question)
                print(f"\n💬 Réponse:\n{response}")
        
        elif choice == "3":
            pipeline.interactive_mode()
        
        elif choice == "4":
            limit = input("Nombre de triples à afficher (défaut: 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            triples = pipeline.extract_triples_sample(limit=limit)
            print("\n📋 Échantillon de triples:")
            print(pipeline.format_triples_for_llm(triples))
        
        elif choice == "5":
            output = input("Nom du fichier de sortie (défaut: graph_stats.json): ").strip()
            output = output if output else "graph_stats.json"
            pipeline.export_statistics(output)
        
        elif choice == "6":
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide")


if __name__ == "__main__":
    rdf_file = None
    model = None
    
    if len(sys.argv) > 1:
        rdf_file = sys.argv[1]
        # Vérifier que le fichier existe
        if not os.path.exists(rdf_file):
            print(f"❌ Erreur: Le fichier '{rdf_file}' n'existe pas")
            print(f"📍 Chemin absolu recherché: {os.path.abspath(rdf_file)}")
            sys.exit(1)
        print(f"📁 Fichier RDF fourni en argument: {rdf_file}")
    
    if len(sys.argv) > 2:
        model = sys.argv[2]
        print(f"🤖 Modèle fourni en argument: {model}")
    
    main(rdf_file_path=rdf_file, model_name=model)
