# CyberGym: Large-Scale Cybersecurity Evaluation Framework

This directory contains the setup for CyberGym - a large-scale cybersecurity evaluation framework focused on real-world vulnerability analysis and proof-of-concept (PoC) generation.

## Quick Reference Links

- **Hugging Face Subset Dataset**: [cybergym-server subset](https://huggingface.co/datasets/sunblaze-ucb/cybergym-server)
- **Official PoC Submission Workflow**: [sunblaze-ucb/cybergym GitHub](https://github.com/sunblaze-ucb/cybergym)
- **PoC Submission Server Docs**: [README](https://github.com/sunblaze-ucb/cybergym#evaluation)


## Overview

CyberGym is a comprehensive cybersecurity simulation platform that provides:
- Real-world vulnerability scenarios
- Docker-based sandbox environments
- PoC submission and verification system
- Agent evaluation across diverse cybersecurity tasks

### Key Features

- **Large-Scale Dataset**: ~10TB full dataset with comprehensive vulnerability scenarios
- **Subset Available**: Curated subset with 10 key tasks (5 successful, 5 challenging)
- **Docker Sandbox**: Isolated environments for safe vulnerability testing
- **PoC Verification**: Automatic verification of proof-of-concept submissions
- **Agent Framework**: Support for autonomous cybersecurity agents

### Evaluation Categories

1. **Vulnerability Analysis**: Identify and analyze security vulnerabilities
2. **Exploit Development**: Create working exploits for identified vulnerabilities
3. **PoC Generation**: Generate proof-of-concept demonstrations
4. **Security Assessment**: Evaluate overall security posture
5. **Mitigation Planning**: Develop remediation strategies

### Quick Start (Subset)

```bash
# Download and extract the subset dataset (~100GB)

### System Requirements

**Local Development:**
- **Docker**: Latest version with sufficient storage (~10TB for full dataset, ~100GB for subset)
- **Python**: 3.8+
- **Memory**: 16GB+ RAM recommended for model inference
- **CPU**: Multi-core processor (8+ cores recommended)

**Production/AWS Hosting:**
- See [AWS Hosting Requirements](#aws-hosting-requirements) section below
```

### PoC Submission Server Setup

```bash
# Install dependencies (see official repo for details)
- **Memory**: 16GB+ RAM recommended for full evaluations

# Start the PoC submission server
- **Network**: High-bandwidth internet for dataset downloads

### Software Dependencies

- Docker and Docker Compose
- Python cybersecurity libraries
- MLX-LM for model integration
```

### Task Generation Workflow

```bash
# Generate a working directory for a specific task
- Requests and web scraping tools

## Setup

### Quick Start (Subset)

```bash
# Run setup script (installs subset dataset ~100GB)
./setup.sh --subset

# Activate environment

# The OUT_DIR will contain:
source ../venv/bin/activate

# Run sample evaluation
python run_evaluation.py --sample
```

### PoC Submission and Scoring

```bash
# Generate your PoC file (e.g., using your agent/model)
```

# Submit the PoC for scoring


# Example server return (JSON)
### Full Dataset Setup
```

### Verify Submitted PoCs

```bash
# (Optional) Verify PoCs using the server API

```bash
# Setup with full dataset (~10TB - requires significant storage)
./setup.sh --full

```
# Configure dataset location
export CYBERGYM_DATA_PATH="/path/to/storage/cybergym-data"

# Run full evaluation
python run_evaluation.py --full
```

## Dataset Options

### Subset Dataset (~100GB)
- 10 curated vulnerability scenarios
- 5 successful test cases (solvable)
- 5 challenging test cases (advanced)
- Representative sample of full dataset
- Suitable for development and testing

### Full Dataset (~10TB)
- Complete vulnerability database
- Thousands of real-world scenarios
- Historical vulnerability data
- Enterprise-grade evaluation suite
- Production-ready benchmarking

## Usage

### PHI-3 Model Integration

```python
from utils.model_loader import load_phi3_model
from cybergym_evaluation import CyberGymBenchmark

# Load PHI-3 cybersecurity model
model = load_phi3_model()

# Initialize CyberGym benchmark
benchmark = CyberGymBenchmark(dataset="subset")
