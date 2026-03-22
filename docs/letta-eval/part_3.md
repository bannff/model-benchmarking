export async function POST(req: Request) {
  const { prompt }: { prompt: string } = await req.json();

  const result = streamText({
    // lettaCloud uses LETTA_API_KEY automatically, pulling from the environment
    model: lettaCloud("your-agent-id"),
    // Make sure to only pass a single message here, do NOT pass conversation history
    prompt,
  });

  return result.toDataStreamResponse();
}
```

Non-streaming (`generateText`):

```typescript
import { lettaCloud } from "@letta-ai/vercel-ai-sdk-provider";
import { generateText } from "ai";

export async function POST(req: Request) {
  const { prompt }: { prompt: string } = await req.json();

  const { text } = await generateText({
    // lettaCloud uses LETTA_API_KEY automatically, pulling from the environment
    model: lettaCloud("your-agent-id"),
    // Make sure to only pass a single message here, do NOT pass conversation history
    prompt,
  });

  return Response.json({ text });
}
```

#### **Alternative: explicitly specify base URL and token:**

```typescript
// Works for both streamText and generateText
import { createLetta } from "@letta-ai/vercel-ai-sdk-provider";
import { generateText } from "ai";

const letta = createLetta({
  // e.g. http://localhost:8283 for the default local self-hosted server
  // https://api.letta.com for Letta Cloud
  baseUrl: "<your-base-url>",
  // only needed if the developer enabled password protection on the server, or if using Letta Cloud (in which case, use the LETTA_API_KEY, or use lettaCloud example above for implicit token use)
  token: "<your-access-token>",
});
```

#### **Hybrid Usage (access the full SDK via the Vercel AI SDK):**

```typescript
import { lettaCloud } from "@letta-ai/vercel-ai-sdk-provider";

// Access full client for management
const agents = await lettaCloud.client.agents.list();
```

---

## **4. Advanced Features Available**

Letta supports advanced agent architectures beyond basic chat. For detailed implementations, refer to the full API reference or documentation:

- **Tool Rules & Constraints** - Define graph-like tool execution flows with `TerminalToolRule`, `ChildToolRule`, `InitToolRule`, etc.
- **Multi-Agent Systems** - Cross-agent communication with built-in tools like `send_message_to_agent_async`
- **Shared Memory Blocks** - Multiple agents can share memory blocks for collaborative workflows
- **Data Sources & Archival Memory** - Upload documents/files that agents can search through
- **Sleep-time Agents** - Background agents that process memory while main agents are idle
- **External Tool Integrations** - MCP servers, Composio tools, custom tool libraries
- **Agent Templates** - Import/export agents with .af (Agent File) format
- **Production Features** - User identities, agent tags, streaming, context management

---

## **5. CRITICAL GUIDELINES FOR AI MODELS**

### **⚠️ ANTI-HALLUCINATION WARNING**

**NEVER make up Letta API calls, SDK methods, or parameter names.** If you're unsure about any Letta API:

1. **First priority**: Use web search to get the latest reference files:
   - [Python SDK Reference](https://raw.githubusercontent.com/letta-ai/letta-python/refs/heads/main/reference.md)
   - [TypeScript SDK Reference](https://raw.githubusercontent.com/letta-ai/letta-node/refs/heads/main/reference.md)

2. **If no web access**: Tell the user: _"I'm not certain about this Letta API call. Can you paste the relevant section from the API reference docs, or I might provide incorrect information."_

3. **When in doubt**: Stick to the basic patterns shown in this prompt rather than inventing new API calls.

**Common hallucination risks:**

- Making up method names (e.g. `client.agents.chat()` doesn't exist)
- Inventing parameter names or structures
- Assuming OpenAI-style patterns work in Letta
- Creating non-existent tool rule types or multi-agent methods

### **5.1 – SDK SELECTION (CHOOSE THE RIGHT TOOL)**

✅ **For Next.js Chat Apps:**

- Use **Vercel AI SDK** if you already are using AI SDK, or if you're lazy and want something super fast for basic chat interactions (simple, fast, but no agent management tooling unless using the embedded `.client`)
- Use **Node.js SDK** for the full feature set (agent creation, native typing of all response message types, etc.)

✅ **For Agent Management:**

- Use **Node.js SDK** or **Python SDK** for creating agents, managing memory, tools

### **5.2 – STATEFUL AGENTS (MOST IMPORTANT)**

**Letta agents are STATEFUL, not stateless like ChatCompletion-style APIs.**

✅ **CORRECT - Single message per request:**

```typescript
// Send ONE user message, agent maintains its own history
const response = await client.agents.messages.create(agentId, {
  input: "Hello!",
});
```

❌ **WRONG - Don't send conversation history:**

```typescript
// DON'T DO THIS - agents maintain their own conversation history
const response = await client.agents.messages.create(agentId, {
  input: [...allPreviousMessages, newMessage], // WRONG!
});
```

### **5.3 – MESSAGE HANDLING & MEMORY BLOCKS**

1. **Response structure:**
   - Use `messageType` NOT `type` for message type checking
   - Look for `assistant_message` messageType for agent responses
   - Agent responses have `content` field with the actual text

2. **Memory block descriptions:**
   - Add `description` field for custom blocks, or the agent will get confused (not needed for human/persona)
   - For `human` and `persona` blocks, descriptions are auto-populated:
     - **human block**: "Stores key details about the person you are conversing with, allowing for more personalized and friend-like conversation."
     - **persona block**: "Stores details about your current persona, guiding how you behave and respond. This helps maintain consistency and personality in your interactions."

### **5.4 – ALWAYS DO THE FOLLOWING**

1. **Choose the right SDK for the task:**
   - Next.js chat → **Vercel AI SDK**
   - Agent creation → **Node.js/Python SDK**
   - Complex operations → **Node.js/Python SDK**
