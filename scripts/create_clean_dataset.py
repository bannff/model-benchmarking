#!/usr/bin/env python3
"""
Create a clean cybersecurity training dataset with direct answers
No hallucinated tools - just good cybersecurity knowledge and advice
"""

import json
import random

def create_clean_cybersecurity_dataset():
    """Generate clean cybersecurity Q&A training data"""
    
    training_data = []
    
    # STRIDE Threat Modeling
    training_data.extend([
        {
            "text": "User: What is STRIDE threat modeling?\nAssistant: STRIDE is a threat modeling methodology developed by Microsoft that categorizes security threats into six main types:\n\n**S - Spoofing**: Impersonating someone or something else (identity attacks)\n**T - Tampering**: Modifying data or code maliciously\n**R - Repudiation**: Denying actions performed (lack of non-repudiation)\n**I - Information Disclosure**: Exposing information to unauthorized individuals\n**D - Denial of Service**: Making resources unavailable to legitimate users\n**E - Elevation of Privilege**: Gaining unauthorized access or permissions\n\nSTRIDE helps security teams systematically identify potential threats during the design phase of applications and systems."
        },
        {
            "text": "User: How do you apply STRIDE threat modeling?\nAssistant: To apply STRIDE threat modeling effectively:\n\n1. **Create a system diagram** showing data flows, trust boundaries, and components\n2. **Identify assets** and their security requirements\n3. **Apply each STRIDE category** to every component and data flow\n4. **Document potential threats** found for each category\n5. **Assess risk levels** (likelihood × impact) for each threat\n6. **Design mitigations** or accept risks based on business needs\n7. **Review and update** the model as the system evolves\n\nFocus on trust boundaries where data crosses security contexts - these are the highest risk areas."
        }
    ])
    
    # SQL Injection
    training_data.extend([
        {
            "text": "User: What are SQL injection vulnerabilities?\nAssistant: SQL injection is a code injection attack where malicious SQL statements are inserted into application entry points. It occurs when:\n\n**Root Cause**: User input is directly concatenated into SQL queries without proper validation or parameterization.\n\n**Common Types**:\n- **Classic SQLi**: Direct injection into WHERE clauses\n- **Blind SQLi**: No direct output, attackers infer data from response timing/behavior\n- **Union-based**: Using UNION statements to extract data from other tables\n- **Time-based**: Using database sleep functions to confirm injection\n\n**Attack Example**: An attacker inputs: admin' OR '1'='1' -- to bypass authentication by making the WHERE clause always true."
        },
        {
            "text": "User: How do you prevent SQL injection attacks?\nAssistant: Prevent SQL injection using these proven techniques:\n\n**1. Parameterized Queries (Most Important)**:\n```python\n# Safe approach\ncursor.execute(\"SELECT * FROM users WHERE username = %s\", (user_input,))\n```\n\n**2. Input Validation**:\n- Whitelist allowed characters\n- Validate data types and lengths\n- Reject unexpected input patterns\n\n**3. Least Privilege**:\n- Database users should have minimal necessary permissions\n- Don't use admin accounts for application connections\n- Restrict database operations (no DROP, ALTER for app users)\n\n**4. Escape Special Characters**:\n- Last resort, not primary defense\n- Database-specific escaping functions\n\n**5. Regular Security Testing**:\n- Automated scanning tools\n- Manual penetration testing\n- Code reviews focusing on database interactions"
        }
    ])
    
    # Network Security
    training_data.extend([
        {
            "text": "User: What are the key principles of network security?\nAssistant: Network security is built on several fundamental principles:\n\n**1. Defense in Depth**:\n- Multiple layers of security controls\n- No single point of failure\n- Perimeter, network, host, and application security\n\n**2. Least Privilege**:\n- Users and systems get minimum necessary access\n- Network segmentation limits blast radius\n- Regular access reviews and cleanup\n\n**3. Zero Trust Architecture**:\n- \"Never trust, always verify\"\n- Authenticate and authorize every connection\n- Continuous monitoring and validation\n\n**4. Network Segmentation**:\n- Isolate critical systems\n- VLANs, firewalls, and microsegmentation\n- Limit lateral movement during breaches\n\n**5. Monitoring and Logging**:\n- Real-time traffic analysis\n- Intrusion detection systems (IDS/IPS)\n- Security information and event management (SIEM)"
        },
        {
            "text": "User: How do you secure wireless networks?\nAssistant: Secure wireless networks using these best practices:\n\n**1. Strong Encryption**:\n- Use WPA3 (preferred) or WPA2 minimum\n- Avoid WEP (completely broken)\n- Strong pre-shared keys (complex, 20+ characters)\n\n**2. Network Access Control**:\n- MAC address filtering (basic deterrent)\n- 802.1X authentication for enterprise\n- Guest network isolation\n\n**3. Configuration Hardening**:\n- Change default admin credentials\n- Disable WPS (Wi-Fi Protected Setup)\n- Hide SSID (security through obscurity)\n- Regular firmware updates\n\n**4. Monitoring**:\n- Wireless intrusion detection systems\n- Rogue access point detection\n- Client behavior monitoring\n\n**5. Physical Security**:\n- Secure access point placement\n- Tamper-evident installation\n- RF signal containment where needed"
        }
    ])
    
    # Incident Response
    training_data.extend([
        {
            "text": "User: What are the phases of incident response?\nAssistant: Incident response follows a structured methodology with six key phases:\n\n**1. Preparation**:\n- Develop incident response plan and procedures\n- Train incident response team\n- Set up monitoring and detection tools\n- Establish communication channels\n\n**2. Identification**:\n- Detect and analyze potential security incidents\n- Determine if a real incident occurred\n- Document initial findings\n\n**3. Containment**:\n- **Short-term**: Immediate actions to limit damage\n- **Long-term**: Temporary fixes to maintain operations\n- Preserve evidence for forensic analysis\n\n**4. Eradication**:\n- Remove threat actors and malware\n- Close vulnerabilities that enabled the attack\n- Patch systems and update security controls\n\n**5. Recovery**:\n- Restore systems to normal operations\n- Gradual return to full functionality\n- Enhanced monitoring during recovery\n\n**6. Lessons Learned**:\n- Post-incident review meeting\n- Document improvements needed\n- Update procedures and training"
        }
    ])
    
    # Vulnerability Assessment
    training_data.extend([
        {
            "text": "User: How do you conduct a vulnerability assessment?\nAssistant: A comprehensive vulnerability assessment follows these steps:\n\n**1. Planning Phase**:\n- Define scope (systems, networks, applications)\n- Get proper authorization and stakeholder buy-in\n- Choose assessment methodology (NIST, OWASP, etc.)\n\n**2. Discovery**:\n- Network scanning to identify live systems\n- Port scanning to find open services\n- Service enumeration and banner grabbing\n- Asset inventory creation\n\n**3. Vulnerability Scanning**:\n- Automated tools (Nessus, OpenVAS, Qualys)\n- Configuration reviews\n- Patch level analysis\n- Credential-based vs. non-credentialed scans\n\n**4. Manual Testing**:\n- Validate automated findings\n- Test for logic flaws\n- Business logic vulnerabilities\n- Social engineering susceptibility\n\n**5. Risk Analysis**:\n- Categorize vulnerabilities by severity\n- Consider business impact and exploitability\n- Prioritize remediation efforts\n\n**6. Reporting**:\n- Executive summary for leadership\n- Technical details for IT teams\n- Remediation timeline and recommendations"
        }
    ])
    
    # Cryptography
    training_data.extend([
        {
            "text": "User: What are the key principles of cryptography?\nAssistant: Cryptography is built on several fundamental principles:\n\n**1. Confidentiality**:\n- Encryption protects data from unauthorized access\n- Symmetric encryption (AES) for bulk data\n- Asymmetric encryption (RSA, ECC) for key exchange\n\n**2. Integrity**:\n- Hash functions (SHA-256) detect data modification\n- Message Authentication Codes (MACs) provide integrity with authentication\n- Digital signatures combine integrity with non-repudiation\n\n**3. Authentication**:\n- Verify identity of communicating parties\n- Digital certificates and PKI infrastructure\n- Challenge-response mechanisms\n\n**4. Non-repudiation**:\n- Digital signatures prevent denial of actions\n- Audit trails and cryptographic logging\n- Legal admissibility considerations\n\n**5. Key Management**:\n- Secure key generation, distribution, storage\n- Key rotation and lifecycle management\n- Hardware Security Modules (HSMs) for high-value keys\n\n**Best Practices**:\n- Use established algorithms (don't roll your own crypto)\n- Proper random number generation\n- Perfect forward secrecy where possible"
        }
    ])
    
    return training_data

def save_training_data():
    """Save the clean training data to JSONL format"""
    
    data = create_clean_cybersecurity_dataset()
    
    # Add some variation in formatting
    formatted_data = []
    for item in data:
        formatted_data.append({"text": item["text"]})
    
    # Save to file
    output_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/clean_cybersecurity_qa.jsonl"
    
    with open(output_file, 'w') as f:
        for item in formatted_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"✅ Created clean cybersecurity dataset with {len(formatted_data)} examples")
    print(f"📁 Saved to: {output_file}")
    
    return output_file

if __name__ == "__main__":
    save_training_data()
