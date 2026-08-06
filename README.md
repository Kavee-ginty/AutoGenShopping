# Shopping Agent using AutoGen

## Goal

Build a production-quality AI shopping assistant that communicates with the Kapruka MCP server.

The objective of this project is not only to build the application, but also to learn AutoGen from the ground up by implementing one concept at a time.

For the continuation guide from Module 1 onward, see [ToDo.md](ToDo.md).

---

# Learning Philosophy

This project intentionally starts very small.

Instead of building a complicated multi-agent system immediately, we will first understand each AutoGen concept individually.

Every new feature will be introduced only when it solves a real problem.

The focus is:

- Learn first
- Build second
- Keep everything simple
- Avoid unnecessary abstractions
- Prioritize functionality over clever architecture

---

# Final Architecture

User

↓

Shopping Assistant

↓

Intent Classification

↓

Workflow

↓

Python Tools

↓

Kapruka MCP

Only one conversational assistant talks to the user.

Behind the scenes, different workflows handle different tasks.

---

# Modules

## Module 0 — Environment Setup

Goal:

- Create project structure
- Configure OpenRouter
- Create first AssistantAgent
- Learn project organization

Result:

A simple AI assistant that responds to the user.

---

## Module 1 — Shopping Conversation

Topics:

- AssistantAgent
- UserProxyAgent
- System Prompts
- Basic conversation

Result:

A simple shopping chatbot with no tools.

---

## Module 2 — Tool Calling

Topics:

- AutoGen Tools
- Python Functions
- Function Calling

Result:

The assistant can call Python functions such as:

- search_products()
- add_to_cart()
- track_order()

Initially these functions will contain dummy implementations.

---

## Module 3 — Fake Shopping Backend

Topics:

- Local product database
- Orders
- Cart
- Product search

Result:

The assistant behaves like an online shopping website without needing Kapruka.

---

## Module 4 — Intent Classification

Topics:

- User intent
- Routing
- Classification

Possible intents include:

- Search Product
- Add to Cart
- Checkout
- Track Order
- Feedback
- Customer Support

Result:

User requests automatically enter the correct workflow.

---

## Module 5 — Shopping Workflows

Topics:

- Workflow design
- State management
- User interaction

Workflows include:

- Search
- Cart
- Checkout
- Tracking
- Feedback

Result:

Each shopping task becomes an independent workflow.

---

## Module 6 — Kapruka MCP Integration

Topics:

- MCP
- Tool replacement
- API integration

The local backend is replaced with the Kapruka MCP server while keeping the workflows unchanged.

---

## Module 7 — Multiple Agents

Topics:

- Specialized agents
- Agent collaboration
- Delegation

Possible agents:

- Shopping Assistant
- Intent Classifier
- Customer Support

Result:

Agents collaborate only where it improves the system.

---

## Module 8 — Production Improvements

Topics:

- Better prompts
- Logging
- Error handling
- Conversation memory
- Folder organization
- Deployment

Result:

A clean, maintainable production-ready shopping assistant.

---

# Project Structure

```
shopping-agent/

│
├── app.py
├── llm_config.py
├── README.md
├── requirements.txt
│
├── agents/
├── workflows/
├── tools/
├── backend/
├── mcp/
└── prompts/
```

---

# Development Rule

Whenever adding new functionality, ask:

> "Does this make the project easier to understand?"

If not, simplify it.
