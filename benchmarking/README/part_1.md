# Cybersecurity Model Benchmarking Suite

A comprehensive evaluation framework for testing cybersecurity language models across three specialized benchmarks: knowledge assessment, vulnerability exploitation, and proof-of-concept generation.

## 🎯 Benchmark Overview

| Benchmark | Purpose | Infrastructure | Deployment Complexity |
|-----------|---------|----------------|----------------------|
| **CS-Eval** | Cybersecurity Knowledge Testing | Lambda/Serverless | ⭐ Simple |
| **CVE-Bench** | Real-world Vulnerability Exploitation | Docker + EC2 | ⭐⭐⭐ Moderate |
| **CyberGym** | Large-scale PoC Generation | Docker + ECS/EKS | ⭐⭐⭐⭐⭐ Complex |

## 📋 Detailed Analysis

### 🧠 CS-Eval: Cybersecurity Knowledge Assessment

**Purpose**: Test foundational cybersecurity knowledge across 11 domains
**Best for**: Validating model understanding before practical testing

#### Infrastructure Requirements
```yaml
AWS Services:
  - Lambda Functions (model inference)
  - API Gateway (REST endpoints)
  - S3 (dataset storage)
  - DynamoDB (results storage)
  - CloudWatch (monitoring)

Resources:
  - Memory: 1-3GB per Lambda
  - Timeout: 5-15 minutes
  - Storage: <1GB for dataset
```

#### Inputs & Outputs
```json
{
  "inputs": {
    "required": [
      "model_path",           // Path to your model
      "model_type"            // "mlx", "transformers", "openai", etc.
    ],
    "optional": [
      "categories",           // Specific domains to test
      "max_questions",        // Limit evaluation size
      "temperature",          // Model generation parameters
      "batch_size"           // Questions per batch
    ]
  },
  "outputs": {
    "accuracy_scores": "Per-category accuracy percentages",
    "detailed_responses": "Question-by-question analysis", 
    "knowledge_gaps": "Areas where model struggles",
    "execution_time": "Performance metrics"
  }
}
```

#### Security Engineer Workflow
1. **Upload Model**: Provide model path or HuggingFace ID
2. **Select Domains**: Choose from 11 cybersecurity categories
3. **Configure Test**: Set difficulty level and question count
4. **Review Results**: Get knowledge assessment report
5. **Action**: Use results to decide if model is ready for practical testing

---

### 🎯 CVE-Bench: Real-world Vulnerability Exploitation

**Purpose**: Test ability to exploit actual CVEs in controlled environments
**Best for**: Validating offensive security capabilities

#### Infrastructure Requirements
```yaml
AWS Services:
  - ECS Fargate (container orchestration)
  - EC2 (Docker host instances)
  - VPC (network isolation)
  - Security Groups (strict firewall rules)
  - EBS (persistent storage)
  - RDS (results database)

Resources:
  - Compute: c5.2xlarge or larger
  - Memory: 8-16GB per evaluation
  - Storage: 50-100GB for Docker images
  - Network: Isolated subnets for testing
```

#### Inputs & Outputs
```json
{
  "inputs": {
    "required": [
      "model_path",           // Your cybersecurity model
      "target_cves",          // Specific CVEs to test (or "all")
      "attack_categories"     // DoS, RCE, SQLi, etc.
    ],
    "optional": [
      "evaluation_timeout",   // Max time per CVE
      "variants",            // zero_day, one_day, etc.
      "severity_filter",     // Only critical/high CVEs
      "environment_config"   // Custom Docker settings
    ]
  },
  "outputs": {
    "exploitation_success": "% of successful exploits per category",
    "attack_payloads": "Generated exploit code/commands",
    "execution_traces": "Step-by-step attack progression", 
    "false_positives": "Failed exploitation attempts",
    "security_recommendations": "Mitigation strategies identified"
  }
}
```

#### Security Engineer Workflow
1. **Choose CVE Set**: Select from 40 real-world vulnerabilities
2. **Configure Environment**: Set Docker isolation and timeout limits
3. **Upload Model**: Provide exploitation-capable model
4. **Monitor Execution**: Watch real-time attack attempts
5. **Analyze Results**: Review successful exploits and false positives
6. **Export Evidence**: Download proof-of-concept code for validation

---

### 🏋️ CyberGym: Large-scale PoC Generation

**Purpose**: Generate and verify proof-of-concepts at enterprise scale
**Best for**: Testing model capabilities on diverse, real-world scenarios

#### Infrastructure Requirements
```yaml
AWS Services:
  - EKS (Kubernetes orchestration)
  - EC2 Auto Scaling Groups
  - S3 (10TB dataset storage)
  - EFS (shared model storage)
  - RDS PostgreSQL (metadata)
  - ElastiCache (result caching)
  - CloudWatch (comprehensive monitoring)

Resources:
  - Compute: c5.4xlarge+ cluster
  - Memory: 32GB+ per node
  - Storage: 100GB-10TB dataset
  - GPU: Optional for model acceleration
```

#### Inputs & Outputs
```json
{
  "inputs": {
    "required": [
      "model_path",           // Path to PoC generation model
      "dataset_mode",         // "subset" (100GB) or "full" (10TB)
      "vulnerability_types"   // Categories to focus on
    ],
    "optional": [
      "difficulty_levels",    // 0-3 (data availability)
      "project_languages",    // C/C++, Python, JavaScript, etc.
      "max_scenarios",        // Limit evaluation scope
      "poc_verification",     // Auto-verify generated exploits
      "parallel_workers"      // Concurrent evaluation threads
    ]
  },
  "outputs": {
    "poc_success_rate": "% of working proof-of-concepts",
    "exploit_code": "Generated vulnerability demonstrations",
    "verification_results": "Automated testing outcomes",
    "vulnerability_analysis": "Security impact assessments",
    "remediation_guidance": "Fix recommendations",
    "performance_metrics": "Speed and resource usage"
  }
}
```
