# Experiment 002 - French Equestrian Graph RAG with Qwen2.5

**Date:** 2024-12-04  
**Author:** Amira  
**Status:** 🔄 In Progress

---

## 🎯 Objective

Build and test a **Graph RAG (Retrieval-Augmented Generation)** system for analyzing equestrian training performance data stored in a Neo4j knowledge graph. The system should:

1. Accept natural language questions **in French**
2. Generate valid **Cypher queries** automatically using an LLM
3. Execute queries on the Neo4j database
4. Return natural language answers in French

**Key Innovation:** Using a lightweight local model (Qwen2.5 1.5B) instead of cloud APIs to reduce costs and maintain data privacy.

---

## 🤖 Model Used

- **Model:** Qwen2.5 1.5B Instruct
- **Quantization:** Q4_0 GGUF (4-bit quantization for efficiency)
- **Provider:** Ollama (local deployment)
- **Temperature:** 0.1 (very low for deterministic query generation)
- **Max Tokens:** 512
- **Context Window:** 2048 tokens

**Why this model?**

- **Lightweight:** Runs on modest hardware without GPU
- **Local:** No API costs, full data privacy
- **Multilingual:** Supports French (our domain language)
- **Risk:** 1.5B parameters might struggle with complex Cypher syntax

---

## 📊 Dataset

### Knowledge Graph Schema

- **Database:** Neo4j 5.x (local instance)
- **Domain:** Equestrian training performance analysis
- **Language:** French (node labels, properties, relationships in French)

### Node Types (Labels)

- `Cheval` (Horse)
- `Seance` (Training Session)
- `Exercice` (Exercise)
- `Cavalier` (Rider)
- `Evenement` (Competitive Event)
- `Donnee` (Data/Metrics)
- `ParametrePhysiologique` (Physiological Parameter)
- `Acteur` (Stakeholder)

### Test Data

- **Type:** Custom test set with 9 predefined questions
- **Language:** French
- **Focus Areas:**
  - Training session participation
  - Exercise intensity analysis
  - Physiological correlations
  - Data collection details
  - Competitive event scheduling
  - Training frequency
  - Horse-rider pairings
  - Performance rankings
  - Stakeholder involvement
  - Horse breed information

---

## 🛠️ Setup Instructions

### Prerequisites

```bash
# 1. Install Python dependencies
pip install langchain langchain-community neo4j

# 2. Install and start Ollama
# Download from: https://ollama.com/download
ollama pull qwen2.5:1.5b

# 3. Start Neo4j
# Option A: Neo4j Desktop (download from neo4j.com)
# Option B: Docker
docker run -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/your_password neo4j:latest
```

### Running the Experiment

```bash
# Navigate to experiment directory
cd experiments/exp_002_amira/code

# Run the main script
python graph_rag_system.py
```

### Configuration

Edit the following in `graph_rag_system.py`:

```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password"  # Update this
MODEL_NAME = "qwen2.5:1.5b"
```

---

## 📁 Project Structure

```
experiments/exp_002_amira/
├── config.yaml              # Experiment configuration
├── README.md                # This file (overview)
├── TECHNICAL_DOCUMENTATION.md  # Detailed code explanation
├── code/
│   ├── graph_rag_system.py  # Main implementation
│   ├── test_imports.py      # Dependency verification
│   └── check_schema.py      # Neo4j schema inspection
├── results/
│   ├── test_run_001.log     # First test run logs
│   └── cypher_queries.txt   # Generated queries
└── notes/
    └── observations.md      # Development notes
```

---

## 📈 Results

### Expected Metrics

- [ ] **Query Generation Success Rate:** % of questions that produce valid Cypher
- [ ] **Execution Success Rate:** % of valid queries that run without errors
- [ ] **Answer Quality:** Manual assessment (1-5 scale)
- [ ] **Response Time:** Average time per question
- [ ] **Intermediate Steps Transparency:** Can we trace LLM reasoning?

### Preliminary Observations

_[To be filled after running tests]_

**Sample Output Structure:**

```
Question: "Quel cheval a participé à quelle séance d'entraînement ?"

Generated Cypher:
MATCH (c:Cheval)-[r:A_PARTICIPE]->(s:Seance)
RETURN c.nom, s.date, s.type

Raw Results:
[{'c.nom': 'Tonnerre', 's.date': '2024-11-15', 's.type': 'Dressage'}, ...]

Final Answer:
"Le cheval Tonnerre a participé à une séance de dressage le 15 novembre 2024..."
```

---

## 🔄 Comparison with Exp 001

| Aspect             | Exp 001 (Jiwoo) | Exp 002 (Amira)           |
| ------------------ | --------------- | ------------------------- |
| **Approach**       | [TBD]           | Graph RAG with Neo4j      |
| **Model**          | [TBD]           | Qwen2.5 1.5B (Ollama)     |
| **Data Structure** | [TBD]           | Knowledge Graph           |
| **Language**       | [TBD]           | French                    |
| **Deployment**     | [TBD]           | Fully local               |
| **Query Method**   | [TBD]           | Text-to-Cypher generation |
| **Domain**         | [TBD]           | Equestrian training       |

**Key Differences:**

1. **Graph-native approach:** Uses Neo4j graph database instead of vector embeddings
2. **Local-first:** Ollama deployment vs. API-based models
3. **Specialized domain:** Equestrian performance analysis
4. **Language support:** Full French language pipeline
5. **Transparency:** Returns intermediate steps (Cypher queries + raw results)

---

## 🚧 Known Challenges

1. **Model Size Limitation:** Qwen2.5 1.5B may struggle with complex Cypher syntax
   - _Mitigation:_ Very low temperature (0.1), detailed prompt engineering
2. **French-English Code-Switching:** Queries in French, Cypher syntax in English

   - _Mitigation:_ Explicit prompt instructions about language handling

3. **Schema Complexity:** LLM must understand graph structure to generate valid queries

   - _Mitigation:_ Schema included in every prompt

4. **First-Time Implementation:** No prior Graph RAG experience
   - _Mitigation:_ Incremental testing, manual validation after each question

---

## 🔮 Next Steps

- [ ] Complete initial test run with all 9 questions
- [ ] Analyze Cypher query quality (syntax correctness)
- [ ] Evaluate answer accuracy against ground truth
- [ ] Document failure patterns
- [ ] Consider upgrading to Qwen2.5 7B if 1.5B insufficient
- [ ] Add few-shot examples to prompt if needed
- [ ] Implement query validation layer
- [ ] Create automated evaluation metrics

---

## 📚 References

- [LangChain GraphCypherQAChain Documentation](https://python.langchain.com/docs/use_cases/graph/graph_cypher_qa)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Qwen2.5 Model Card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)

---

## 📝 License & Attribution

This experiment is part of the SportLLM project. Code is based on LangChain framework with custom modifications for French language support and equestrian domain adaptation.
