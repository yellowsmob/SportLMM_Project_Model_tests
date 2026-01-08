from kg_llm import RDFLLMPipeline, create_example_rdf
import os

def test_pipeline():
    """Test simple de la pipeline"""
    
    print("="*60)
    print("Test de la Pipeline RDF + LLM")
    print("="*60)
    
    # 1. Créer un fichier RDF d'exemple
    print("\n1️Création d'un fichier RDF d'exemple...")
    create_example_rdf()
    rdf_file = "/home/claude/example_knowledge_graph.rdf"
    
    if not os.path.exists(rdf_file):
        print("Erreur: Le fichier d'exemple n'a pas été créé")
        return
    
    print(f"✅ Fichier créé: {rdf_file}")
    
    # 2. Initialiser la pipeline
    print("\n2️⃣ Initialisation de la pipeline...")
    pipeline = RDFLLMPipeline(rdf_file, ollama_model="llama3.2")
    
    # 3. Charger le fichier RDF
    print("\n3️⃣ Chargement du fichier RDF...")
    if not pipeline.load_rdf():
        print("❌ Erreur lors du chargement")
        return
    
    # 4. Afficher les statistiques
    print("\n4️⃣ Statistiques du graph:")
    stats = pipeline.get_graph_statistics()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    # 5. Extraire un échantillon
    print("\n5️⃣ Échantillon de triples:")
    triples = pipeline.extract_triples_sample(limit=10)
    print(pipeline.format_triples_for_llm(triples))
    
    # 6. Test d'une question au LLM
    print("\n6️⃣ Test d'une question au LLM...")
    response = pipeline.analyze_graph_with_llm(
        "Donne-moi un résumé très court de ce graph en 2 phrases maximum."
    )
    print(f"\n💬 Réponse du LLM:\n{response}")
    
    print("\n" + "="*60)
    print("✅ Test terminé avec succès!")
    print("="*60)

if __name__ == "__main__":
    test_pipeline()
