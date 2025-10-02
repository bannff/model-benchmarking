#!/usr/bin/env python3
"""
Create a comprehensive cybersecurity training dataset
Direct Q&A with no hallucinated tools
"""

import json

def create_comprehensive_dataset():
    """Generate a comprehensive cybersecurity Q&A dataset"""
    
    training_data = []
    
    # Load the base dataset
    base_data = [
        # STRIDE
        ("What is STRIDE threat modeling?", 
         "STRIDE is a threat modeling methodology developed by Microsoft that categorizes security threats into six main types:\n\n**S - Spoofing**: Impersonating someone or something else (identity attacks)\n**T - Tampering**: Modifying data or code maliciously\n**R - Repudiation**: Denying actions performed (lack of non-repudiation)\n**I - Information Disclosure**: Exposing information to unauthorized individuals\n**D - Denial of Service**: Making resources unavailable to legitimate users\n**E - Elevation of Privilege**: Gaining unauthorized access or permissions\n\nSTRIDE helps security teams systematically identify potential threats during the design phase of applications and systems."),
        
        # SQL Injection
        ("What are SQL injection vulnerabilities?",
         "SQL injection is a code injection attack where malicious SQL statements are inserted into application entry points. It occurs when user input is directly concatenated into SQL queries without proper validation or parameterization.\n\n**Common Types**:\n- Classic SQLi: Direct injection into WHERE clauses\n- Blind SQLi: No direct output, attackers infer data from response timing\n- Union-based: Using UNION statements to extract data from other tables\n- Time-based: Using database sleep functions to confirm injection\n\n**Prevention**: Use parameterized queries, input validation, and least privilege database accounts."),
        
        ("How do you prevent SQL injection?",
         "Prevent SQL injection using these proven techniques:\n\n1. **Parameterized Queries**: Use prepared statements with parameter binding\n2. **Input Validation**: Whitelist allowed characters and validate data types\n3. **Least Privilege**: Database users should have minimal necessary permissions\n4. **Escape Special Characters**: Database-specific escaping as last resort\n5. **Regular Testing**: Automated scanning and manual penetration testing\n\nParameterized queries are the most effective defense - they separate SQL code from data completely."),
        
        # Web Security
        ("What is Cross-Site Scripting (XSS)?",
         "Cross-Site Scripting (XSS) is a vulnerability where malicious scripts are injected into web applications and executed in users' browsers.\n\n**Types**:\n- **Stored XSS**: Malicious script stored on server (most dangerous)\n- **Reflected XSS**: Script reflected back from user input\n- **DOM XSS**: Client-side script manipulation\n\n**Impact**: Session hijacking, credential theft, defacement, malware distribution\n\n**Prevention**: Input validation, output encoding, Content Security Policy (CSP), and proper sanitization of user data."),
        
        ("How do you implement Content Security Policy?",
         "Content Security Policy (CSP) is a security header that helps prevent XSS attacks by controlling resource loading.\n\n**Basic Implementation**:\n```\nContent-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'\n```\n\n**Best Practices**:\n- Start with restrictive policy and gradually allow needed resources\n- Use 'nonce' or hashes instead of 'unsafe-inline'\n- Implement report-uri to monitor violations\n- Test thoroughly in report-only mode first\n\nCSP significantly reduces XSS attack surface when properly implemented."),
        
        # Network Security
        ("What are the OSI model security implications?",
         "Each OSI layer has specific security considerations:\n\n**Layer 1 (Physical)**: Physical access controls, cable protection\n**Layer 2 (Data Link)**: MAC filtering, 802.1X authentication, VLAN security\n**Layer 3 (Network)**: IPSec, routing security, firewalls\n**Layer 4 (Transport)**: TLS/SSL, port security\n**Layer 5 (Session)**: Session management, authentication\n**Layer 6 (Presentation)**: Encryption, data compression security\n**Layer 7 (Application)**: Application-specific controls, WAF\n\nSecurity must be implemented at multiple layers for defense in depth."),
        
        ("How does TLS/SSL work?",
         "TLS (Transport Layer Security) provides encrypted communication between client and server:\n\n**Handshake Process**:\n1. Client Hello: Supported cipher suites and random number\n2. Server Hello: Selected cipher suite, certificate, random number\n3. Key Exchange: Client verifies certificate, exchanges pre-master secret\n4. Finished: Both sides derive session keys and confirm handshake\n\n**Security Features**:\n- **Confidentiality**: Symmetric encryption of data\n- **Integrity**: Message authentication codes (MAC)\n- **Authentication**: Digital certificates verify server identity\n\nModern implementations use TLS 1.2+ with perfect forward secrecy."),
        
        # Cryptography
        ("What is the difference between symmetric and asymmetric encryption?",
         "**Symmetric Encryption**:\n- Same key for encryption and decryption\n- Fast performance, suitable for bulk data\n- Key distribution challenge\n- Examples: AES, ChaCha20\n\n**Asymmetric Encryption**:\n- Public/private key pairs\n- Slower performance, used for key exchange and digital signatures\n- Solves key distribution problem\n- Examples: RSA, Elliptic Curve (ECDH, ECDSA)\n\n**Hybrid Approach**: Most systems use asymmetric encryption to securely exchange symmetric keys, then use symmetric encryption for actual data."),
        
        ("What are digital signatures and how do they work?",
         "Digital signatures provide authentication, integrity, and non-repudiation using asymmetric cryptography:\n\n**Process**:\n1. **Signing**: Hash the message, encrypt hash with private key\n2. **Verification**: Decrypt signature with public key, compare with message hash\n\n**Security Properties**:\n- **Authentication**: Proves who signed the message\n- **Integrity**: Detects any changes to the message\n- **Non-repudiation**: Signer cannot deny signing\n\n**Common Algorithms**: RSA-PSS, ECDSA, EdDSA\n\nDigital signatures are legally binding in many jurisdictions and essential for PKI."),
        
        # Incident Response
        ("What is the NIST Incident Response Framework?",
         "The NIST Incident Response Framework defines four key phases:\n\n**1. Preparation**:\n- Develop policies, procedures, and capabilities\n- Train incident response team\n- Implement detection and analysis tools\n\n**2. Detection and Analysis**:\n- Monitor for security events\n- Analyze and validate incidents\n- Document findings and impact\n\n**3. Containment, Eradication, and Recovery**:\n- Contain the incident to prevent spread\n- Remove threat from environment\n- Restore systems to normal operations\n\n**4. Post-Incident Activity**:\n- Conduct lessons learned sessions\n- Update procedures based on experience\n- Prepare for future incidents\n\nThis cyclical process continuously improves incident response capabilities."),
        
        # Risk Assessment
        ("How do you calculate cybersecurity risk?",
         "Cybersecurity risk is typically calculated as:\n\n**Risk = Threat × Vulnerability × Impact**\n\n**Components**:\n- **Threat**: Likelihood of attack (Annual Rate of Occurrence)\n- **Vulnerability**: Weakness that could be exploited (0-1 scale)\n- **Impact**: Potential damage in monetary terms\n\n**Qualitative Approach**:\n- High/Medium/Low scales for each component\n- Risk matrix combining likelihood and impact\n\n**Quantitative Approach**:\n- Single Loss Expectancy (SLE) = Asset Value × Exposure Factor\n- Annual Loss Expectancy (ALE) = SLE × Annual Rate of Occurrence\n\nBoth approaches help prioritize security investments and risk treatment decisions."),
        
        # Penetration Testing
        ("What are the phases of penetration testing?",
         "Penetration testing follows a structured methodology:\n\n**1. Planning and Reconnaissance**:\n- Define scope and objectives\n- Gather intelligence on target systems\n- Passive and active information gathering\n\n**2. Scanning**:\n- Port scanning and service enumeration\n- Vulnerability scanning\n- Network mapping\n\n**3. Gaining Access**:\n- Exploit vulnerabilities\n- Privilege escalation\n- Maintain access\n\n**4. Maintaining Access**:\n- Install backdoors or persistent access\n- Pivot to other systems\n- Data exfiltration simulation\n\n**5. Analysis and Reporting**:\n- Document findings and evidence\n- Risk assessment and recommendations\n- Present results to stakeholders\n\nEthical considerations and proper authorization are essential throughout."),
        
        # Cloud Security
        ("What is the shared responsibility model in cloud security?",
         "The shared responsibility model defines security obligations between cloud providers and customers:\n\n**Cloud Provider Responsibilities**:\n- Physical security of data centers\n- Infrastructure and platform security\n- Network controls and host operating system patching\n- Hypervisor and service availability\n\n**Customer Responsibilities**:\n- Data encryption and classification\n- Identity and access management\n- Operating system and application patching\n- Network traffic protection\n- Firewall configuration\n\n**Varies by Service Model**:\n- **IaaS**: Customer has more responsibilities\n- **PaaS**: Shared responsibilities for platform\n- **SaaS**: Provider handles most security aspects\n\nUnderstanding this division is crucial for cloud security strategy."),
        
        # Identity and Access Management
        ("What is Zero Trust Architecture?",
         "Zero Trust is a security model based on the principle 'never trust, always verify':\n\n**Core Principles**:\n- Verify explicitly using all available data points\n- Use least privilege access with just-enough-access\n- Assume breach and minimize blast radius\n\n**Key Components**:\n- **Identity verification**: Multi-factor authentication\n- **Device compliance**: Verify device health and compliance\n- **Application security**: Micro-segmentation and application-layer security\n- **Data protection**: Encryption and data loss prevention\n- **Network security**: Software-defined perimeters\n\n**Implementation**: Gradual transition from traditional perimeter-based security to identity-centric, data-aware security model.\n\nZero Trust addresses modern threats in cloud and mobile environments."),
        
        # Compliance
        ("What is SOC 2 and why is it important?",
         "SOC 2 (Service Organization Control 2) is an auditing framework for service providers handling customer data:\n\n**Trust Service Criteria**:\n- **Security**: Protection against unauthorized access\n- **Availability**: System operational availability\n- **Processing Integrity**: Complete, valid, accurate processing\n- **Confidentiality**: Protection of confidential information\n- **Privacy**: Personal information protection\n\n**Types**:\n- **Type I**: Design effectiveness at a point in time\n- **Type II**: Operating effectiveness over time (6-12 months)\n\n**Benefits**:\n- Demonstrates security commitment to customers\n- Competitive advantage in B2B markets\n- Improves internal security processes\n- Required by many enterprise customers\n\nSOC 2 Type II reports are often prerequisites for enterprise software sales."),
    ]
    
    # Convert to training format
    for question, answer in base_data:
        training_data.append({
            "text": f"User: {question}\nAssistant: {answer}"
        })
    
    # Add variations and follow-ups
    variations = [
        ("Explain STRIDE methodology", "STRIDE is Microsoft's threat modeling framework that categorizes security threats into six types: Spoofing (identity attacks), Tampering (data modification), Repudiation (denial of actions), Information Disclosure (unauthorized data access), Denial of Service (resource unavailability), and Elevation of Privilege (unauthorized access). This systematic approach helps identify potential threats during system design and development phases."),
        
        ("What is XSS and how to prevent it?", "Cross-Site Scripting (XSS) allows attackers to inject malicious scripts into web applications. Prevention includes: input validation and sanitization, output encoding, Content Security Policy (CSP) headers, and using frameworks with built-in XSS protection. Never trust user input and always encode output based on context (HTML, JavaScript, CSS, URL)."),
        
        ("How does encryption work?", "Encryption transforms plaintext into ciphertext using mathematical algorithms and keys. Symmetric encryption uses the same key for encryption/decryption (fast, for bulk data). Asymmetric encryption uses public/private key pairs (slower, for key exchange and signatures). Modern systems combine both: asymmetric encryption securely exchanges symmetric keys, then symmetric encryption protects the actual data."),
        
        ("What is a firewall?", "A firewall is a network security device that monitors and controls traffic based on predetermined rules. Types include packet filtering (Layer 3/4), stateful inspection (tracks connections), application layer (Layer 7 inspection), and next-generation firewalls (NGFW) with advanced features. Firewalls can be hardware appliances, software, or cloud-based services."),
        
        ("Explain multi-factor authentication", "Multi-factor authentication (MFA) requires two or more verification factors: something you know (password), something you have (token/phone), something you are (biometrics), or somewhere you are (location). MFA significantly reduces account compromise risk even if passwords are stolen. Common implementations include SMS codes, authenticator apps, hardware tokens, and biometric scanners."),
    ]
    
    for question, answer in variations:
        training_data.append({
            "text": f"User: {question}\nAssistant: {answer}"
        })
    
    return training_data

def save_comprehensive_dataset():
    """Save comprehensive dataset"""
    data = create_comprehensive_dataset()
    
    output_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/comprehensive_cybersecurity_qa.jsonl"
    
    with open(output_file, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')
    
    print(f"✅ Created comprehensive cybersecurity dataset with {len(data)} examples")
    print(f"📁 Saved to: {output_file}")
    
    return output_file

if __name__ == "__main__":
    save_comprehensive_dataset()
