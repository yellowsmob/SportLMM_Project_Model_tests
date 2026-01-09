# graphdb_client.py
"""
GraphDB Client - Handles SPARQL queries to GraphDB
"""

import requests
from typing import Dict, Any
from config import GRAPHDB_ENDPOINT, REQUEST_TIMEOUT


class GraphDBClient:
    """Client for executing SPARQL queries on GraphDB"""
    
    def __init__(self, endpoint: str = GRAPHDB_ENDPOINT):
        """
        Initialize GraphDB client
        
        Args:
            endpoint: GraphDB SPARQL endpoint URL
        """
        self.endpoint = endpoint
    
    def query(self, sparql_query: str) -> Dict[str, Any]:
        """
        Execute a SPARQL query on GraphDB
        
        Args:
            sparql_query: SPARQL query string
            
        Returns:
            Dictionary with query results
        """
        try:
            response = requests.post(
                self.endpoint,
                data=sparql_query,
                headers={
                    "Content-Type": "application/sparql-query",
                    "Accept": "application/sparql-results+json"
                },
                timeout=REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            print( "Erreur: Impossible de se connecter à GraphDB")
            print(f"Vérifiez que GraphDB est lancé sur {self.endpoint}")
            return {"results": {"bindings": []}}
            
        except requests.exceptions.Timeout:
            print(f"Erreur: Timeout après {REQUEST_TIMEOUT}s")
            return {"results": {"bindings": []}}
            
        except Exception as e:
            print(f"Erreur lors de l'exécution de la requête: {e}")
            return {"results": {"bindings": []}}
    
    def test_connection(self) -> bool:
        """Test connection to GraphDB"""
        test_query = """
        SELECT (COUNT(*) as ?count)
        WHERE { ?s ?p ?o }
        """
        
        try:
            result = self.query(test_query)
            if result and 'results' in result:
                count = result['results']['bindings'][0]['count']['value']
                print(" Connexion à GraphDB réussie!")
                print(f"{count} triplets trouvés dans le graphe")
                return True
        except:
            pass
        
        print("Impossible de se connecter à GraphDB")
        return False


if __name__ == "__main__":
    print("Test de connexion à GraphDB...")
    
    client = GraphDBClient()
    client.test_connection()
