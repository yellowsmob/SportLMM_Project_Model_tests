# Graph RAG Experiments Tracker

## Overview

This repository tracks our Graph RAG experiments with different models, codebases, and datasets.

## Experiments

| Exp ID | Date       | Author | Model                   | Dataset            | Status      | Key Results |
| ------ | ---------- | ------ | ----------------------- | ------------------ | ----------- | ----------- | --------- |
| 001    | [date]     | Jiwoo  | [model]                 | [source]           | Original    | ✅ Complete | [metrics] |
| 002    | 2024-12-04 | amira  | [Qwen2.5 1.5B (Ollama)] | [sportllm dataset] | Custom test | 🔄 Running  | -         |

## Quick Links

- [Experiment 001](./experiments/exp_001_jiwoo/)
- [Experiment 002](./experiments/exp_002_amira/)

## Status Legend

- ✅ Complete
- 🔄 In Progress
- ⏸️ Paused
- ❌ Failed
- 📊 Analyzing Results

## How to Add a New Experiment

1. Create folder: `experiments/exp_XXX_description/`
2. Add config.yaml and README.md
3. Update this file
4. Create branch: `git checkout -b exp/XXX-description`
