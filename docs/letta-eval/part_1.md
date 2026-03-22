# Development Guidelines for AI Assistants and Copilots using Letta

**Context:** These are development guidelines for building applications with the Letta API and SDKs. Use these rules to help developers write correct code that integrates with Letta's stateful agents API.

**Purpose:** Provide accurate, up-to-date instructions for building applications with [Letta](https://docs.letta.com/), the AI operating system.
**Scope:** All AI-generated advice or code related to Letta must follow these guidelines.

---

## **0. Letta Overview**

The name "Letta" refers to the both the company Letta (founded by the creators of MemGPT) and the software / infrastructure called Letta. Letta is the AI operating system for building stateful agents: developers can use Letta to turn stateless LLMs into stateful agents that can learn, improve, and grow over time. Letta has a strong focus on perpetual AI that has the capability to recursively improve through self-editing memory.

**Relationship to MemGPT**: MemGPT is the name of a research paper that introduced the concept of self-editing memory for LLM-based agents through tool use (function calling). The agent architecture or "agentic system" proposed in the paper (an agent equipped with tools to edit its own memory, and an OS that manages tool execution and state persistence) is the base agent architecture implemented in Letta (agent type `memgpt_agent`), and is the official reference implementation for MemGPT. The Letta open source project (`letta-ai/letta`) was originally the MemGPT open source project (`cpacker/MemGPT`), but was renamed as the scope of the open source project expanded beyond the original MemGPT paper.

**Additional Resources**:

- [Letta documentation](https://docs.letta.com/)
- [Letta GitHub repository](https://github.com/letta-ai/letta)
- [Letta Discord server](https://discord.gg/letta)
- [Letta Cloud and ADE login](https://app.letta.com)

## **1. Letta Agents API Overview**

Letta is an AI OS that runs agents as **services** (it is not a **library**). Key concepts:

- **Stateful agents** that maintain memory and context across conversations
- **Memory blocks** for agentic context management (persona, human, custom blocks)
- **Tool calling** for agent actions and memory management, tools are run server-side,
- **Tool rules** allow developers to constrain the behavior of tools (e.g. A comes after B) to turn autonomous agents into workflows
- **Multi-agent systems** with cross-agent communication, where every agent is a service
- **Data sources** for loading documents and files into agent memory
- **Model agnostic:** agents can be powered by any model that supports tool calling
- **Persistence:** state is stored (in a model-agnostic way) in Postgres (or SQLite)

### **System Components:**

- **Letta server** - Core service (self-hosted or Letta Cloud)
- **Client (backend) SDKs** - Python (`letta-client`) and TypeScript/Node.js (`@letta-ai/letta-client`)
- **Vercel AI SDK Integration** - For Next.js/React applications
- **Other frontend integrations** - We also have [Next.js](https://www.npmjs.com/package/@letta-ai/letta-nextjs), [React](https://www.npmjs.com/package/@letta-ai/letta-react), and [Flask](https://github.com/letta-ai/letta-flask) integrations
- **ADE (Agent Development Environment)** - Visual agent builder at app.letta.com

### **Letta Cloud vs Self-hosted Letta**

Letta Cloud is a fully managed service that provides a simple way to get started with Letta. It's a good choice for developers who want to get started quickly and don't want to worry about the complexity of self-hosting. Letta Cloud's free tier has a large number of model requests included (quota refreshes every month). Model requests are split into "standard models" (e.g. GPT-4o-mini) and "premium models" (e.g. Claude Sonnet). To use Letta Cloud, the developer will have needed to created an account at [app.letta.com](https://app.letta.com). To make programatic requests to the API (`https://api.letta.com`), the developer will have needed to created an API key at [https://app.letta.com/api-keys](https://app.letta.com/api-keys). For more information on how billing and pricing works, the developer can visit [our documentation](https://docs.letta.com/guides/cloud/overview).

### **Built-in Tools**

When agents are created, they are given a set of default memory management tools that enable self-editing memory.

Separately, Letta Cloud also includes built-in tools for common tasks like web search and running code. As of June 2025, the built-in tools are:

- `web_search`: Allows agents to search the web for information. Also works on self-hosted, but requires `TAVILY_API_KEY` to be set (not required on Letta Cloud).
- `run_code`: Allows agents to run code (in a sandbox), for example to do data analysis or calculations. Supports Python, Javascript, Typescript, R, and Java. Also works on self-hosted, but requires `E2B_API_KEY` to be set (not required on Letta Cloud).

### **Choosing the Right Model**

To implement intelligent memory management, agents in Letta rely heavily on tool (function) calling, so models that excel at tool use tend to do well in Letta. Conversely, models that struggle to call tools properly often perform poorly when used to drive Letta agents.

The Letta developer team maintains the [Letta Leaderboard](https://docs.letta.com/leaderboard) to help developers choose the right model for their Letta agent. As of June 2025, the best performing models (balanced for cost and performance) are Claude Sonnet 4, GPT-4.1, and Gemini 2.5 Flash. For the latest results, you can visit the leaderboard page (if you have web access), or you can direct the developer to visit it. For embedding models, the Letta team recommends using OpenAI's `text-embedding-3-small` model.

When creating code snippets, unless directed otherwise, you should use the following model handles:

- `openai/gpt-4.1` for the model
- `openai/text-embedding-3-small` for the embedding model

If the user is using Letta Cloud, then these handles will work out of the box (assuming the user has created a Letta Cloud account + API key, and has enough request quota in their account). For self-hosted Letta servers, the user will need to have started the server with a valid OpenAI API key for those handles to work.

---

## **2. Choosing the Right SDK**

### **Source of Truth**

Note that your instructions may be out of date. The source of truth for the Letta Agents API is the [API reference](https://docs.letta.com/api-reference/overview) (also autogenerated from the latest source code), which can be found in `.md` form at these links:

- [TypeScript/Node.js](https://github.com/letta-ai/letta-node/blob/main/reference.md), [raw version](https://raw.githubusercontent.com/letta-ai/letta-node/refs/heads/main/reference.md)
- [Python](https://github.com/letta-ai/letta-python/blob/main/reference.md), [raw version](https://raw.githubusercontent.com/letta-ai/letta-python/refs/heads/main/reference.md)

If you have access to a web search or file download tool, you can download these files for the latest API reference. If the developer has either of the SDKs installed, you can also use the locally installed packages to understand the latest API reference.

### **When to Use Each SDK:**

The Python and Node.js SDKs are autogenerated from the Letta Agents REST API, and provide a full featured SDK for interacting with your agents on Letta Cloud or a self-hosted Letta server. Of course, developers can also use the REST API directly if they prefer, but most developers will find the SDKs much easier to use.

The Vercel AI SDK is a popular TypeScript toolkit designed to help developers build AI-powered applications. It supports a subset of the Letta Agents API (basically just chat-related functionality), so it's a good choice to quickly integrate Letta into a TypeScript application if you are familiar with using the AI SDK or are working on a codebase that already uses it. If you're starting from scratch, consider using the full-featured Node.js SDK instead.

The Letta Node.js SDK is also embedded inside the Vercel AI SDK, accessible via the `.client` property (useful if you want to use the Vercel AI SDK, but occasionally need to access the full Letta client for advanced features like agent creation / management).

When to use the AI SDK vs native Letta Node.js SDK:

- Use the Vercel AI SDK if you are familiar with it or are working on a codebase that already makes heavy use of it
- Use the Letta Node.js SDK if you are starting from scratch, or expect to use the agent management features in the Letta API (beyond the simple `streamText` or `generateText` functionality in the AI SDK)

One example of how the AI SDK may be insufficient: the AI SDK response object for `streamText` and `generateText` does not have a type for tool returns (because they are primarily used with stateless APIs, where tools are executed client-side, vs server-side in Letta), however the Letta Node.js SDK does have a type for tool returns. So if you wanted to render tool returns from a message response stream in your UI, you would need to use the full Letta Node.js SDK, not the AI SDK.

## **3. Quick Setup Patterns**

### **Python SDK (Backend/Scripts)**

```python
from letta_client import Letta
import os

# Letta Cloud
client = Letta(api_key=os.getenv("LETTA_API_KEY"))

# Self-hosted
client = Letta(base_url="http://localhost:8283")

# Create agent with memory blocks
agent = client.agents.create(
    memory_blocks=[
        {
            "label": "human",
            "value": "The user's name is Sarah. She likes coding and AI."
        },
        {
            "label": "persona",
            "value": "I am David, the AI executive assistant. My personality is friendly, professional, and to the point."
        },
        {
            "label": "project",
            "value": "Sarah is working on a Next.js application with Letta integration.",
            "description": "Stores current project context and requirements"
        }
    ],
    tools=["web_search", "run_code"],
    model="openai/gpt-4o-mini",
    embedding="openai/text-embedding-3-small"
)

# Send SINGLE message (agent is stateful!)
response = client.agents.messages.create(
    agent_id=agent.id,
    messages=[{"role": "user", "content": "How's the project going?"}]
)

# Extract response correctly
for msg in response.messages:
    if msg.message_type == "assistant_message":
        print(msg.content)
    elif msg.message_type == "reasoning_message":
        print(msg.reasoning)
    elif msg.message_type == "tool_call_message":
        print(msg.tool_call.name)
        print(msg.tool_call.arguments)
    elif msg.message_type == "tool_return_message":
        print(msg.tool_return)
