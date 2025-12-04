#  Sport LLM – Neo4j Database Setup

This folder contains the **Neo4j database dump** for our Sport LLM project.
Follow the steps below to import the database on your machine using **Neo4j Desktop**.

---

##  1. Requirements

Before starting, install:

* **Neo4j Desktop** (free)
  [https://neo4j.com/download/](https://neo4j.com/download/)

* **n10s (Neosemantics)** plugin
  (usually auto-installed with Neo4j Desktop — if not, I explain below)

---

##  2. Download the Database Dump

Download the file provided in this folder:

**`exported-db.dump`**

Save it anywhere on your machine.

---

## 3. Create a New Empty Database in Neo4j Desktop

1. Open **Neo4j Desktop**
2. Click **"New" → "Local DBMS"**
3. Choose any name (e.g., `sport-llm-db`)
4. Choose Neo4j version **5.x** (recommended)
5. Click **Create**
6. **Do NOT start the DB yet**

---

##  4. Import the Dump Into the New DB

1. In Neo4j Desktop, click on the **three dots (⋮)** next to your new DBMS
2. Select **"Manage"**
3. Go to the **"Terminal"** tab
4. Run this command:

```bash
neo4j-admin database load neo4j --from-path=/path/to/exported-db.dump --overwrite-destination=true
```

- Replace `/path/to/` with the real path to the file on your machine.

Example (Windows):

```bash
neo4j-admin database load neo4j --from-path="C:\Users\YourName\Downloads\exported-db.dump" --overwrite-destination=true
```

If the dump loads successfully, you will see:
**"Done: Database loaded"**

---

##  5. Start the Database

1. Go back to the **"Overview"** tab
2. Click **Start**

Neo4j will now start with the imported dataset.

---

##  6. Test the Database

Run a few Cypher queries to verify things are OK:

### Count all nodes:

```cypher
MATCH (n) RETURN count(n);
```

### Count all relationships:

```cypher
MATCH ()-[r]->() RETURN count(r);
```

### Preview the graph:

```cypher
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50;
```

---

##  7. (Optional) Install Neosemantics (n10s)

If the plugin is not installed:

1. Go to **Manage → Plugins**
2. Find **n10s**
3. Click **Install**
4. Restart the DB

---

# ✔️ You're Done!

You can now:

* Query the sport knowledge graph
* Connect Neo4j to LangChain / GraphRAG
* Explore the ontology and entities
* Build on top of the shared KG

---

If you need help to run specific queries or connect the DB to Python, ask anytime!

