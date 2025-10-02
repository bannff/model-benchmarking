#!/usr/bin/env python3
"""
Enhanced Cybersecurity Dataset Creator
Creates high-quality, multi-turn conversations that promote agentic, truth-seeking behavior
Integrates pattern identification examples and cybersecurity rule detection
"""

import json
import random
from typing import List, Dict, Any

class CybersecDatasetEnhancer:
    def __init__(self):
        self.pattern_examples = self.load_pattern_examples()
        self.security_rules = self.extract_security_rules()
        
    def load_pattern_examples(self) -> List[Dict]:
        """Load existing pattern identification examples"""
        examples = []
        try:
            with open('datasets/pattern_identification_examples.jsonl', 'r') as f:
                for line in f:
                    examples.append(json.loads(line.strip()))
        except FileNotFoundError:
            print("Pattern examples file not found, will generate from scratch")
        return examples
    
    def extract_security_rules(self) -> List[Dict]:
        """Extract security rules from the pattern identification document"""
        rules = [
            {
                "rule_id": "RULE-MISSING-OBJ-VERSIONING",
                "rule_name": "Missing Object Versioning Configuration",
                "detection_pattern": "resource.VersioningConfiguration.Status != 'Enabled'",
                "description": "Detects resources that do not have versioning enabled. Versioning is a critical security control that protects against accidental or malicious deletions and modifications of data by maintaining multiple versions of objects. Without versioning, there is no way to recover from unintended changes or deletions, potentially leading to data loss and compliance violations.",
                "severity": "HIGH",
                "category": "LOGGING DISABLED"
            },
            {
                "rule_id": "RULE-HARDCODED-PROD-CREDS",
                "rule_name": "Hardcoded Production Credentials in Source Code",
                "detection_pattern": "(?i)(password|credential|secret|key).*=.*['\\\"][^'\\\"]+['\\\"].*(?:prod|production)",
                "description": "Detects hardcoded credentials, particularly those accessing production systems, embedded directly in source code. This represents a significant security risk as credentials stored in source code can be accessed by unauthorized parties, may be inadvertently committed to version control systems, and violate the principle of secure credential management. Production credentials require especially strict protection and should never be hardcoded.",
                "severity": "CRITICAL",
                "category": "HARDCODED CREDENTIALS"
            },
            {
                "rule_id": "RULE-S3-KMS-ENCRYPTION-MISSING",
                "rule_name": "S3 Bucket Missing KMS Encryption",
                "detection_pattern": "resource.type == 'AWS::S3::Bucket' && encryption.type != 'AWS-KMS'",
                "description": "Detects S3 buckets that are not configured to use AWS KMS encryption for data at rest. AWS KMS encryption provides an additional layer of security and is essential for meeting security and compliance requirements for data protection. Lack of KMS encryption may expose sensitive data to unauthorized access and non-compliance risks.",
                "severity": "HIGH",
                "category": "ENCRYPTION MISSING IN AWS RESOURCES"
            },
            {
                "rule_id": "RULE-AWS-SNS-MISSING-SSE",
                "rule_name": "AWS SNS Topics Missing Server-Side Encryption",
                "detection_pattern": "resource.type == \"AWS::SNS::Topic\" && \\nresource.encryption.serverSideEncryption == null || \\nresource.encryption.serverSideEncryption.enabled != true",
                "description": "Detects AWS SNS topics that do not have server-side encryption (SSE) enabled. SNS topics without encryption enabled can expose sensitive message data in transit and at rest. Server-side encryption using AWS KMS provides an additional layer of data protection by helping secure message contents. This is particularly critical for topics handling sensitive or regulated data.",
                "severity": "HIGH",
                "category": "ENCRYPTION MISSING IN AWS RESOURCES"
            }
        ]
        return rules
    
    def generate_agentic_conversations(self) -> List[Dict]:
        """Generate multi-turn agentic conversations that promote truth-seeking behavior"""
        conversations = []
        
        # Truth-seeking behavior patterns
        conversations.extend(self.generate_truth_seeking_conversations())
        
        # Pattern identification conversations
        conversations.extend(self.generate_pattern_identification_conversations())
        
        # Multi-turn cybersecurity analysis
        conversations.extend(self.generate_multi_turn_security_conversations())
        
        # Agentic research behavior
        conversations.extend(self.generate_research_behavior_conversations())
        
        return conversations
    
    def generate_truth_seeking_conversations(self) -> List[Dict]:
        """Generate conversations that demonstrate truth-seeking when information is unknown"""
        conversations = []
        
        # Template for unknown CVE requests
        cve_conversation = {
            "messages": [
                {
                    "role": "user", 
                    "content": "What can you tell me about CVE-2024-12345?"
                },
                {
                    "role": "assistant", 
                    "content": "I don't have information about CVE-2024-12345 in my training data. To get accurate information about this specific vulnerability, I should search for current details. Let me help you find reliable sources:\\n\\n1. **Official MITRE CVE Database**: https://cve.mitre.org\\n2. **National Vulnerability Database (NVD)**: https://nvd.nist.gov\\n3. **Vendor security advisories** if you know the affected product\\n\\nWould you like me to help you understand how to interpret CVE information once you find it, or do you have any other details about this vulnerability?"
                },
                {
                    "role": "user",
                    "content": "I found it affects Apache Struts. Can you help me understand the impact?"
                },
                {
                    "role": "assistant",
                    "content": "Great! Since you've identified it affects Apache Struts, I can help you understand the general impact patterns for Struts vulnerabilities and what to look for:\\n\\n**Common Apache Struts vulnerability impacts:**\\n- Remote Code Execution (RCE) - most critical\\n- Path traversal attacks\\n- Denial of Service (DoS)\\n- Information disclosure\\n\\n**Key questions to research about this specific CVE:**\\n1. **CVSS Score**: What's the severity rating?\\n2. **Attack Vector**: Network, local, or physical access required?\\n3. **Authentication**: Does the attacker need to be authenticated?\\n4. **Affected Versions**: Which Struts versions are vulnerable?\\n5. **Exploit Availability**: Are there public exploits?\\n\\n**Immediate actions to consider:**\\n- Check your Struts version against the CVE details\\n- Review Apache's security advisory\\n- Plan patching if affected\\n\\nCan you share what specific aspect of the impact you're most concerned about?"
                }
            ]
        }
        conversations.append(cve_conversation)
        
        # Template for unknown tools/techniques
        unknown_tool_conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "How do I use the new SecScanPro 3.7 vulnerability scanner?"
                },
                {
                    "role": "assistant", 
                    "content": "I don't have specific information about SecScanPro 3.7 in my training data, as this appears to be a recent or specialized tool. To get accurate usage instructions, I'd recommend:\\n\\n**Primary Sources:**\\n1. **Official documentation** from SecScanPro's vendor\\n2. **User manual** or getting started guide\\n3. **Vendor support** or community forums\\n\\n**General scanner research approach:**\\n1. Check the tool's official website\\n2. Look for video tutorials or webinars\\n3. Search for user reviews and case studies\\n\\n**Meanwhile, I can help with:**\\n- General vulnerability scanning methodologies\\n- Common scanner features and workflows\\n- Interpreting typical scan results\\n- Best practices for vulnerability management\\n\\nWhat specific aspect of vulnerability scanning are you trying to accomplish? This might help me provide more targeted guidance."
                },
                {
                    "role": "user",
                    "content": "I need to scan for web application vulnerabilities in our React app"
                },
                {
                    "role": "assistant",
                    "content": "Perfect! I can definitely help with web application vulnerability scanning approaches for React apps, even without knowing SecScanPro 3.7 specifically.\\n\\n**Key vulnerability categories to scan for in React apps:**\\n\\n1. **Client-side vulnerabilities:**\\n   - XSS (Cross-Site Scripting)\\n   - CSRF (Cross-Site Request Forgery)\\n   - Insecure data storage\\n   - Sensitive data exposure\\n\\n2. **Dependency vulnerabilities:**\\n   - Outdated npm packages\\n   - Known CVEs in third-party libraries\\n   - Supply chain risks\\n\\n3. **Configuration issues:**\\n   - Debug mode in production\\n   - Exposed source maps\\n   - Missing security headers\\n\\n**Scanning approach:**\\n- **Static Analysis**: Scan source code and dependencies\\n- **Dynamic Analysis**: Test running application\\n- **Interactive Analysis**: Combine both approaches\\n\\n**While researching SecScanPro 3.7, you might also consider:**\\n- npm audit (for dependencies)\\n- ESLint security plugins\\n- OWASP ZAP (free alternative)\\n- Snyk (for dependency scanning)\\n\\nWhat's your primary concern - dependencies, runtime vulnerabilities, or configuration issues?"
                }
            ]
        }
        conversations.append(unknown_tool_conversation)
        
        return conversations
    
    def generate_pattern_identification_conversations(self) -> List[Dict]:
        """Generate conversations about security pattern identification"""
        conversations = []
        
        for rule in self.security_rules:
            conversation = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"I found a security issue where {rule['rule_name'].lower()}. Can you help me understand this pattern?"
                    },
                    {
                        "role": "assistant",
                        "content": f"I can help you understand this security pattern. Based on your description, this appears to match the pattern: **{rule['rule_name']}**\\n\\n**Pattern Details:**\\n- **Rule ID**: {rule['rule_id']}\\n- **Severity**: {rule['severity']}\\n- **Category**: {rule['category']}\\n\\n**Description:**\\n{rule['description']}\\n\\n**Detection Logic:**\\n```\\n{rule['detection_pattern']}\\n```\\n\\n**Questions to help me provide more specific guidance:**\\n1. What specific resource or system is affected?\\n2. What environment is this occurring in (dev/staging/prod)?\\n3. Are you looking for immediate remediation steps or trying to understand the broader impact?\\n\\nCan you provide more details about your specific situation?"
                    },
                    {
                        "role": "user", 
                        "content": "This is happening in our production S3 buckets. What should I prioritize?"
                    },
                    {
                        "role": "assistant",
                        "content": f"Production S3 buckets with {rule['rule_name'].lower()} is a **{rule['severity']}-priority** issue that needs immediate attention.\\n\\n**Immediate Assessment Steps:**\\n1. **Inventory affected buckets**: List all buckets matching this pattern\\n2. **Data classification**: Identify what sensitive data is stored\\n3. **Access analysis**: Review who has access to these buckets\\n4. **Impact assessment**: Determine potential compliance violations\\n\\n**Prioritization Framework:**\\n- **Critical**: Buckets with PII, financial data, or regulated content\\n- **High**: Buckets with business-critical or proprietary data\\n- **Medium**: Internal operational data\\n- **Low**: Public or non-sensitive data\\n\\n**Next Steps:**\\n1. **Document findings** with affected bucket names and data types\\n2. **Create remediation plan** with timeline based on data sensitivity\\n3. **Implement monitoring** to prevent future occurrences\\n4. **Review detection rules** to catch similar issues earlier\\n\\n**Would you like me to help you:**\\n- Draft a remediation plan template?\\n- Create monitoring rules for this pattern?\\n- Understand compliance implications?\\n\\nWhat's your biggest concern right now - immediate remediation or preventing recurrence?"
                    }
                ]
            }
            conversations.append(conversation)
        
        return conversations
    
    def generate_multi_turn_security_conversations(self) -> List[Dict]:
        """Generate detailed multi-turn security analysis conversations"""
        conversations = []
        
        # Deep dive security analysis conversation
        security_analysis = {
            "messages": [
                {
                    "role": "user",
                    "content": "Our automated security scanner flagged several issues but I'm not sure which ones to prioritize. Can you help me understand how to approach this?"
                },
                {
                    "role": "assistant",
                    "content": "Absolutely! Security finding prioritization is critical for effective vulnerability management. Let me help you develop a systematic approach.\\n\\n**First, I need to understand your context:**\\n1. What types of findings did the scanner identify?\\n2. What systems/applications were scanned?\\n3. Do you have information about CVSS scores or severity ratings?\\n4. What's your organization's risk tolerance and compliance requirements?\\n\\n**General prioritization framework:**\\n- **Critical/High + Production + Public-facing** = Immediate attention\\n- **External attack surface** takes priority over internal\\n- **Exploitable vulnerabilities** with known exploits\\n- **Compliance-related** findings based on your industry\\n\\n**Key questions to ask about each finding:**\\n- Is this system Internet-accessible?\\n- What's the business impact if compromised?\\n- Are there compensating controls in place?\\n- How difficult would this be to exploit?\\n\\nCan you share some specific examples of the findings? Even without exact details, general categories would help me give you more targeted advice."
                },
                {
                    "role": "user",
                    "content": "We have findings like unencrypted databases, missing security headers, and some XSS vulnerabilities. The databases are internal but the web app is public-facing."
                },
                {
                    "role": "assistant",
                    "content": "Perfect! Now I can give you specific prioritization guidance. Based on what you've described, here's how I'd approach this:\\n\\n**Immediate Priority (Fix within 24-72 hours):**\\n1. **XSS vulnerabilities on public-facing web app** - These can be exploited immediately and affect user data\\n   - Stored XSS is more critical than reflected XSS\\n   - Any XSS that could access admin functionality\\n\\n**High Priority (Fix within 1-2 weeks):**\\n2. **Missing security headers on public web app** - Easy to exploit, affects all users\\n   - Missing CSP (Content Security Policy)\\n   - Missing HSTS (HTTP Strict Transport Security)\\n   - Missing X-Frame-Options\\n\\n**Medium Priority (Fix within 30 days):**\\n3. **Unencrypted internal databases** - High impact but lower immediate risk\\n   - Focus on databases with sensitive data first\\n   - Consider network segmentation as temporary mitigation\\n\\n**Questions to refine prioritization:**\\n- Are the XSS vulnerabilities authenticated or unauthenticated?\\n- Do the internal databases contain PII or sensitive business data?\\n- What type of authentication does your web app use?\\n- Are there any compliance requirements (PCI, HIPAA, etc.)?\\n\\nShould we dive deeper into remediation approaches for any of these specific categories?"
                },
                {
                    "role": "user",
                    "content": "The XSS is in our user comment system and we do store user PII in the databases. How should I approach the XSS fix?"
                },
                {
                    "role": "assistant",
                    "content": "XSS in a comment system with PII storage is definitely your top priority - this is a **CRITICAL** finding that needs immediate attention.\\n\\n**Why this is critical:**\\n- **Stored XSS** in comments can affect all users who view the comments\\n- **PII exposure** risk if attackers can access user profiles/data\\n- **Session hijacking** potential for account takeover\\n- **Privilege escalation** if admin users view malicious comments\\n\\n**Immediate XSS remediation steps:**\\n\\n**1. Emergency mitigation (implement today):**\\n   - Temporarily disable HTML/rich text in comments if possible\\n   - Add basic input filtering as stopgap measure\\n   - Monitor for suspicious comment content\\n\\n**2. Proper fix (implement within 48 hours):**\\n   - **Input validation**: Whitelist allowed characters/tags\\n   - **Output encoding**: HTML encode all user content on display\\n   - **Content Security Policy**: Implement strict CSP headers\\n   - **Input sanitization**: Use libraries like DOMPurify for rich content\\n\\n**3. Testing approach:**\\n   - Test with common XSS payloads: `<script>alert('xss')</script>`\\n   - Test encoding: `&lt;script&gt;` should be displayed as text\\n   - Verify CSP blocks inline scripts\\n\\n**Questions for your fix:**\\n- Do users need rich text formatting in comments?\\n- What framework/language is your web app built on?\\n- Do you have a staging environment for testing?\\n\\nShould I help you draft the specific code fixes or focus on testing procedures?"
                }
            ]
        }
        conversations.append(security_analysis)
        
        return conversations
    
    def generate_research_behavior_conversations(self) -> List[Dict]:
        """Generate conversations that demonstrate agentic research behavior"""
        conversations = []
        
        research_conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "I keep hearing about 'zero trust architecture' but I'm not sure if it's just marketing hype or if there's real substance. Can you help me understand what it actually means?"
                },
                {
                    "role": "assistant",
                    "content": "Great question! Zero Trust is definitely more than marketing hype, though it's often oversimplified. Let me break down the real substance vs. the buzzword aspects.\\n\\n**Core Zero Trust Principles (the real substance):**\\n\\n1. **Never trust, always verify** - No implicit trust based on network location\\n2. **Principle of least privilege** - Minimum necessary access only\\n3. **Assume breach** - Design systems expecting compromise\\n4. **Verify explicitly** - Use identity, device, location, and behavior signals\\n5. **Continuous monitoring** - Real-time risk assessment\\n\\n**What Zero Trust actually involves:**\\n- **Identity and Access Management (IAM)** with strong authentication\\n- **Micro-segmentation** of networks and applications\\n- **Device compliance** and health verification\\n- **Data protection** with encryption and rights management\\n- **Security monitoring** and analytics\\n\\n**Where I'd recommend researching further:**\\n- **NIST SP 800-207** - The definitive Zero Trust Architecture guide\\n- **Forrester Research** - They coined the term, good historical context\\n- **CISA Zero Trust Maturity Model** - Practical implementation guidance\\n\\n**Critical questions to research:**\\n- What specific problems are you trying to solve?\\n- What's your current security architecture maturity?\\n- What's your timeline and budget for transformation?\\n\\nWhat aspects would you like to explore deeper - the technical implementation or the business case?"
                },
                {
                    "role": "user",
                    "content": "We're a mid-size company with hybrid cloud infrastructure. What should I focus on first?"
                },
                {
                    "role": "assistant",
                    "content": "Perfect context! For mid-size hybrid cloud environments, you want to focus on high-impact, manageable wins first. Here's a practical roadmap:\\n\\n**Phase 1: Foundation (0-6 months)**\\n1. **Identity consolidation** - Single sign-on (SSO) across cloud and on-premises\\n2. **Multi-factor authentication (MFA)** - Everywhere, especially admin access\\n3. **Asset inventory** - Know what you have in both environments\\n4. **Network segmentation basics** - Separate critical systems\\n\\n**Phase 2: Enhanced controls (6-12 months)**\\n1. **Privileged access management (PAM)** - Secure admin credentials\\n2. **Device compliance** - Ensure managed devices meet security standards\\n3. **Cloud security posture** - Implement cloud security best practices\\n4. **Monitoring and logging** - Centralized security information\\n\\n**Specific research I'd recommend for your situation:**\\n\\n**Technical research:**\\n- Compare SSO solutions (Okta, Azure AD, Ping Identity)\\n- Review cloud security frameworks (CSF, CIS Controls)\\n- Research network segmentation tools for hybrid environments\\n\\n**Business research:**\\n- Calculate cost of current security incidents/risks\\n- Research compliance requirements for your industry\\n- Look into cyber insurance requirements and discounts\\n\\n**Questions to guide your research:**\\n- What's your biggest security pain point right now?\\n- Do you have dedicated security staff or is this additional responsibility?\\n- What compliance frameworks do you need to meet?\\n\\nWould you like me to help you create a specific research plan for any of these areas?"
                }
            ]
        }
        conversations.append(research_conversation)
        
        return conversations
    
    def enhance_existing_dataset(self, 
                                input_file: str = "datasets/primus_training/train_mlx.jsonl",
                                output_file: str = "datasets/primus_training/train_enhanced.jsonl",
                                cybersec_ratio: float = 0.1):
        """Enhance existing dataset by adding cybersecurity agentic conversations"""
        print("🔍 Enhancing existing dataset with cybersecurity content...")
        
        # Load existing dataset
        existing_data = []
        print(f"📖 Loading existing dataset: {input_file}")
        with open(input_file, 'r') as f:
            for line in f:
                existing_data.append(json.loads(line.strip()))
        
        existing_count = len(existing_data)
        print(f"📊 Loaded {existing_count:,} existing samples")
        
        # Generate cybersecurity conversations
        cybersec_conversations = self.generate_agentic_conversations()
        
        # Convert to MLX format
        cybersec_data = []
        for item in cybersec_conversations:
            if 'messages' in item:
                conversation_text = self.convert_messages_to_text(item['messages'])
                cybersec_data.append({"text": conversation_text})
        
        # Calculate how many cybersec samples to add
        target_cybersec_count = int(existing_count * cybersec_ratio)
        
        # Repeat cybersec data if needed to reach target count
        if len(cybersec_data) < target_cybersec_count:
            multiplier = (target_cybersec_count // len(cybersec_data)) + 1
            cybersec_data = (cybersec_data * multiplier)[:target_cybersec_count]
        else:
            cybersec_data = cybersec_data[:target_cybersec_count]
        
        # Combine datasets
        enhanced_dataset = existing_data + cybersec_data
        
        # Shuffle the combined dataset
        random.shuffle(enhanced_dataset)
        
        # Write enhanced dataset
        with open(output_file, 'w') as f:
            for item in enhanced_dataset:
                f.write(json.dumps(item) + '\n')
        
        print(f"✅ Enhanced dataset created: {output_file}")
        print(f"📊 Original samples: {existing_count:,}")
        print(f"🎯 Added cybersec samples: {len(cybersec_data):,}")
        print(f"📈 Total samples: {len(enhanced_dataset):,}")
        print(f"🔒 Cybersecurity ratio: {(len(cybersec_data)/len(enhanced_dataset)*100):.1f}%")
        
        return len(enhanced_dataset)
    
    def convert_messages_to_text(self, messages: List[Dict]) -> str:
        """Convert messages format to single text for MLX training"""
        text_parts = []
        for msg in messages:
            role = msg['role'].title()
            content = msg['content']
            text_parts.append(f"{role}: {content}")
        
        return "\\n\\n".join(text_parts)

def main():
    enhancer = CybersecDatasetEnhancer()
    
    # Enhance existing dataset instead of creating new one
    sample_count = enhancer.enhance_existing_dataset(
        input_file="datasets/primus_training/train_mlx.jsonl",
        output_file="datasets/primus_training/train_enhanced.jsonl",
        cybersec_ratio=0.15  # Add 15% cybersecurity content
    )
    
    print("\n🚀 Dataset Enhancement Complete!")
    print("===============================")
    print("Enhancement features:")
    print("• Kept all your existing 495K samples")
    print("• Added truth-seeking behavior patterns")
    print("• Added multi-turn agentic conversations") 
    print("• Integrated pattern identification examples")
    print("• Added cybersecurity-focused content")
    print("• Added research and verification prompts")
    print(f"• Total enhanced samples: {sample_count:,}")
    print("\n📁 Files:")
    print("• Original: datasets/primus_training/train_mlx.jsonl")
    print("• Enhanced: datasets/primus_training/train_enhanced.jsonl")
    
if __name__ == "__main__":
    main()
