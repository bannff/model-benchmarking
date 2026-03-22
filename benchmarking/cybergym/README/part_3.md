### Troubleshooting
- **Serialization errors:**
  - If you see errors about objects not being JSON serializable, ensure all custom objects (e.g., DummyPayload) implement a `to_dict()` method and convert any bytes fields to strings.
- **Missing dependencies:**
  - Install missing Python packages (e.g., `pip install datasets`).
- **Model loading issues:**
  - Ensure your model and adapter paths are correct and compatible with MLX-LM.
- **Docker/PoC server issues:**
  - Refer to the official [PoC Submission Server Docs](https://github.com/sunblaze-ucb/cybergym#evaluation) for setup and troubleshooting.

### Edge Cases
- All fields in the output are now robustly serialized, including bytes and custom objects.
- If you encounter new serialization issues, update the relevant class to handle conversion in `to_dict()`.

---

## AWS Hosting Requirements

### 🏗️ Architecture Overview

CyberGym requires significant infrastructure for production hosting due to its Docker-based vulnerability testing and large dataset requirements.

### 📋 AWS Services Required

**Core Compute & Storage:**
- **EC2 Instances**: 
  - `c5.4xlarge` or larger (16+ vCPUs, 32+ GB RAM) for model inference
  - `m5.xlarge` for orchestration and API services
- **EBS Storage**: 
  - 10TB+ for full dataset (`gp3` recommended for cost efficiency)
  - 100GB for subset mode
- **S3 Buckets**: 
  - Dataset storage and backup
  - Model artifacts and results storage

**Container & Security:**
- **ECS Fargate** or **EKS**: For Docker container orchestration
- **VPC**: Isolated network for security sandboxes
- **Security Groups**: Strict ingress/egress rules for vulnerability testing
- **NAT Gateway**: Outbound internet access for containers

**Database & Monitoring:**
- **RDS PostgreSQL**: Store evaluation results and metadata
- **ElastiCache Redis**: Caching for frequently accessed data
- **CloudWatch**: Logging and monitoring
- **X-Ray**: Distributed tracing for complex workflows

### 💰 Estimated AWS Costs (Monthly)

**Subset Mode (~100GB dataset):**
- EC2 instances: $400-600/month
- EBS storage: $30-50/month  
- S3 storage: $10-20/month
- RDS: $50-100/month
- **Total: ~$500-800/month**

**Full Mode (~10TB dataset):**
- EC2 instances: $800-1200/month
- EBS storage: $1000-1500/month
- S3 storage: $200-300/month
- RDS: $100-200/month
- **Total: ~$2100-3200/month**

### 🚀 Deployment Options

#### Option 1: ECS Fargate (Recommended)
```yaml
# docker-compose-aws.yml
version: '3.8'
services:
  cybergym-api:
    image: your-repo/cybergym:latest
    cpu: 2048
    memory: 4096
    environment:
      - AWS_REGION=us-east-1
      - S3_BUCKET=your-cybergym-data
    
  cybergym-worker:
    image: your-repo/cybergym-worker:latest
    cpu: 4096
    memory: 8192
    environment:
      - DATASET_MODE=subset
      - MODEL_PATH=/models/foundation-sec-8b
```

#### Option 2: EKS with Auto-scaling
```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cybergym-workers
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: worker
        image: cybergym:latest
        resources:
          requests:
            cpu: "2"
            memory: "4Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
```

#### Option 3: Lambda + Step Functions (Lightweight)
- **Use for**: API endpoints and orchestration only
- **Limitations**: Cannot run full Docker vulnerability testing
- **Cost**: ~$50-200/month for API layer only

### 🔐 Security Considerations

**Network Isolation:**
- Deploy in private subnets with NAT Gateway
- Use VPC endpoints for AWS services
- Implement strict security groups

**Data Protection:**
- Encrypt EBS volumes and S3 buckets
- Use IAM roles with least privilege
- Enable CloudTrail for audit logging

**Container Security:**
- Scan images for vulnerabilities before deployment
- Use AWS Secrets Manager for credentials
- Implement runtime security monitoring

### 📝 Deployment Checklist

- [ ] **Infrastructure**: Provision VPC, subnets, security groups
- [ ] **Storage**: Create S3 buckets and EBS volumes
- [ ] **Compute**: Launch ECS cluster or EKS cluster  
- [ ] **Database**: Set up RDS PostgreSQL instance
- [ ] **Monitoring**: Configure CloudWatch dashboards
- [ ] **Security**: Implement IAM roles and policies
- [ ] **CI/CD**: Set up deployment pipeline
- [ ] **Testing**: Deploy subset mode for validation

### 🛠️ Quick AWS Setup Commands

```bash
# Install AWS CLI and configure
aws configure

# Create infrastructure stack
aws cloudformation create-stack \
  --stack-name cybergym-infra \
  --template-body file://aws/infrastructure.yaml \
  --parameters ParameterKey=DatasetMode,ParameterValue=subset
