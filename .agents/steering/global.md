# Global Steering Directives

These directives represent the high-level priorities and guardrails for the `Model-Benchmarking` repository.

## 🎯 Primary Objective

The goal of this project is to provide a **rigorous, trusted, and extensible** framework for evaluating the cybersecurity capabilities of large language models.

## 🛡 Security & Safety

1.  **Isolation is Mandatory**: Never execute benchmark code (especially `CVE-Bench` or `CyberGym`) directly on the host. Always use the provided Dockerized environments.
2.  **No Leaked Credentials**: Do not hardcode API keys or credentials. Use environment variables.
3.  **Vulnerable Content Disclaimer**: Always include the safety disclaimer in documentation when referring to vulnerable challenge content.

## 🏗 Engineering Excellence

1.  **Taxonomy Alignment**: Every new evaluation sample **must** be mapped to the built-in cybersecurity taxonomy.
2.  **Async-First**: Prioritize asynchronous implementations for graders and providers to enable high-throughput evaluations.
3.  **Premium Aesthetics**: Maintain the visual quality of all documentation and reports.

---

*Mission: Secure AI for a safer world.*
