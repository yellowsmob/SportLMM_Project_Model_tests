"""
Nouveau script pour charger les données RDF avec toutes les propriétés
"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from rdflib import Graph, Namespace, RDF, RDFS, Literal

# Charger .env
load_dotenv()

# Configuration
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

print(f"📊 Connexion à Neo4j: {neo4j_uri}")

# Charger RDF
print("📥 Chargement du fichier RDF...")
rdf_graph = Graph()
rdf_graph.parse("Horse_generatedDataV2.rdf", format="xml")

HORSES = Namespace("http://www.semanticweb.org/noamaadra/ontologies/2024/2/Horses#")

# Connexion Neo4j
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

def clean_uri(uri):
    """Extrait le nom court"""
    return str(uri).split('#')[-1] if '#' in str(uri) else str(uri).split('/')[-1]

def get_value(obj):
    """Extrait la valeur"""
    if isinstance(obj, Literal):
        return obj.toPython()
    return clean_uri(obj)

with driver.session() as session:
    # Nettoyer
    print("🗑️  Nettoyage...")
    session.run("MATCH (n) DETACH DELETE n")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Resource) REQUIRE n.uri IS UNIQUE")
    
    print("📦 Création des nœuds avec propriétés...")
    
    # Traiter chaque sujet
    for subj in rdf_graph.subjects():
        subj_str = str(subj)
        if 'www.w3.org' in subj_str:
            continue
        
        # Types/Labels
        types = list(rdf_graph.objects(subj, RDF.type))
        labels = [clean_uri(t) for t in types if 'Horses#' in str(t)]
        if not labels:
            labels = ['Resource']
        
        # Propriétés
        short_name = clean_uri(subj)
        properties = {
            'uri': subj_str,
            'id': short_name  # Identifiant court pour les requêtes
        }
        
        for pred, obj in rdf_graph.predicate_objects(subj):
            if pred == RDF.type or 'www.w3.org' in str(pred):
                continue
            
            if isinstance(obj, Literal):
                pred_name = clean_uri(pred)
                properties[pred_name] = get_value(obj)
        
        # Créer nœud
        labels_cypher = ':'.join(labels)
        session.run(f"MERGE (n:{labels_cypher} {{uri: $uri}}) SET n = $props", 
                   uri=subj_str, props=properties)
    
    print("🔗 Création des relations...")
    
    # Relations
    for subj, pred, obj in rdf_graph:
        if isinstance(obj, Literal) or 'www.w3.org' in str(pred):
            continue
        
        subj_str = str(subj)
        obj_str = str(obj)
        
        if 'www.w3.org' in subj_str or 'www.w3.org' in obj_str:
            continue
        
        pred_name = clean_uri(pred).upper()
        
        session.run(f"""
        MATCH (a {{uri: $subj}})
        MATCH (b {{uri: $obj}})
        MERGE (a)-[:{pred_name}]->(b)
        """, subj=subj_str, obj=obj_str)
    
    # Stats
    result = session.run("MATCH (n) RETURN count(n) as total")
    total = result.single()['total']
    result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
    total_rel = result.single()['total']
    
    print(f"✅ Terminé!")
    print(f"📈 Nœuds: {total}")
    print(f"🔗 Relations: {total_rel}")
    
    # Vérifier Horse1 et Horse2
    print("\n🐴 Vérification des chevaux:")
    result = session.run("""
    MATCH (h:Horse)
    RETURN h.id as id, h.hasName as name, h.hasRace as race
    ORDER BY h.id
    """)
    for rec in result:
        print(f"  {rec['id']}: {rec['name']} ({rec['race']})")

driver.close()
