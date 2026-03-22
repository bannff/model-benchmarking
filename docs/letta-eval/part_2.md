# Streaming example
message_text = "Repeat my name."
stream = client.agents.messages.create(
    agent_id=agent_state.id,
    messages=[
        MessageCreate(
            role="user",
            content=message_text,
        ),
    ],
    streaming=True,
    # if stream_tokens is false, each "chunk" will have a full piece
    # if stream_tokens is true, the chunks will be token-based (and may need to be accumulated client-side)
    stream_tokens=True,
)

# print the chunks coming back
for chunk in stream:
    if chunk.message_type == "assistant_message":
        print(chunk.content)
    elif chunk.message_type == "reasoning_message":
        print(chunk.reasoning)
    elif chunk.message_type == "tool_call_message":
        if chunk.tool_call.name:
            print(chunk.tool_call.name)
        if chunk.tool_call.arguments:
            print(chunk.tool_call.arguments)
    elif chunk.message_type == "tool_return_message":
        print(chunk.tool_return)
    elif chunk.message_type == "usage_statistics":
        print(chunk)
```

Creating custom tools (Python only):

```python
def my_custom_tool(query: str) -> str:
    """
    Search for information on a topic.

    Args:
        query (str): The search query

    Returns:
        str: Search results
    """
    return f"Results for: {query}"

# Create tool
tool = client.tools.create_from_function(func=my_custom_tool)

# Add to agent
agent = client.agents.create(
    memory_blocks=[...],
    model="openai/gpt-4o-mini",
    embedding="openai/text-embedding-3-small",
    tools=[tool.name]
)
```

### **TypeScript/Node.js SDK**

```typescript
import { Letta } from "@letta-ai/letta-client";

// Letta Cloud
const client = new Letta({ apiKey: process.env.LETTA_API_KEY });

// Self-hosted, token optional (only if the developer enabled password protection on the server)
const client = new Letta({ baseUrl: "http://localhost:8283" });

// Create agent with memory blocks
const agent = await client.agents.create({
  memory_blocks: [
    {
      label: "human",
      value: "The user's name is Sarah. She likes coding and AI.",
    },
    {
      label: "persona",
      value:
        "I am David, the AI executive assistant. My personality is friendly, professional, and to the point.",
    },
    {
      label: "project",
      value:
        "Sarah is working on a Next.js application with Letta integration.",
      description: "Stores current project context and requirements",
    },
  ],
  tools: ["web_search", "run_code"],
  model: "openai/gpt-4o-mini",
  embedding: "openai/text-embedding-3-small",
});

// Send SINGLE message (agent is stateful!)
const response = await client.agents.messages.create(agent.id, {
  messages: [{ role: "user", content: "How's the project going?" }],
});

// Extract response correctly
for (const msg of response.messages) {
  if (msg.messageType === "assistant_message") {
    console.log(msg.content);
  } else if (msg.messageType === "reasoning_message") {
    console.log(msg.reasoning);
  } else if (msg.messageType === "tool_call_message") {
    console.log(msg.toolCall.name);
    console.log(msg.toolCall.arguments);
  } else if (msg.messageType === "tool_return_message") {
    console.log(msg.toolReturn);
  }
}

// Streaming example
const stream = await client.agents.messages.stream(agent.id, {
  messages: [{ role: "user", content: "Repeat my name." }],
  // if stream_tokens is false, each "chunk" will have a full piece
  // if stream_tokens is true, the chunks will be token-based (and may need to be accumulated client-side)
  stream_tokens: true,
});

for await (const chunk of stream) {
  if (chunk.messageType === "assistant_message") {
    console.log(chunk.content);
  } else if (chunk.messageType === "reasoning_message") {
    console.log(chunk.reasoning);
  } else if (chunk.messageType === "tool_call_message") {
    console.log(chunk.toolCall.name);
    console.log(chunk.toolCall.arguments);
  } else if (chunk.messageType === "tool_return_message") {
    console.log(chunk.toolReturn);
  } else if (chunk.messageType === "usage_statistics") {
    console.log(chunk);
  }
}
```

### **Vercel AI SDK Integration**

IMPORTANT: Most integrations in the Vercel AI SDK are for stateless providers (ChatCompletions style APIs where you provide the full conversation history). Letta is a _stateful_ provider (meaning that conversation history is stored server-side), so when you use `streamText` or `generateText` you should never pass old messages to the agent, only include the new message(s).

#### **Chat Implementation (fast & simple):**

Streaming (`streamText`):

```typescript
// app/api/chat/route.ts
import { lettaCloud } from "@letta-ai/vercel-ai-sdk-provider";
import { streamText } from "ai";
