2. **Use the correct client imports:**
   - Python: `from letta_client import Letta` and `import os`
   - TypeScript: `import { Letta } from '@letta-ai/letta-client'`
   - Vercel AI SDK: `from '@letta-ai/vercel-ai-sdk-provider'`

3. **Create agents with proper memory blocks:**
   - Always include `human` and `persona` blocks for chat agents
   - Use descriptive labels and values

4. **Send only single user messages:**
   - Each request should contain only the new user message
   - Agent maintains conversation history automatically
   - Never send previous assistant responses back to agent

5. **Use proper authentication:**
   - Letta Cloud: Always use `apiKey` parameter (TypeScript) or `api_key` (Python)
   - Self-hosted: Use `baseUrl` parameter (TypeScript) or `base_url` (Python), token optional (only if the developer enabled password protection on the server)

---

## **6. Environment Setup**

### **Environment Setup**

```bash
# For Next.js projects (recommended for most web apps)
npm install @letta-ai/vercel-ai-sdk-provider ai

# For agent management (when needed)
npm install @letta-ai/letta-client

# For Python projects
pip install letta-client
```

**Environment Variables:**

```bash
# Required for Letta Cloud
LETTA_API_KEY=your_api_key_here

# Store agent ID after creation (Next.js)
LETTA_AGENT_ID=agent-xxxxxxxxx

# For self-hosted (optional)
LETTA_BASE_URL=http://localhost:8283
```

---

## **7. Verification Checklist**

Before providing Letta solutions, verify:

1. **SDK Choice**: Are you using the simplest appropriate SDK?
   - Familiar with or already using Vercel AI SDK? → use the Vercel AI SDK Letta provider
   - Agent management needed? → use the Node.js/Python SDKs
2. **Statefulness**: Are you sending ONLY the new user message (NOT a full conversation history)?
3. **Message Types**: Are you checking the response types of the messages returned?
4. **Response Parsing**: If using the Python/Node.js SDK, are you extracting `content` from assistant messages?
5. **Imports**: Correct package imports for the chosen SDK?
6. **Client**: Proper client initialization with auth/base_url?
7. **Agent Creation**: Memory blocks with proper structure?
8. **Memory Blocks**: Descriptions for custom blocks?