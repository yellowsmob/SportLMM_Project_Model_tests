# config.py
"""
Configuration Module - Equestrian Knowledge Graph Chatbot
==========================================================

PURPOSE:
--------
This file centralizes ALL configuration settings for the chatbot.
It loads settings from the .env file and provides them to other modules.

WHY THIS EXISTS:
----------------
Instead of hardcoding values in multiple files, we put everything here.
This makes it easy to change settings without modifying code.

HOW IT WORKS:
-------------
1. Loads environment variables from .env file using python-dotenv
2. Provides default values if variables are missing
3. Validates configuration on startup
4. Exports settings for other modules to import

USAGE IN OTHER FILES:
---------------------
    from config import GRAPHDB_ENDPOINT, LOCAL_LLM_MODEL
    
    client = GraphDBClient(GRAPHDB_ENDPOINT)
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# LLM CONFIGURATION
# ============================================================================

USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
LOCAL_LLM_ENDPOINT = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:1234/v1")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "Meta-Llama-3.1-8B-Instruct-GGUF")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# ============================================================================
# GRAPHDB CONFIGURATION
# ============================================================================

GRAPHDB_ENDPOINT = os.getenv(
    "GRAPHDB_ENDPOINT", 
    "http://localhost:7200/repositories/horse-knowledge-graph"
)

ONTOLOGY_GRAPH = os.getenv("ONTOLOGY_GRAPH", "http://example.org/ontology")
INSTANCES_GRAPH = os.getenv("INSTANCES_GRAPH", "http://example.org/instances")

# ============================================================================
# ONTOLOGY CONFIGURATION
# ============================================================================

ONTOLOGY_NAMESPACE = os.getenv(
    "ONTOLOGY_NAMESPACE",
    "http://www.semanticweb.org/noamaadra/ontologies/2024/2/Horses#"
)

BASE_URI = os.getenv("BASE_URI", "http://example.org/horse-ontology#")

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "fr")
VERBOSE = os.getenv("VERBOSE", "true").lower() == "true"
SHOW_SPARQL = os.getenv("SHOW_SPARQL", "true").lower() == "true"
SHOW_CONTEXT = os.getenv("SHOW_CONTEXT", "true").lower() == "true"

# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "false").lower() == "true"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/chatbot.log")

Path("logs").mkdir(exist_ok=True)

# ============================================================================
# FUNCTIONS
# ============================================================================

def validate_config():
    """Validate configuration"""
    errors = []
    
    if USE_LOCAL_LLM:
        if not LOCAL_LLM_ENDPOINT:
            errors.append("LOCAL_LLM_ENDPOINT is not set")
        if not LOCAL_LLM_MODEL:
            errors.append("LOCAL_LLM_MODEL is not set")
    
    if not GRAPHDB_ENDPOINT:
        errors.append("GRAPHDB_ENDPOINT is not set")
    
    if not ONTOLOGY_NAMESPACE:
        errors.append("ONTOLOGY_NAMESPACE is not set")
    
    if DEFAULT_LANGUAGE not in ['fr', 'en']:
        errors.append("DEFAULT_LANGUAGE must be 'fr' or 'en'")
    
    if errors:
        print("\nConfiguration Errors:")
        for error in errors:
            print(f"   {error}")
        print()
        return False
    
    return True


def print_config():
    """Print current configuration"""
    print("\n" + "="*80)
    print("🐴 EQUESTRIAN CHATBOT - CONFIGURATION")
    print("="*80)
    
    print("\n LLM Settings:")
    print(f"   Provider:        {'🖥️  Local (LM Studio)' if USE_LOCAL_LLM else '☁️  OpenAI'}")
    if USE_LOCAL_LLM:
        print(f"   Endpoint:        {LOCAL_LLM_ENDPOINT}")
        print(f"   Model:           {LOCAL_LLM_MODEL}")
    print(f"   Temperature:     {LLM_TEMPERATURE}")
    print(f"   Max Tokens:      {LLM_MAX_TOKENS}")
    
    print("\n GraphDB Settings:")
    print(f"   Endpoint:        {GRAPHDB_ENDPOINT}")
    print(f"   Ontology Graph:  {ONTOLOGY_GRAPH}")
    print(f"   Instances Graph: {INSTANCES_GRAPH}")
    
    print("\n Ontology Settings:")
    print(f"   Namespace:       {ONTOLOGY_NAMESPACE}")
    
    print("\n Application:")
    print(f"   Language:        {DEFAULT_LANGUAGE.upper()}")
    print(f"   Verbose:         {'✅' if VERBOSE else '❌'}")
    
    print("="*80 + "\n")


def get_sparql_prefixes():
    """Generate SPARQL prefixes"""
    return f"""
PREFIX horses: <{ONTOLOGY_NAMESPACE}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""


if __name__ == "__main__":
    print_config()
    
    if validate_config():
        print(" Configuration is valid!")
    else:
        print(" Configuration has errors")
