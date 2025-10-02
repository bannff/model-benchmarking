#!/usr/bin/env python3
"""
Comprehensive Cybersecurity Dataset Creator
Generates a large, diverse dataset of cybersecurity conversations with agentic truth-seeking behavior
"""

import json
import random
from typing import List, Dict, Any

class ComprehensiveCybersecDataset:
    def __init__(self):
        self.vulnerability_types = [
            "SQL Injection", "XSS", "CSRF", "RCE", "Path Traversal", "IDOR", 
            "XXE", "SSRF", "Deserialization", "Command Injection"
        ]
        
        self.aws_services = [
            "S3", "EC2", "RDS", "Lambda", "EKS", "ECS", "CloudTrail", "CloudWatch",
            "IAM", "VPC", "SNS", "SQS", "API Gateway", "ALB", "CloudFront"
        ]
        
        self.compliance_frameworks = [
            "SOX", "PCI DSS", "HIPAA", "GDPR", "SOC 2", "ISO 27001", "NIST", "FedRAMP"
        ]
        
        self.attack_techniques = [
            "Lateral Movement", "Privilege Escalation", "Data Exfiltration", "Persistence",
            "Defense Evasion", "Discovery", "Collection", "Command and Control"
        ]

    def generate_comprehensive_dataset(self) -> List[Dict]:
        """Generate a comprehensive cybersecurity dataset"""
        conversations = []
        
        # Truth-seeking patterns (40 conversations)
        conversations.extend(self.generate_unknown_cve_conversations(10))
        conversations.extend(self.generate_unknown_tool_conversations(10))
        conversations.extend(self.generate_unknown_technique_conversations(10))
        conversations.extend(self.generate_research_methodology_conversations(10))
        
        # Pattern identification (30 conversations)
        conversations.extend(self.generate_aws_security_patterns(15))
        conversations.extend(self.generate_application_security_patterns(15))
        
        # Multi-turn analysis (25 conversations - simplified)
        conversations.extend(self.generate_incident_analysis_conversations(15))
        conversations.extend(self.generate_compliance_conversations(10))
        
        # Agentic behavior (30 conversations)
        conversations.extend(self.generate_threat_hunting_conversations(10))
        conversations.extend(self.generate_security_architecture_conversations(10))
        conversations.extend(self.generate_risk_assessment_conversations(10))
        
        return conversations

    def generate_unknown_cve_conversations(self, count: int) -> List[Dict]:
        """Generate conversations about unknown CVEs that demonstrate truth-seeking"""
        conversations = []
        
        for i in range(count):
            cve_year = random.choice([2024, 2025])
            cve_number = random.randint(10000, 99999)
            cve_id = f"CVE-{cve_year}-{cve_number}"
            
            products = ["Apache Struts", "Microsoft Exchange", "VMware vCenter", "Cisco ASA", 
                       "WordPress", "Drupal", "SolarWinds", "Fortinet FortiOS", "Palo Alto PAN-OS"]
            product = random.choice(products)
            
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"What do you know about {cve_id}? I heard it affects {product}."
                    },
                    {
                        "role": "assistant",
                        "content": f"I don't have information about {cve_id} in my training data, as this appears to be a recent vulnerability identifier. Since you mentioned it affects {product}, I can help you research this systematically.\\n\\n**Immediate research steps:**\\n\\n1. **Official Sources:**\\n   - MITRE CVE Database: https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve_id}\\n   - NVD Database: https://nvd.nist.gov/vuln/detail/{cve_id}\\n   - {product.split()[0]} Security Advisories\\n\\n2. **Key information to look for:**\\n   - CVSS score and severity rating\\n   - Attack vector and complexity\\n   - Authentication requirements\\n   - Affected product versions\\n   - Available patches or workarounds\\n\\n3. **Threat intelligence sources:**\\n   - Vendor security bulletins\\n   - CISA Known Exploited Vulnerabilities\\n   - Security researcher blogs\\n\\n**While you research, I can help with:**\\n- Understanding CVSS scoring methodology\\n- {product} security best practices\\n- Vulnerability management workflows\\n- Risk assessment frameworks\\n\\nWhat specific aspect would you like to focus on once you gather the CVE details?"
                    },
                    {
                        "role": "user",
                        "content": f"I found it has a CVSS score of 9.8 and allows remote code execution. We use {product} in production."
                    },
                    {
                        "role": "assistant",
                        "content": f"A CVSS 9.8 RCE vulnerability in production {product} is **CRITICAL** and requires immediate emergency response.\\n\\n**Immediate Actions (within hours):**\\n\\n1. **Threat Assessment:**\\n   - Is your {product} instance Internet-facing?\\n   - What version are you running?\\n   - Are there any compensating controls (WAF, network segmentation)?\\n\\n2. **Emergency Response:**\\n   - Activate your incident response team\\n   - Consider temporary isolation if exploit is active\\n   - Backup critical data before any changes\\n   - Document current configuration\\n\\n3. **Research Priority Items:**\\n   - **Exploit availability**: Are there public exploits or PoCs?\\n   - **Attack indicators**: IOCs to search for in logs\\n   - **Patch availability**: Is there an official fix?\\n   - **Workaround options**: Temporary mitigations\\n\\n**Risk Factors to Investigate:**\\n- Network exposure (internal vs external)\\n- Data sensitivity level\\n- Business criticality\\n- Compliance requirements\\n\\n**Questions for your emergency assessment:**\\n1. Can you safely take the system offline for patching?\\n2. Do you have recent backups and tested restore procedures?\\n3. Are there signs of compromise in your logs?\\n4. What's your maximum acceptable downtime?\\n\\nWhat's your biggest constraint right now - patching window, system criticality, or resource availability?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations

    def generate_aws_security_patterns(self, count: int) -> List[Dict]:
        """Generate AWS security pattern conversations"""
        conversations = []
        
        patterns = [
            {
                "issue": "S3 buckets without encryption",
                "rule_id": "RULE-S3-UNENCRYPTED",
                "severity": "HIGH",
                "detection": "S3 bucket.encryption == null OR bucket.encryption.algorithm != 'AES256'"
            },
            {
                "issue": "EC2 instances with public IPs in private subnets",
                "rule_id": "RULE-EC2-PUBLIC-IP-PRIVATE-SUBNET",
                "severity": "MEDIUM",
                "detection": "EC2.PublicIpAddress != null AND Subnet.Type == 'private'"
            },
            {
                "issue": "IAM users with console access but no MFA",
                "rule_id": "RULE-IAM-NO-MFA-CONSOLE",
                "severity": "HIGH",
                "detection": "IAM.User.ConsoleAccess == true AND IAM.User.MFADevices.length == 0"
            },
            {
                "issue": "RDS instances without backup enabled",
                "rule_id": "RULE-RDS-NO-BACKUP",
                "severity": "MEDIUM",
                "detection": "RDS.BackupRetentionPeriod == 0 OR RDS.BackupRetentionPeriod == null"
            },
            {
                "issue": "Security groups with 0.0.0.0/0 inbound access",
                "rule_id": "RULE-SG-OPEN-INBOUND",
                "severity": "CRITICAL",
                "detection": "SecurityGroup.InboundRules.SourceCIDR == '0.0.0.0/0'"
            }
        ]
        
        for i in range(count):
            pattern = random.choice(patterns)
            service = random.choice(self.aws_services)
            
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Our security scan found {pattern['issue']} in our AWS environment. How serious is this?"
                    },
                    {
                        "role": "assistant",
                        "content": f"This finding represents a **{pattern['severity']}** severity security issue that needs attention. Let me break down the pattern and help you understand the implications.\\n\\n**Security Pattern Identified:**\\n- **Rule ID**: {pattern['rule_id']}\\n- **Detection Logic**: `{pattern['detection']}`\\n- **Severity**: {pattern['severity']}\\n\\n**Why this matters:**\\n{self.get_pattern_explanation(pattern['issue'])}\\n\\n**Assessment Questions:**\\n1. How many resources are affected?\\n2. What type of data do these resources handle?\\n3. Are these resources in production environments?\\n4. Do you have network-level compensating controls?\\n\\n**Next Steps:**\\n1. **Inventory**: Get a complete list of affected resources\\n2. **Prioritize**: Focus on production and sensitive data first\\n3. **Remediate**: Apply security best practices\\n4. **Monitor**: Set up alerts to prevent recurrence\\n\\nCan you tell me more about your environment context - are these production resources, and what type of data or applications are involved?"
                    },
                    {
                        "role": "user",
                        "content": "These are production resources that handle customer data. We have about 15 affected resources."
                    },
                    {
                        "role": "assistant",
                        "content": f"With 15 production resources handling customer data, this needs **immediate prioritization**. Customer data exposure creates both security and compliance risks.\\n\\n**Immediate Action Plan:**\\n\\n**Phase 1: Emergency Assessment (Today)**\\n1. **Data Classification**:\\n   - What types of customer data (PII, payment info, etc.)?\\n   - Any regulated data (HIPAA, PCI, GDPR)?\\n   - Volume and sensitivity level?\\n\\n2. **Risk Analysis**:\\n   - Network exposure level\\n   - Access patterns and logs\\n   - Existing monitoring and alerts\\n\\n**Phase 2: Rapid Remediation (24-48 hours)**\\n1. **High-Risk Resources First**:\\n   - Internet-facing resources\\n   - Resources with most sensitive data\\n   - Most frequently accessed systems\\n\\n2. **Implementation Strategy**:\\n   {self.get_remediation_steps(pattern['issue'])}\\n\\n**Phase 3: Validation (48-72 hours)**\\n1. **Testing**: Verify fixes don't break functionality\\n2. **Monitoring**: Confirm security improvements\\n3. **Documentation**: Update runbooks and procedures\\n\\n**Compliance Considerations:**\\n- Document remediation for audit trails\\n- Assess if this requires breach notification\\n- Review similar patterns across environment\\n\\n**Questions for your remediation planning:**\\n1. Do you have a maintenance window available?\\n2. What's your change management process for production?\\n3. Are there any high-availability requirements?\\n\\nWhat's your biggest constraint - technical complexity, downtime windows, or resource availability?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations[:count]

    def generate_incident_analysis_conversations(self, count: int) -> List[Dict]:
        """Generate multi-turn incident analysis conversations"""
        conversations = []
        
        incident_types = [
            "suspected data breach", "malware detection", "unusual network traffic", 
            "failed login attempts", "privilege escalation", "data exfiltration"
        ]
        
        for i in range(count):
            incident = random.choice(incident_types)
            
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"We're dealing with a potential {incident} incident. Our monitoring tools flagged some unusual activity. Where should I start with the investigation?"
                    },
                    {
                        "role": "assistant",
                        "content": f"A potential {incident} requires systematic investigation. Let me guide you through the initial response framework.\\n\\n**Immediate Steps (First 30 minutes):**\\n\\n1. **Contain and Preserve**:\\n   - Don't shut down systems yet (preserves evidence)\\n   - Isolate affected systems from network if needed\\n   - Document everything with timestamps\\n   - Notify your incident response team\\n\\n2. **Initial Information Gathering**:\\n   - What specific indicators triggered the alert?\\n   - When did the activity first appear?\\n   - Which systems or users are involved?\\n   - What data or resources might be affected?\\n\\n3. **Evidence Collection**:\\n   - Save relevant logs before they rotate\\n   - Capture network traffic if possible\\n   - Document system states and running processes\\n   - Screenshot any relevant alerts or interfaces\\n\\n**Key Questions for {incident}:**\\n{self.get_incident_questions(incident)}\\n\\n**Research Areas to Investigate:**\\n- Similar attack patterns in threat intelligence\\n- Known indicators of compromise (IOCs)\\n- Relevant MITRE ATT&CK techniques\\n- Industry-specific threat reports\\n\\nBefore we dive deeper, can you share:\\n1. What specific alerts or indicators did you observe?\\n2. What's the scope of potentially affected systems?\\n3. Do you have an established incident response plan?"
                    },
                    {
                        "role": "user",
                        "content": "We saw unusual outbound traffic to unknown IPs and some files being accessed that haven't been touched in months. This started about 6 hours ago."
                    },
                    {
                        "role": "assistant",
                        "content": f"Those indicators suggest potential data exfiltration activity - unusual outbound traffic combined with accessing dormant files is a classic pattern. This needs urgent attention.\\n\\n**Critical Analysis Steps:**\\n\\n**1. Traffic Analysis (Priority 1):**\\n   - **Destination IPs**: Research the unknown IPs\\n     - WHOIS lookups, geolocation\\n     - Threat intelligence databases\\n     - Check against known C2 infrastructure\\n   - **Traffic Patterns**: Volume, timing, protocols\\n   - **Source Systems**: Which hosts initiated the connections\\n\\n**2. File Access Investigation:**\\n   - **File Inventory**: What specific files were accessed?\\n   - **Data Classification**: Sensitivity level of accessed files\\n   - **Access Patterns**: Normal vs. unusual access times/users\\n   - **File Integrity**: Any modifications or just reads?\\n\\n**3. Timeline Reconstruction:**\\n   - **T-6 hours**: What was the initial entry point?\\n   - **Authentication logs**: Any suspicious logins?\\n   - **Process execution**: New processes or scheduled tasks?\\n   - **Lateral movement**: Evidence of spreading to other systems?\\n\\n**Immediate Research Actions:**\\n1. **Threat Intelligence**: Search for the destination IPs\\n2. **MITRE ATT&CK**: Map observed techniques\\n3. **Similar Incidents**: Research comparable attack patterns\\n\\n**Questions for deeper analysis:**\\n1. What types of files were accessed (databases, documents, source code)?\\n2. Do you have network monitoring that shows the data volume transferred?\\n3. Were these file accesses from legitimate user accounts or service accounts?\\n\\nWhat's the most concerning aspect right now - the data exposure or the ongoing connection to unknown IPs?"
                    },
                    {
                        "role": "user",
                        "content": "The files included customer databases and source code. The traffic is still ongoing. The account accessing files appears to be a legitimate service account but at unusual times."
                    },
                    {
                        "role": "assistant",
                        "content": f"This is now confirmed as a **CRITICAL SECURITY INCIDENT** with active data exfiltration of customer data and intellectual property. You need to act immediately.\\n\\n**EMERGENCY ACTIONS (Execute Now):**\\n\\n**1. Immediate Containment:**\\n   - **Block outbound traffic** to the suspicious IPs at firewall level\\n   - **Disable the compromised service account** immediately\\n   - **Isolate affected systems** from the network\\n   - **Preserve evidence** before any shutdown\\n\\n**2. Emergency Communications:**\\n   - **Notify leadership** and legal counsel immediately\\n   - **Activate full incident response team**\\n   - **Consider law enforcement** notification\\n   - **Prepare for potential breach disclosure** requirements\\n\\n**3. Evidence Preservation:**\\n   - **Memory dumps** of affected systems before shutdown\\n   - **Network packet captures** of ongoing connections\\n   - **Complete log exports** before they're overwritten\\n   - **Database access logs** showing what data was accessed\\n\\n**Critical Investigation Focus:**\\n\\n**Service Account Compromise Analysis:**\\n   - How was the service account credentials obtained?\\n   - When did the account behavior change from normal patterns?\\n   - What systems have this account accessed recently?\\n   - Are there other service accounts with similar access?\\n\\n**Data Impact Assessment:**\\n   - How many customer records potentially accessed?\\n   - What specific data fields (PII, payment data, etc.)?\\n   - Which source code repositories were accessed?\\n   - Total data volume potentially exfiltrated?\\n\\n**Immediate Questions:**\\n1. Can you immediately disable that service account without breaking critical services?\\n2. Do you have executive leadership and legal counsel contacts available?\\n3. What's your process for emergency network changes?\\n\\nTime is critical - what's your immediate priority: stopping the data loss or preserving evidence?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations

    def get_pattern_explanation(self, issue: str) -> str:
        """Get explanation for security pattern"""
        explanations = {
            "S3 buckets without encryption": "Unencrypted S3 buckets expose data at rest to unauthorized access. If the bucket or account is compromised, data can be read directly without decryption barriers. This violates data protection best practices and many compliance requirements.",
            "EC2 instances with public IPs in private subnets": "This configuration violates the principle of defense in depth. Private subnets should contain only private resources. Public IPs increase attack surface and may bypass intended network security controls.",
            "IAM users with console access but no MFA": "Console access without MFA creates a single point of failure. Compromised passwords alone can provide full AWS access. MFA adds critical second factor authentication.",
            "RDS instances without backup enabled": "No database backups create risk of permanent data loss from corruption, deletion, or ransomware. Recovery becomes impossible without backup retention.",
            "Security groups with 0.0.0.0/0 inbound access": "Open inbound access from the entire Internet dramatically increases attack surface. Any service behind this security group is exposed to global threat actors."
        }
        return explanations.get(issue, "This security configuration increases risk and should be reviewed against security best practices.")

    def get_remediation_steps(self, issue: str) -> str:
        """Get remediation steps for security issues"""
        steps = {
            "S3 buckets without encryption": "- Enable default encryption (AES-256 or KMS)\\n   - Update bucket policies to require encryption\\n   - Audit existing objects for encryption status",
            "EC2 instances with public IPs in private subnets": "- Move instances to public subnets if Internet access needed\\n   - Use NAT Gateway for outbound-only access\\n   - Implement bastion hosts for administrative access",
            "IAM users with console access but no MFA": "- Enable MFA for all console users\\n   - Consider enforcing MFA via IAM policies\\n   - Use IAM conditions to require MFA for sensitive actions",
            "RDS instances without backup enabled": "- Enable automated backups with appropriate retention\\n   - Test restore procedures\\n   - Consider cross-region backup replication",
            "Security groups with 0.0.0.0/0 inbound access": "- Replace with specific IP ranges or other security groups\\n   - Use Application Load Balancer for web traffic\\n   - Implement defense in depth with multiple security layers"
        }
        return steps.get(issue, "Apply security best practices and principle of least privilege")

    def get_incident_questions(self, incident_type: str) -> str:
        """Get specific questions for incident types"""
        questions = {
            "suspected data breach": "- What data assets might be compromised?\\n- Are there signs of data exfiltration?\\n- When did unauthorized access begin?\\n- What compliance notifications may be required?",
            "malware detection": "- What type of malware was detected?\\n- How many systems are affected?\\n- Is the malware still active?\\n- What is the malware's apparent purpose?",
            "unusual network traffic": "- What makes the traffic unusual (volume, destination, timing)?\\n- Is traffic inbound, outbound, or lateral?\\n- Are there patterns suggesting automation?\\n- Do the destinations have known reputation issues?"
        }
        return questions.get(incident_type, "- What are the primary indicators?\\n- What systems are affected?\\n- What is the potential impact?\\n- Are there signs of ongoing activity?")

    def generate_unknown_tool_conversations(self, count: int) -> List[Dict]:
        """Generate conversations about unknown security tools"""
        tools = [
            "SecAnalyzer Pro 4.2", "ThreatScope Enterprise", "VulnScanner X", 
            "NetDefender 2025", "CloudGuard Advanced", "DataShield Analytics"
        ]
        
        conversations = []
        for i in range(count):
            tool = random.choice(tools)
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"How do I configure {tool} for our environment? I need to set up automated scanning."
                    },
                    {
                        "role": "assistant",
                        "content": f"I don't have specific information about {tool} in my training data, as security tools evolve rapidly and this may be a recent version or specialized product. Let me help you find the right configuration guidance.\\n\\n**Research Approach for {tool}:**\\n\\n1. **Official Documentation:**\\n   - Vendor's documentation portal\\n   - Configuration guides and best practices\\n   - Integration examples for your environment type\\n\\n2. **Community Resources:**\\n   - User forums and communities\\n   - GitHub repositories or configuration examples\\n   - YouTube tutorials or vendor webinars\\n\\n3. **Professional Networks:**\\n   - LinkedIn groups for security professionals\\n   - Reddit communities (r/cybersecurity, r/netsec)\\n   - Security conferences and vendor events\\n\\n**General Automated Scanning Setup Questions:**\\nWhile you research {tool} specifics, I can help with general scanning considerations:\\n\\n- What types of assets do you need to scan (web apps, networks, cloud)?\\n- What compliance requirements drive your scanning needs?\\n- What's your preferred scanning frequency and schedule?\\n- How do you want to handle false positives and reporting?\\n\\n**Alternative Tools to Research:**\\nIf {tool} documentation is limited, consider comparing with established tools like:\\n- Nessus, OpenVAS (vulnerability scanning)\\n- OWASP ZAP, Burp Suite (web application)\\n- Nmap, Masscan (network discovery)\\n\\nWhat specific type of scanning are you trying to implement - vulnerability assessment, web application testing, or network discovery?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations

    def generate_unknown_technique_conversations(self, count: int) -> List[Dict]:
        """Generate conversations about unknown attack techniques"""
        conversations = []
        
        for i in range(count):
            technique_id = f"T{random.randint(1000, 1999)}.{random.randint(100, 999)}"
            technique_name = random.choice([
                "Neural Network Poisoning", "Quantum Key Extraction", "Edge Device Pivoting",
                "Container Runtime Escape", "API Chain Exploitation", "Memory Lane Attack"
            ])
            
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"I found reference to MITRE ATT&CK technique {technique_id} '{technique_name}' in a threat report. Can you explain this technique?"
                    },
                    {
                        "role": "assistant", 
                        "content": f"I don't have information about MITRE ATT&CK technique {technique_id} '{technique_name}' in my training data. This appears to be either a very recent addition to the framework or possibly a technique that wasn't in my training cutoff.\\n\\n**Let me help you research this systematically:**\\n\\n**Primary Sources:**\\n1. **MITRE ATT&CK Framework**: https://attack.mitre.org/techniques/{technique_id}/\\n2. **MITRE ATT&CK Navigator**: Use the navigator tool to explore related techniques\\n3. **MITRE ATT&CK GitHub**: https://github.com/mitre-attack/ for latest updates\\n\\n**Research Framework:**\\n1. **Technique Analysis**:\\n   - What tactic category does it fall under?\\n   - What are the technical requirements?\\n   - What detection methods are recommended?\\n   - Are there sub-techniques listed?\\n\\n2. **Threat Intelligence Context**:\\n   - Which threat groups use this technique?\\n   - What are common indicators of compromise?\\n   - How does it fit into attack chains?\\n\\n3. **Defense Research**:\\n   - What mitigations are effective?\\n   - How can it be detected and monitored?\\n   - What tools can identify this technique?\\n\\n**While you research, I can help with:**\\n- General ATT&CK framework navigation\\n- Related technique analysis from similar categories\\n- Detection and mitigation strategies for related techniques\\n- Building custom detection rules\\n\\nWhat specific aspect are you most concerned about - detection, mitigation, or understanding the attack methodology?"
                    },
                    {
                        "role": "user",
                        "content": f"I found it's a new technique in the {random.choice(['Initial Access', 'Persistence', 'Defense Evasion'])} tactic. How should I approach detection?"
                    },
                    {
                        "role": "assistant",
                        "content": f"Great research! Since this is a new technique in the {random.choice(['Initial Access', 'Persistence', 'Defense Evasion'])} tactic, let's build a systematic detection approach based on ATT&CK methodology.\\n\\n**Detection Development Framework:**\\n\\n**1. Understand the Technical Details:**\\n- What specific actions does the technique perform?\\n- What systems, files, or network connections are involved?\\n- Are there prerequisite conditions or dependencies?\\n- What artifacts or traces does it typically leave?\\n\\n**2. Map Detection Opportunities:**\\n- **Host-based**: Process execution, file modifications, registry changes\\n- **Network-based**: Traffic patterns, protocol anomalies, destinations\\n- **Log-based**: Authentication events, application logs, system logs\\n- **Behavioral**: Timing patterns, frequency, user context\\n\\n**3. Detection Strategy Layers:**\\n- **Signature-based**: Known indicators and patterns\\n- **Behavioral-based**: Anomaly detection for unusual activity\\n- **Context-aware**: Correlating multiple data sources\\n- **Threat hunting**: Proactive searching for technique usage\\n\\n**4. Implementation Approach:**\\n- Start with high-confidence, low-noise detections\\n- Build analytics that can distinguish legitimate vs. malicious use\\n- Create detection rules for your SIEM/EDR platform\\n- Establish baseline behaviors for comparison\\n\\n**Key Questions for Your Detection Design:**\\n1. What logging capabilities do you currently have in place?\\n2. What security tools can you leverage for detection?\\n3. How often might this technique realistically be used in your environment?\\n4. What would be the business impact of false positives?\\n\\nOnce you gather the technical details from MITRE, I can help you design specific detection logic and implementation strategies. What's your primary detection platform - SIEM, EDR, or custom analytics?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations

    def generate_research_methodology_conversations(self, count: int) -> List[Dict]:
        """Generate conversations about research methodology"""
        conversations = []
        
        research_topics = [
            "zero-day vulnerability analysis", "supply chain attack patterns", 
            "cloud security misconfiguration", "insider threat indicators",
            "IoT device exploitation", "social engineering techniques"
        ]
        
        for i in range(count):
            topic = random.choice(research_topics)
            
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"I need to research {topic} for a security assessment. Where should I start and what sources are most reliable?"
                    },
                    {
                        "role": "assistant",
                        "content": f"Researching {topic} requires a structured approach using multiple authoritative sources. Let me guide you through a comprehensive research methodology.\\n\\n**Tier 1 Sources (Highest Reliability):**\\n\\n1. **Government and Standards Bodies:**\\n   - NIST Cybersecurity Framework and publications\\n   - CISA alerts and advisories\\n   - NSA/CSS technical reports\\n   - ISO/IEC security standards\\n\\n2. **Industry Authoritative Sources:**\\n   - SANS Institute research and whitepapers\\n   - OWASP project documentation\\n   - MITRE research and CVE database\\n   - Major vendor security research (Microsoft, Google, etc.)\\n\\n**Tier 2 Sources (High Reliability):**\\n\\n1. **Academic and Research Institutions:**\\n   - IEEE security conference papers\\n   - ACM digital library research\\n   - University cybersecurity research centers\\n   - Peer-reviewed security journals\\n\\n2. **Professional Security Organizations:**\\n   - ISC² research reports\\n   - ISACA frameworks and guidance\\n   - (ISA)² security research\\n\\n**Research Methodology Framework:**\\n\\n1. **Start Broad, Then Focus:**\\n   - Begin with authoritative overviews\\n   - Identify key subtopics and specific areas\\n   - Drill down into technical details\\n   - Cross-reference findings across sources\\n\\n2. **Validate Information:**\\n   - Look for multiple independent confirmations\\n   - Check publication dates for currency\\n   - Verify author credentials and affiliations\\n   - Consider potential bias or commercial interests\\n\\n**For {topic} specifically, I recommend starting with:**\\n{self.get_topic_specific_guidance(topic)}\\n\\nWhat's your specific goal with this research - risk assessment, policy development, or technical implementation guidance?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations

    def generate_application_security_patterns(self, count: int) -> List[Dict]:
        """Generate application security pattern conversations"""
        conversations = []
        
        for i in range(count):
            vuln_type = random.choice(self.vulnerability_types)
            
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Our application security scan found potential {vuln_type} vulnerabilities. How should I prioritize and address these findings?"
                    },
                    {
                        "role": "assistant",
                        "content": f"Finding potential {vuln_type} vulnerabilities requires systematic prioritization and remediation. Let me guide you through the assessment and response process.\\n\\n**Immediate Triage Questions:**\\n\\n1. **Severity Assessment:**\\n   - Are these confirmed exploitable or just potential?\\n   - What's the CVSS score or scanner confidence level?\\n   - Are the vulnerable endpoints publicly accessible?\\n   - What data or functionality could be compromised?\\n\\n2. **Context Analysis:**\\n   - Production vs. development environments?\\n   - Business criticality of affected applications?\\n   - User types with access (internal, customer, public)?\\n   - Sensitive data processing or storage involved?\\n\\n**{vuln_type} Specific Considerations:**\\n{self.get_vulnerability_guidance(vuln_type)}\\n\\n**Prioritization Framework:**\\n\\n**Priority 1 (Immediate - 24-48 hours):**\\n- Internet-facing applications with confirmed exploitation\\n- Applications processing sensitive data (PII, payment, etc.)\\n- High-privilege functionality vulnerabilities\\n\\n**Priority 2 (High - 1-2 weeks):**\\n- Internal applications with potential for lateral movement\\n- Applications with business-critical functionality\\n- Vulnerabilities with published exploits\\n\\n**Priority 3 (Medium - 2-4 weeks):**\\n- Development/staging environment issues\\n- Lower-impact applications\\n- Theoretical vulnerabilities requiring complex exploitation\\n\\n**Remediation Strategy:**\\n1. **Temporary Mitigations**: WAF rules, access controls, monitoring\\n2. **Code Fixes**: Permanent resolution in application code\\n3. **Testing**: Validate fixes don't break functionality\\n4. **Verification**: Re-scan to confirm vulnerability closure\\n\\nCan you provide more details about the scan results - specifically the confidence level and which applications/endpoints are affected?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations

    def generate_compliance_conversations(self, count: int) -> List[Dict]:
        """Generate compliance-focused conversations"""
        conversations = []
        
        for i in range(count):
            framework = random.choice(self.compliance_frameworks)
            
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"We need to prepare for {framework} compliance audit. What security controls should we focus on?"
                    },
                    {
                        "role": "assistant",
                        "content": f"Preparing for {framework} compliance requires understanding both the specific requirements and general security control principles. Let me guide you through the key focus areas.\\n\\n**{framework} Core Security Controls:**\\n{self.get_compliance_guidance(framework)}\\n\\n**Audit Preparation Strategy:**\\n\\n**1. Documentation Review (4-6 weeks before audit):**\\n   - Policies and procedures alignment\\n   - Risk assessments and management plans\\n   - Incident response procedures\\n   - Training and awareness programs\\n\\n**2. Technical Controls Assessment (3-4 weeks before):**\\n   - Access control implementations\\n   - Encryption and data protection\\n   - Network security configurations\\n   - Monitoring and logging capabilities\\n\\n**3. Evidence Collection (2-3 weeks before):**\\n   - Log reviews and analysis\\n   - Configuration screenshots\\n   - Process execution evidence\\n   - Training completion records\\n\\n**4. Gap Analysis and Remediation (1-2 weeks before):**\\n   - Identify compliance gaps\\n   - Implement quick fixes where possible\\n   - Document compensating controls\\n   - Prepare explanations for any deficiencies\\n\\n**Common Audit Focus Areas:**\\n- Data classification and handling\\n- User access management and reviews\\n- Change management processes\\n- Vulnerability management\\n- Business continuity planning\\n\\n**Questions to help focus your preparation:**\\n1. When is your audit scheduled?\\n2. Is this your first {framework} audit or a recurring one?\\n3. What's your current confidence level with existing controls?\\n4. Are there specific areas of concern or known gaps?\\n\\nWhat aspect of {framework} compliance is your biggest challenge right now?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations

    def generate_threat_hunting_conversations(self, count: int) -> List[Dict]:
        """Generate threat hunting conversations"""
        conversations = []
        
        for i in range(count):
            hunt_focus = random.choice([
                "lateral movement", "data staging", "command and control", 
                "credential harvesting", "persistence mechanisms", "reconnaissance"
            ])
            
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"I want to conduct a threat hunt focusing on {hunt_focus} activities. How should I structure this hunting campaign?"
                    },
                    {
                        "role": "assistant",
                        "content": f"A structured threat hunt for {hunt_focus} requires hypothesis-driven methodology and systematic data analysis. Let me guide you through building an effective hunting campaign.\\n\\n**Threat Hunting Framework for {hunt_focus}:**\\n\\n**1. Hypothesis Development:**\\n   - **Primary Hypothesis**: What specific behaviors indicate {hunt_focus}?\\n   - **Threat Model**: Which adversaries commonly use these techniques?\\n   - **Environment Context**: How would this appear in your specific infrastructure?\\n   - **Detection Gaps**: Where might existing controls miss this activity?\\n\\n**2. Data Requirements:**\\n{self.get_hunt_data_requirements(hunt_focus)}\\n\\n**3. Hunting Methodology:**\\n   - **Baseline Establishment**: What does normal activity look like?\\n   - **Anomaly Detection**: Statistical and behavioral analysis\\n   - **Pattern Recognition**: Known attack signatures and variations\\n   - **Timeline Analysis**: Sequence and correlation of events\\n\\n**4. Investigation Playbook:**\\n   - **Initial Indicators**: What triggers further investigation?\\n   - **Pivot Points**: How to expand investigation scope?\\n   - **Evidence Collection**: What artifacts to preserve?\\n   - **Escalation Criteria**: When to involve incident response?\\n\\n**Hunt Campaign Structure:**\\n   - **Week 1**: Data collection and baseline analysis\\n   - **Week 2**: Hypothesis testing and initial findings\\n   - **Week 3**: Deep investigation of interesting findings\\n   - **Week 4**: Report development and control improvements\\n\\n**Success Metrics:**\\n   - Threats identified and contained\\n   - False positive rate and investigation efficiency\\n   - Detection capability improvements\\n   - Knowledge and skill development\\n\\nWhat data sources do you currently have available for hunting, and what's your team's experience level with threat hunting methodologies?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations

    def generate_security_architecture_conversations(self, count: int) -> List[Dict]:
        """Generate security architecture conversations"""
        conversations = []
        
        for i in range(count):
            architecture_topic = random.choice([
                "zero trust implementation", "cloud security architecture", 
                "network segmentation", "identity and access management",
                "data protection architecture", "DevSecOps integration"
            ])
            
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"We're designing a {architecture_topic} for our organization. What are the key security principles and considerations?"
                    },
                    {
                        "role": "assistant",
                        "content": f"Designing effective {architecture_topic} requires balancing security principles with business requirements and operational feasibility. Let me guide you through the key considerations.\\n\\n**Core Security Principles:**\\n\\n1. **Defense in Depth**: Multiple layers of security controls\\n2. **Least Privilege**: Minimal access rights for users and systems\\n3. **Fail Secure**: System failures should default to secure state\\n4. **Security by Design**: Built-in rather than bolted-on security\\n5. **Continuous Monitoring**: Ongoing visibility and assessment\\n\\n**{architecture_topic.title()} Specific Considerations:**\\n{self.get_architecture_guidance(architecture_topic)}\\n\\n**Architecture Development Process:**\\n\\n**Phase 1: Requirements Analysis**\\n   - Business objectives and constraints\\n   - Compliance and regulatory requirements\\n   - Risk tolerance and threat model\\n   - Performance and scalability needs\\n\\n**Phase 2: Design Framework**\\n   - Reference architectures and standards\\n   - Technology selection criteria\\n   - Integration requirements\\n   - Migration and transition planning\\n\\n**Phase 3: Implementation Planning**\\n   - Phased rollout strategy\\n   - Resource and skill requirements\\n   - Testing and validation approach\\n   - Change management process\\n\\n**Phase 4: Governance and Evolution**\\n   - Ongoing assessment and improvement\\n   - Metrics and success criteria\\n   - Regular architecture reviews\\n   - Adaptation to changing threats\\n\\n**Key Questions for Your Design:**\\n1. What's driving this architecture initiative?\\n2. What are your current pain points or security gaps?\\n3. What's your timeline and available resources?\\n4. Are there specific compliance or regulatory drivers?\\n\\nWhat aspect of {architecture_topic} is your primary focus - initial design, technology selection, or implementation strategy?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations

    def generate_risk_assessment_conversations(self, count: int) -> List[Dict]:
        """Generate risk assessment conversations"""
        conversations = []
        
        for i in range(count):
            risk_area = random.choice([
                "cloud migration", "remote work security", "supply chain security",
                "IoT device deployment", "AI/ML system security", "merger and acquisition"
            ])
            
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"We need to conduct a security risk assessment for our {risk_area} initiative. What methodology should we follow?"
                    },
                    {
                        "role": "assistant",
                        "content": f"A comprehensive security risk assessment for {risk_area} requires structured methodology to identify, analyze, and prioritize risks effectively. Let me guide you through the process.\\n\\n**Risk Assessment Framework:**\\n\\n**1. Scope Definition:**\\n   - What systems, processes, and data are involved?\\n   - What are the business objectives and timeline?\\n   - Who are the stakeholders and decision makers?\\n   - What are the regulatory or compliance considerations?\\n\\n**2. Asset Identification:**\\n   - Critical business assets and data\\n   - Supporting infrastructure and systems\\n   - Human resources and expertise\\n   - Third-party dependencies and relationships\\n\\n**3. Threat Modeling:**\\n   - Internal threats (insider, accidental)\\n   - External threats (cybercriminals, nation-states)\\n   - Environmental threats (natural disasters, outages)\\n   - Systemic threats (supply chain, technology failures)\\n\\n**{risk_area.title()} Specific Risk Considerations:**\\n{self.get_risk_guidance(risk_area)}\\n\\n**Risk Analysis Methodology:**\\n\\n**Qualitative Assessment:**\\n   - Likelihood: Very Low → Very High (1-5 scale)\\n   - Impact: Minimal → Catastrophic (1-5 scale)\\n   - Risk Score: Likelihood × Impact\\n   - Risk Rating: Low (1-6), Medium (8-12), High (15-20), Critical (25)\\n\\n**Risk Prioritization Matrix:**\\n   - **Critical Risks**: Immediate attention and mitigation\\n   - **High Risks**: Short-term mitigation planning\\n   - **Medium Risks**: Include in security roadmap\\n   - **Low Risks**: Monitor and review periodically\\n\\n**Mitigation Strategy Development:**\\n   - **Accept**: Risk within tolerance levels\\n   - **Avoid**: Eliminate the risk source\\n   - **Mitigate**: Reduce likelihood or impact\\n   - **Transfer**: Insurance or third-party assumption\\n\\nWhat's the primary driver for this risk assessment - compliance requirement, business initiative, or security improvement?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations

    def get_vulnerability_guidance(self, vuln_type: str) -> str:
        """Get specific guidance for vulnerability types"""
        guidance = {
            "SQL Injection": "- Test with manual payloads to confirm exploitability\\n- Check if prepared statements are consistently used\\n- Verify input validation and sanitization\\n- Assess data exposure potential",
            "XSS": "- Determine if stored, reflected, or DOM-based\\n- Test impact scope (session hijacking, data theft)\\n- Check Content Security Policy implementation\\n- Verify output encoding practices",
            "CSRF": "- Confirm anti-CSRF token implementation\\n- Check SameSite cookie attributes\\n- Verify referrer header validation\\n- Assess business function impact"
        }
        return guidance.get(vuln_type, "- Validate exploitability and impact\\n- Check compensating controls\\n- Assess business risk\\n- Plan remediation approach")

    def get_compliance_guidance(self, framework: str) -> str:
        """Get compliance-specific guidance"""
        guidance = {
            "SOX": "- Financial reporting controls and accuracy\\n- IT general controls (access, change management)\\n- Data integrity and backup procedures\\n- Audit logging and monitoring",
            "PCI DSS": "- Cardholder data protection and encryption\\n- Network security and access controls\\n- Vulnerability management and testing\\n- Security awareness and training",
            "HIPAA": "- PHI protection and access controls\\n- Risk assessment and management\\n- Breach notification procedures\\n- Business associate agreements"
        }
        return guidance.get(framework, "- Access controls and data protection\\n- Risk management processes\\n- Incident response procedures\\n- Regular security assessments")

    def get_topic_specific_guidance(self, topic: str) -> str:
        """Get topic-specific research guidance"""
        guidance = {
            "zero-day vulnerability analysis": "1. **CVE Database and NVD**: Latest vulnerability disclosures\\n2. **Vendor Security Advisories**: Direct from affected vendors\\n3. **Threat Intelligence Feeds**: Commercial and open source\\n4. **Security Research Blogs**: Researchers and security companies",
            "supply chain attack patterns": "1. **NIST Supply Chain Framework**: Government guidance\\n2. **ENISA Supply Chain Reports**: European cybersecurity agency\\n3. **Industry Case Studies**: SolarWinds, Kaseya, Log4j analyses\\n4. **Vendor Risk Management**: Best practices and frameworks"
        }
        return guidance.get(topic, "1. **Industry Standards**: Relevant frameworks and guidelines\\n2. **Government Resources**: NIST, CISA, and agency publications\\n3. **Research Literature**: Academic and industry research\\n4. **Case Studies**: Real-world examples and lessons learned")

    def get_hunt_data_requirements(self, hunt_focus: str) -> str:
        """Get data requirements for threat hunting"""
        data_reqs = {
            "lateral movement": "- **Network Logs**: East-west traffic analysis\\n- **Authentication Logs**: Cross-system login patterns\\n- **Process Execution**: Remote execution and tools\\n- **File Access**: Unusual file sharing activity",
            "data staging": "- **File System Monitoring**: Large file creation/movement\\n- **Network Traffic**: Unusual data volumes\\n- **Process Activity**: Archiving and compression tools\\n- **Storage Access**: Database and file server logs",
            "command and control": "- **DNS Logs**: Domain resolution patterns\\n- **Network Traffic**: Beaconing and communication patterns\\n- **Process Execution**: Network tool usage\\n- **Registry Changes**: Persistence mechanisms"
        }
        return data_reqs.get(hunt_focus, "- **System Logs**: Process and authentication events\\n- **Network Logs**: Traffic patterns and destinations\\n- **Security Logs**: Alert and detection data\\n- **Application Logs**: Service-specific activity")

    def get_architecture_guidance(self, architecture_topic: str) -> str:
        """Get architecture-specific guidance"""
        guidance = {
            "zero trust implementation": "- **Identity Verification**: Multi-factor authentication everywhere\\n- **Device Trust**: Continuous device posture assessment\\n- **Network Segmentation**: Micro-segmentation and least privilege\\n- **Data Protection**: Encryption and access controls",
            "cloud security architecture": "- **Shared Responsibility**: Clear division of security duties\\n- **Identity and Access**: Cloud-native IAM integration\\n- **Data Protection**: Encryption in transit and at rest\\n- **Monitoring**: Cloud-native security tools and SIEM"
        }
        return guidance.get(architecture_topic, "- **Security Controls**: Appropriate protection mechanisms\\n- **Integration**: Seamless workflow integration\\n- **Scalability**: Growth and change accommodation\\n- **Monitoring**: Visibility and alerting capabilities")

    def get_risk_guidance(self, risk_area: str) -> str:
        """Get risk area specific guidance"""
        guidance = {
            "cloud migration": "- **Data Exposure**: Public cloud misconfigurations\\n- **Access Control**: Identity and privilege management\\n- **Compliance**: Regulatory requirement changes\\n- **Vendor Lock-in**: Dependency and exit strategy risks",
            "remote work security": "- **Endpoint Security**: Unmanaged device risks\\n- **Network Security**: VPN and connection security\\n- **Data Protection**: Information on personal devices\\n- **Physical Security**: Home office environment risks"
        }
        return guidance.get(risk_area, "- **Technology Risks**: System and infrastructure vulnerabilities\\n- **Process Risks**: Workflow and procedure gaps\\n- **People Risks**: Training and awareness needs\\n- **Compliance Risks**: Regulatory and legal considerations")

    def convert_to_mlx_format(self, conversations: List[Dict]) -> List[Dict]:
        """Convert conversations to MLX training format"""
        mlx_data = []
        
        for conv in conversations:
            if 'messages' in conv:
                text_parts = []
                for msg in conv['messages']:
                    role = msg['role'].title()
                    content = msg['content']
                    text_parts.append(f"{role}: {content}")
                
                full_text = "\\n\\n".join(text_parts)
                mlx_data.append({"text": full_text})
        
        return mlx_data

    def create_comprehensive_dataset(self, output_file: str = "datasets/comprehensive_cybersec_dataset.jsonl"):
        """Create comprehensive cybersecurity dataset"""
        print("🔍 Creating comprehensive cybersecurity dataset...")
        print("📊 Generating conversations...")
        
        # Generate all conversation types
        conversations = self.generate_comprehensive_dataset()
        
        # Convert to MLX format
        mlx_data = self.convert_to_mlx_format(conversations)
        
        # Write to file
        with open(output_file, 'w') as f:
            for item in mlx_data:
                f.write(json.dumps(item) + '\\n')
        
        print(f"✅ Comprehensive dataset created: {output_file}")
        print(f"📊 Total conversations: {len(conversations)}")
        print(f"📊 Total MLX samples: {len(mlx_data)}")
        print("🎯 Focus areas:")
        print("  • Truth-seeking behavior for unknown information")
        print("  • Multi-turn agentic conversations") 
        print("  • AWS security pattern identification")
        print("  • Incident response and analysis")
        print("  • Research methodology and verification")
        
        return len(mlx_data)

def main():
    dataset_creator = ComprehensiveCybersecDataset()
    sample_count = dataset_creator.create_comprehensive_dataset()
    
    print("\\n🚀 Comprehensive Dataset Creation Complete!")
    print("==========================================")
    print(f"📈 Generated {sample_count} high-quality cybersecurity training samples")
    print("🎯 Key behavioral patterns included:")
    print("  ✓ Admits knowledge limitations honestly")
    print("  ✓ Provides research guidance when uncertain")
    print("  ✓ Demonstrates systematic investigation approaches")
    print("  ✓ Shows multi-turn analytical thinking")
    print("  ✓ Emphasizes verification and evidence-based decisions")

if __name__ == "__main__":
    main()
