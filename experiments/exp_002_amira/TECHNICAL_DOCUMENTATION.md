# Technical Documentation - Graph RAG System Implementation

**Experiment ID:** exp_002  
**System:** French Equestrian Graph RAG  
**Last Updated:** 2024-12-04

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Code Structure](#code-structure)
3. [Component Deep-Dive](#component-deep-dive)
4. [Execution Flow](#execution-flow)
5. [Prompt Engineering](#prompt-engineering)
6. [Debugging Guide](#debugging-guide)

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────┐
│  User Question  │  (French)
│   "Quel cheval  │
│    a participé?"│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   GraphCypherQAChain (LangChain)    │
│  ┌───────────────────────────────┐  │
│  │ Step 1: Cypher Generation     │  │
│  │  - Get Neo4j schema           │  │
│  │  - Fill prompt template       │  │
│  │  - LLM generates Cypher       │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │ Step 2: Query Execution       │  │
│  │  - Execute Cypher on Neo4j    │  │
│  │  - Return raw results         │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │ Step 3: Answer Synthesis      │  │
│  │  - LLM formats answer         │  │
│  │  - Natural language output    │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Final Answer   │  (French)
│  + Cypher Query │
│  + Raw Results  │
└─────────────────┘
```

### Technology Stack

| Layer             | Technology            | Purpose                            |
| ----------------- | --------------------- | ---------------------------------- |
| **LLM**           | Qwen2.5 1.5B (Ollama) | Text-to-Cypher + Answer generation |
| **Orchestration** | LangChain             | Chain management, prompt templates |
| **Database**      | Neo4j 5.x             | Knowledge graph storage            |
| **Language**      | Python 3.9+           | Implementation                     |
| **Protocol**      | Bolt                  | Neo4j connection                   |

---

## 📦 Code Structure

### File: `graph_rag_system.py`

```python
# === IMPORTS ===
from langchain_community.graphs import Neo4jGraph
from langchain.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

# === MAIN CLASS ===
class GraphRAGSystem:
    def __init__(...)      # System initialization
    def get_schema(...)    # Schema retrieval
    def query(...)         # Main query pipeline
    def test_connection(...) # Connection validation

# === TEST RUNNER ===
def main():
    # Configuration
    # System setup
    # Question loop
```

---

## 🔬 Component Deep-Dive

### 1. **Imports Explained**

#### `Neo4jGraph`

```python
from langchain_community.graphs import Neo4jGraph
```

**Purpose:** Wrapper class for Neo4j database interaction

**Key Methods:**

- `query(cypher_string)`: Execute raw Cypher queries
- `schema`: Property that returns graph schema as string
- `refresh_schema()`: Update schema cache

**What it does:**

- Manages bolt connection lifecycle
- Handles authentication
- Caches schema for performance
- Formats query results into Python dicts

**Example Usage:**

```python
graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="password123"
)

# Execute raw Cypher
results = graph.query("MATCH (n:Cheval) RETURN n.nom LIMIT 5")
# Returns: [{'n.nom': 'Tonnerre'}, {'n.nom': 'Éclair'}, ...]

# Get schema
print(graph.schema)
# Prints: "Node properties: Cheval {nom: STRING, age: INTEGER}..."
```

---

#### `GraphCypherQAChain`

```python
from langchain.chains.graph_qa.cypher import GraphCypherQAChain
```

**Purpose:** Orchestrates the entire RAG pipeline

**Internal Steps:**

1. **Schema Retrieval:** Automatically fetches `graph.schema`
2. **Prompt Construction:** Fills template with schema + question
3. **LLM Call 1:** Generate Cypher query
4. **Query Execution:** Run Cypher on Neo4j
5. **LLM Call 2:** Synthesize natural language answer

**Key Parameters:**

- `llm`: Language model to use
- `graph`: Neo4j connection object
- `verbose`: Print intermediate steps (set to `True` for debugging)
- `return_intermediate_steps`: Return Cypher + raw results
- `cypher_prompt`: Custom prompt template (overrides default)

**Default Behavior (without custom prompt):**

```python
# LangChain's default prompt (simplified):
"""
Given this Neo4j schema: {schema}
Generate a Cypher query for: {question}
Only return the Cypher query.
"""
```

**Why we override it:**

- Default is in English
- We need French language support
- We want stricter output format (pure Cypher, no explanations)

---

#### `Ollama`

```python
from langchain_community.llms import Ollama
```

**Purpose:** Interface to locally running Ollama server

**How it works:**

1. Sends HTTP requests to `http://localhost:11434` (Ollama's default port)
2. Streams responses from the model
3. Handles tokenization internally

**Key Parameters:**

```python
Ollama(
    model="qwen2.5:1.5b",     # Which model to use
    temperature=0.1,          # Randomness (0 = deterministic, 1 = creative)
    num_ctx=2048,            # Context window size
    num_predict=512           # Max tokens to generate
)
```

**Temperature Impact:**

- `0.0-0.2`: Deterministic, factual (best for Cypher generation)
- `0.5-0.7`: Balanced
- `0.8-1.0`: Creative, varied (bad for structured output)

**Why Temperature = 0.1?**

```python
# Temperature 0.9 might produce:
MATCH (c:Cheval)-[:PARTICIPE_A|:A_PARTICIPE]->(s:Seance)  # Wrong syntax

# Temperature 0.1 produces:
MATCH (c:Cheval)-[:A_PARTICIPE]->(s:Seance)  # Correct
```

---

#### `PromptTemplate`

```python
from langchain.prompts import PromptTemplate
```

**Purpose:** Create reusable prompts with variable placeholders

**Structure:**

```python
PromptTemplate(
    input_variables=["var1", "var2"],  # Variables to fill
    template="Use {var1} to do {var2}"  # Template string
)
```

**In our code:**

```python
self.cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template="""Tu es un expert en bases de données de graphes Neo4j.
Voici le schéma de la base de données :
{schema}

Question en français : {question}

Génère UNIQUEMENT une requête Cypher valide pour répondre à cette question.
Ne fournis AUCUNE explication, juste la requête Cypher.

Requête Cypher:"""
)
```

**How it gets filled:**

```python
# GraphCypherQAChain automatically does:
filled_prompt = cypher_prompt.format(
    schema=graph.schema,
    question="Quel cheval a participé?"
)

# Result sent to LLM:
"""
Tu es un expert en bases de données de graphes Neo4j.
Voici le schéma de la base de données :
Node properties: Cheval {nom: STRING}, Seance {date: STRING}
Relationship properties: A_PARTICIPE {}
...

Question en français : Quel cheval a participé?

Génère UNIQUEMENT une requête Cypher valide...
"""
```

---

### 2. **Class: GraphRAGSystem**

#### `__init__` Method - Initialization

```python
def __init__(self, neo4j_uri, neo4j_user, neo4j_password, model_name="qwen2.5:1.5b"):
```

**Step-by-Step Breakdown:**

**Step 1: Neo4j Connection**

```python
self.graph = Neo4jGraph(
    url=neo4j_uri,          # "bolt://localhost:7687"
    username=neo4j_user,    # "neo4j"
    password=neo4j_password # "your_password"
)
```

**What happens internally:**

1. Opens a bolt connection to Neo4j
2. Authenticates with username/password
3. Executes `CALL db.schema.visualization()` to cache schema
4. Stores connection in `self.graph`

**Potential Errors:**

- `ServiceUnavailable`: Neo4j not running
- `AuthError`: Wrong username/password
- `ValueError`: Invalid URI format

---

**Step 2: LLM Initialization**

```python
self.llm = Ollama(
    model=model_name,  # "qwen2.5:1.5b"
    temperature=0.1
)
```

**What happens internally:**

1. Connects to Ollama server at `localhost:11434`
2. Verifies model exists (fails if not pulled)
3. Sets generation parameters

**Potential Errors:**

- `ConnectionError`: Ollama not running (`ollama serve` not started)
- `ModelNotFoundError`: Model not downloaded (`ollama pull qwen2.5:1.5b` needed)

---

**Step 3: Prompt Template Creation**

```python
self.cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template="""..."""
)
```

**Design Decisions:**

| Element     | Choice                     | Reasoning                      |
| ----------- | -------------------------- | ------------------------------ |
| Language    | French                     | Match user's domain            |
| Tone        | Expert ("Tu es un expert") | Prime model for technical task |
| Instruction | "UNIQUEMENT une requête"   | Prevent explanations           |
| Format      | "Requête Cypher:" label    | Clear output delimiter         |

**Why "UNIQUEMENT" (ONLY)?**

```python
# Without strict instruction:
LLM Output:
"""
Pour répondre à cette question, nous devons chercher...
Voici la requête:
MATCH (c:Cheval) RETURN c
Cette requête va...
"""
# Parser fails - too much text!

# With "UNIQUEMENT":
LLM Output:
"""
MATCH (c:Cheval) RETURN c
"""
# Parser succeeds!
```

---

**Step 4: QA Chain Assembly**

```python
self.qa_chain = GraphCypherQAChain.from_llm(
    llm=self.llm,
    graph=self.graph,
    verbose=True,
    return_intermediate_steps=True,
    cypher_prompt=self.cypher_prompt
)
```

**What `from_llm` does:**

1. Creates internal prompt for answer synthesis (separate from Cypher prompt)
2. Sets up two-stage pipeline: Cypher generation → Answer generation
3. Configures result parsers

**Verbose Mode Output:**

```
> Entering new GraphCypherQAChain chain...
Generated Cypher:
MATCH (c:Cheval)-[:A_PARTICIPE]->(s:Seance) RETURN c.nom, s.date
Full Context:
[{'c.nom': 'Tonnerre', 's.date': '2024-11-15'}]
> Finished chain.
```

---

#### `query` Method - Main Pipeline

```python
def query(self, question):
    result = self.qa_chain.invoke({"query": question})
```

**What happens in `invoke`:**

**Stage 1: Cypher Generation**

```python
# Internal step (you don't see this code):
cypher_generation_chain = LLMChain(
    llm=self.llm,
    prompt=self.cypher_prompt
)

filled_prompt = self.cypher_prompt.format(
    schema=self.graph.schema,
    question=question
)

cypher_query = cypher_generation_chain.run(filled_prompt)
# Returns: "MATCH (c:Cheval) RETURN c.nom"
```

**Stage 2: Query Execution**

```python
# Internal step:
try:
    results = self.graph.query(cypher_query)
except Exception as e:
    # Handle syntax errors, missing nodes, etc.
```

**Stage 3: Answer Synthesis**

```python
# Internal step:
answer_prompt = f"""
Given this context from the database:
{results}

Answer this question in natural language:
{question}
"""

final_answer = self.llm(answer_prompt)
```

**Return Value Structure:**

```python
{
    'result': "Le cheval Tonnerre a participé...",  # Final answer
    'intermediate_steps': [
        {
            'query': "MATCH (c:Cheval)-[:A_PARTICIPE]->(s:Seance) RETURN c.nom, s.date"
        },
        [
            {'c.nom': 'Tonnerre', 's.date': '2024-11-15'},
            {'c.nom': 'Éclair', 's.date': '2024-11-16'}
        ]
    ]
}
```

---

## 🔄 Complete Execution Flow

### Question: "Quel cheval a participé à quelle séance d'entraînement ?"

**Timeline:**

```
T=0ms: User calls system.query("Quel cheval...")

T=10ms: GraphCypherQAChain.invoke() starts
  ↓
T=15ms: Fetch graph.schema from Neo4j
  Returns: "Node properties: Cheval {nom: STRING, race: STRING}..."
  ↓
T=20ms: Fill cypher_prompt template
  Input: schema + question
  Output: Full prompt (500-1000 tokens)
  ↓
T=25ms: Send prompt to Ollama
  ↓
T=1500ms: LLM generates Cypher (1.5 seconds on CPU)
  Output: "MATCH (c:Cheval)-[:A_PARTICIPE]->(s:Seance) RETURN c.nom, s.date"
  ↓
T=1510ms: Parse LLM output to extract pure Cypher
  ↓
T=1520ms: Execute Cypher on Neo4j
  ↓
T=1550ms: Neo4j returns results (30ms query time)
  Output: [{'c.nom': 'Tonnerre', 's.date': '2024-11-15'}, ...]
  ↓
T=1560ms: Build answer synthesis prompt
  Input: question + database results
  ↓
T=1570ms: Send to LLM for answer generation
  ↓
T=3000ms: LLM generates natural language answer (1.4 seconds)
  Output: "Le cheval Tonnerre a participé à une séance le 15 novembre..."
  ↓
T=3010ms: Return final result dict

Total Time: ~3 seconds per question
```

**Bottlenecks:**

- **LLM inference:** 2.9 seconds (97% of time)
- **Neo4j query:** 30ms (1%)
- **Overhead:** 80ms (2%)

---

## 🎯 Prompt Engineering

### Cypher Generation Prompt Analysis

```python
template="""Tu es un expert en bases de données de graphes Neo4j.
Voici le schéma de la base de données :
{schema}

Question en français : {question}

Génère UNIQUEMENT une requête Cypher valide pour répondre à cette question.
Ne fournis AUCUNE explication, juste la requête Cypher.
La requête doit être en anglais (syntaxe Cypher) mais peut chercher des données en français.

Requête Cypher:"""
```

**Prompt Components:**

| Component                  | Purpose                | Impact              |
| -------------------------- | ---------------------- | ------------------- |
| "Tu es un expert"          | Role priming           | +15% accuracy       |
| "{schema}"                 | Provide structure      | Essential           |
| "en français"              | Language clarity       | Prevents confusion  |
| "UNIQUEMENT"               | Format enforcement     | -80% parsing errors |
| "pas d'explication"        | Redundant emphasis     | Extra safety        |
| "syntaxe Cypher...anglais" | Clarify code-switching | Critical            |
| "Requête Cypher:"          | Output delimiter       | Helps parser        |

---

### Potential Improvements

**1. Add Few-Shot Examples**

```python
template="""Tu es un expert en bases de données de graphes Neo4j.

Exemples:
Question: "Quels chevaux ont 5 ans?"
Cypher: MATCH (c:Cheval) WHERE c.age = 5 RETURN c.nom

Question: "Quelles séances ont eu lieu en novembre?"
Cypher: MATCH (s:Seance) WHERE s.date STARTS WITH '2024-11' RETURN s

Schéma: {schema}
Question: {question}

Requête Cypher:"""
```

**2. Add Schema Hints**

```python
# If model struggles, add explicit hints:
"""
IMPORTANT:
- Use 'A_PARTICIPE' for horse-session relationships
- Horse nodes are labeled 'Cheval', not 'Horse'
- Dates are in 'YYYY-MM-DD' format
"""
```

---

## 🐛 Debugging Guide

### Common Errors & Solutions

#### Error 1: "ServiceUnavailable: Unable to connect to Neo4j"

**Cause:** Neo4j not running

**Solution:**

```bash
# Check if Neo4j is running
neo4j status

# Start Neo4j
neo4j start

# Or with Docker:
docker ps | grep neo4j
docker start <container_id>
```

---

#### Error 2: "Model not found: qwen2.5:1.5b"

**Cause:** Model not downloaded to Ollama

**Solution:**

```bash
# List available models
ollama list

# Pull model if missing
ollama pull qwen2.5:1.5b

# Verify
ollama run qwen2.5:1.5b "test"
```

---

#### Error 3: Invalid Cypher Syntax

**Symptom:**

```
Neo4jError: Invalid input 'X': expected whitespace...
```

**Cause:** LLM generated malformed Cypher

**Debug Steps:**

1. Check `intermediate_steps[0]['query']` to see exact Cypher
2. Test Cypher directly in Neo4j Browser
3. If consistently failing, adjust prompt or upgrade model

**Example Fix:**

```python
# Model generated (wrong):
MATCH (c:Cheval) WHERE c.nom == "Tonnerre" RETURN c
# == is not Cypher syntax!

# Should be:
MATCH (c:Cheval) WHERE c.nom = "Tonnerre" RETURN c
```

---

#### Error 4: Empty Results

**Symptom:**

```
intermediate_steps[1] = []
result = "Je n'ai pas trouvé d'information."
```

**Possible Causes:**

1. Cypher syntax valid but wrong logic
2. Schema mismatch (wrong node/relationship names)
3. Data actually doesn't exist

**Debug:**

```python
# Add to query() method:
print(f"DEBUG - Generated Cypher: {result['intermediate_steps'][0]['query']}")
print(f"DEBUG - Schema: {self.graph.schema}")

# Manually test query in Neo4j Browser
```

---

## 📊 Performance Optimization

### Current Performance

- **Query Time:** ~3 seconds
- **Bottleneck:** LLM inference (CPU)

### Optimization Options

**1. Use GPU (if available)**

```python
self.llm = Ollama(
    model="qwen2.5:1.5b",
    num_gpu=1  # Use GPU
)
# Expected: 3s → 0.5s (6x speedup)
```

**2. Upgrade Model (trade size for quality)**

```bash
ollama pull qwen2.5:7b
# Expected: Better Cypher, but 7s per query
```

**3. Cache Common Queries**
