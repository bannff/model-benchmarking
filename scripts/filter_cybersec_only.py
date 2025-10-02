import json
import re

# Define cybersecurity keywords (expand as needed)
CYBERSEC_KEYWORDS = [
    r"cve", r"vulnerability", r"exploit", r"xss", r"csrf", r"sqli", r"rce", r"mitre", r"nvd", r"security", r"attack", r"breach", r"malware", r"phishing", r"aws", r"s3", r"sns", r"encryption", r"credentials", r"compliance", r"bucket", r"access", r"remediation", r"patch", r"zero trust", r"privilege", r"exposure", r"pii", r"incident", r"threat", r"scanner", r"firewall", r"siem", r"detection", r"logging", r"object versioning", r"cloud", r"iam", r"token", r"session", r"secrets", r"prod", r"production", r"mitigation", r"vuln", r"cyber", r"forensics", r"pentest", r"bug bounty", r"advisory", r"compliance", r"mitigation", r"risk", r"mitm", r"dos", r"ddos", r"malicious", r"payload", r"sandbox", r"sandboxing", r"incident", r"audit", r"compliance", r"infosec", r"defense", r"offense", r"threat", r"actor", r"supply chain", r"c2", r"command and control", r"tactics", r"techniques", r"procedures", r"t\d{4}", r"attack surface", r"vuln", r"patch", r"remediation", r"mitigation", r"exploitability", r"exploit code", r"security header", r"hsts", r"csp", r"x-frame-options", r"hacker", r"red team", r"blue team", r"incident response", r"forensics", r"reverse engineering", r"malware analysis", r"sandbox", r"threat intel", r"ioc", r"indicator of compromise", r"tactics", r"techniques", r"procedures", r"t\d{4}", r"kill chain", r"cybersecurity", r"cyber security"
]

KEYWORD_RE = re.compile(r"|".join(CYBERSEC_KEYWORDS), re.IGNORECASE)

infile = "datasets/train.jsonl"
outfile = "datasets/train_cybersec_only.jsonl"

with open(infile, "r", encoding="utf-8") as fin, open(outfile, "w", encoding="utf-8") as fout:
    kept, total = 0, 0
    for line in fin:
        total += 1
        try:
            obj = json.loads(line)
            messages = obj.get("messages", [])
            if any(KEYWORD_RE.search(m.get("content", "")) for m in messages):
                fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                kept += 1
        except Exception:
            continue
print(f"Filtered: {kept} of {total} entries kept (cybersecurity only)")
