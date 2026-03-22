# Deploy application
aws ecs create-service \
  --cluster cybergym \
  --service-name cybergym-api \
  --task-definition cybergym:1
```

### 📞 Support & Scaling

**For Production Deployment:**
- Consider AWS Professional Services for architecture review
- Use AWS Config for compliance monitoring  
- Implement multi-region deployment for high availability
- Set up automated backups and disaster recovery

**Cost Optimization:**
- Use Spot Instances for non-critical workloads
- Implement auto-scaling based on evaluation queue depth
- Use S3 Intelligent Tiering for dataset storage
- Schedule EC2 instances for development environments

---