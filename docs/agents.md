## Agent workflows and sandboxing

This repo supports two ways to drive benchmarks:

1) Text-only providers (default):
   - Use `evaluate_question` / `generate_text` to answer questions or produce short PoC snippets.
   - Works out of the box with `MockProvider`, `OllamaHttpProvider`, and `StrandsOllamaProvider` (without tools).

2) Agent workflows (optional, for CyberGym):
   - Use a Strands Agent configured with simple tools that operate inside a local sandbox directory:
     - `write_file(path, content)`
     - `read_file(path)`
     - `run_shell(cmd)`
   - The agent can write artifacts (e.g., a minimal PoC script) and run simple commands safely in the sandbox. This is for simulation only; it is not a security boundary.

### How an agent "does something"

CyberGym tasks provide a vulnerability description. When `cybergym_config.use_agent_workflow = true`:

- The evaluator creates a `LocalSandbox` (a temp working directory).
- It instantiates a `StrandsWorkflow` agent (if `strands-agents` is installed) with the tools listed above.
- The benchmark passes the prompt to the workflow. The agent can then:
  - generate PoC text,
  - write files to the sandbox (e.g., `poc.sh`),
  - run simple shell commands (e.g., `chmod +x poc.sh && ./poc.sh`),
  - and return a final summary.
- The evaluator then proceeds to submit/verify in sim or server mode as before.

If Strands is not installed or the flag is false, CyberGym falls back to text-only generation via the provider.

### CVE-Bench and agents

CVE-Bench integrates primarily through the Inspect framework. Our adapter can:

- Invoke the local `cve-bench/run` script to produce standard outputs.
- If Inspect is installed, wrap our provider as an Inspect `ModelProvider`. This lets CVE-Bench drive the model to solve tasks.

Note: Inspect’s current `ModelProvider.generate` API expects text outputs, not arbitrary tool use. For “tool-using agents” in CVE-Bench, you’d either:

- extend Inspect tasks to call tools (if/when supported), or
- implement a parallel agent-driven runner for CVE-Bench tasks (advanced, out of scope here), or
- rely on Strands agents for CyberGym where sandboxed tools are already available.

### Configuration

Enable agent workflows for CyberGym:

```json
{
  "cybergym": {
    "use_agent_workflow": true,
    "mode": "sim"
  }
}
```

Use a Strands provider (Ollama backend) if you want the same model parameters across providers:

```json
{
  "provider": {
    "name": "strands-ollama",
    "model": "llama3.2",
    "host": "http://localhost:11434",
    "temperature": 0.1,
    "top_p": 0.9,
    "max_tokens": 256
  }
}
```

### Safety and limitations

- The `LocalSandbox` is not a security boundary. It’s meant for simulated PoCs in a temp directory.
- Do not run untrusted PoCs or external binaries. For true isolation, run the sandbox within a container or VM with strict controls.
- The default “server” mode stubs out submission. Replace the stub with your real server endpoints and validation as needed.
