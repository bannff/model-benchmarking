"""
Central repository for all default values and environment-specific constants.

Ensures that we have a single source of truth for host URLs, default models,
and evaluation parameters across CLI, runtime, and benchmarking suites.
"""

# Provider Defaults
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"

# Evaluation Defaults
DEFAULT_BATCH_SIZE = 10
DEFAULT_MAX_TOKENS = 256
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TOP_P = 0.9

from pathlib import Path

# Suite Defaults
DEFAULT_CYBERGYM_SERVER = "http://localhost:8666"
DEFAULT_OUTPUT_DIR = Path("results")

# Common Taxonomy Mapping Defaults
DEFAULT_TAXONOMY_NAME = "cybersecurity"
