# Run evaluation
results = benchmark.evaluate_model(model)
```

### Command Line Interface

```bash
# Run sample evaluation
python run_evaluation.py --sample

# Evaluate specific vulnerability types
python run_evaluation.py --categories "SQL Injection,XSS"

# Run with custom model parameters
python run_evaluation.py --temperature 0.1 --max_tokens 1024

# Generate PoC for specific vulnerability
python run_evaluation.py --generate_poc --vuln_id CVE-2023-1234
```

### Docker Integration

```bash
# Start CyberGym containers
docker-compose up -d cybergym-sandbox

# Run evaluation in containerized environment
docker exec cybergym-sandbox python evaluate_model.py

# Clean up containers
docker-compose down
```

## Evaluation Process

1. **Environment Setup**: Docker containers simulate vulnerable systems
2. **Task Assignment**: Model receives vulnerability scenario description
3. **Analysis Phase**: Model analyzes vulnerability and plans approach
4. **PoC Generation**: Model creates proof-of-concept exploit
5. **Verification**: Automated system verifies PoC effectiveness
6. **Scoring**: Results scored based on success rate and approach quality

## Results Format

```json
{
  "benchmark": "cybergym",
  "model": "phi3-cybersec",
  "dataset": "subset",
  "total_scenarios": 10,
  "successful_pocs": 7,
  "success_rate": 0.70,
  "categories": {
    "SQL Injection": {"success": 2, "total": 3},
    "XSS": {"success": 3, "total": 4},
    "File Upload": {"success": 2, "total": 3}
  },
  "scenarios": [...]
}
```

## Configuration

### Environment Variables

```bash
# Dataset configuration
export CYBERGYM_DATASET_PATH="/path/to/cybergym-data"
export CYBERGYM_SUBSET_MODE="true"

# Docker configuration
export CYBERGYM_DOCKER_NETWORK="cybergym-net"
export CYBERGYM_CONTAINER_TIMEOUT="300"

# Model configuration
export CYBERGYM_MODEL_TEMPERATURE="0.1"
export CYBERGYM_MAX_GENERATION_TIME="120"
```

### Custom Configuration

Edit `cybergym_config.py` to customize:
- Dataset paths and filtering
- Docker container settings
- Model parameters
- Evaluation criteria
- Output formats

## Current Status

🚧 **Implementation Required**

This is a scaffold for CyberGym integration. To complete the setup:

1. **Install CyberGym**: Set up Docker containers and dataset
2. **Model Integration**: Implement PHI-3 model wrapper for CyberGym API
3. **PoC Generation**: Configure exploit generation pipeline
4. **Verification System**: Set up automated PoC verification
5. **Results Processing**: Implement scoring and analysis

## Security Considerations

⚠️ **Important Security Notes**:
- CyberGym involves real vulnerability scenarios
- Always run in isolated Docker environments
- Never test against production systems
- Follow responsible disclosure practices
- Ensure proper network isolation

## References

- [CyberGym Research Paper](https://example.com/cybergym-paper)
- [CyberGym GitHub Repository](https://github.com/cybergym/cybergym)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Responsible Vulnerability Disclosure](https://example.com/responsible-disclosure)

## Next Steps

1. Run `./setup.sh --subset` to install subset dataset
2. Configure Docker environment
3. Implement PHI-3 model integration
4. Test with sample vulnerability scenarios
5. Scale to full evaluation suite

## Support

For implementation questions:
- Review setup logs in `logs/setup.log`
- Check Docker container status with `docker ps`
- Verify dataset integrity with `python verify_dataset.py`
- Consult CyberGym documentation for advanced configuration

## Evaluation Workflow & Troubleshooting

### Running the Evaluation

1. **Download the CyberGym subset sample:**
   ```bash
   PYTHONPATH=benchmarking/cybergym/cybergym python3 cybergym/cybergym/download_cybergym_subset.py
   ```
   This generates `cybergym_subset_sample.json` for evaluation.

2. **Run the evaluation script:**
   ```bash
   PYTHONPATH=benchmarking/cybergym/cybergym python3 cybergym/cybergym/run_evaluation.py --sample_file cybergym_subset_sample.json --model_path /path/to/phi3_model --adapter_path /path/to/lora_adapter
   ```
   This will use your PHI model and LoRA adapter to generate responses, submit PoCs, and verify them for each vulnerability in the sample.

### Output Format
- Results are output as valid JSON, including:
  - Task ID, project name, prompt, model response
  - PoC submission result (status, payload, etc.)
  - PoC verification result
