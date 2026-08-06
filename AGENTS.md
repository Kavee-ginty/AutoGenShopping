# AGENTS.md

# Shopping Agent Project Guidelines

This file defines the engineering principles for everyone (human or AI) contributing to this repository.

The objective of this project is to **learn AutoGen while building a functional shopping assistant**.

---

# Primary Goal

Always prioritize:

1. Correct functionality
2. Readability
3. Simplicity
4. Learning value

Never prioritize cleverness or unnecessary abstraction.

---

# Project Philosophy

This project is intentionally beginner-friendly.

Every new feature should be understandable by someone who has just learned AutoGen.

Assume the reader is new to:

- AutoGen
- Agentic AI
- MCP
- Multi-agent systems

Write code that teaches.

---

# Simplicity Rules

Prefer:

- Simple functions
- Small files
- Explicit code
- Straightforward control flow

Avoid:

- Complex inheritance
- Deep abstraction
- Generic frameworks
- Premature optimization
- Clever one-liners
- Over-engineering

If two implementations produce the same result, choose the simpler one.

---

# Functionality Over Beauty

Working software is always more important than elegant code.

Good:

```
Simple code that works.
```

Better than:

```
Beautiful architecture that is difficult to understand.
```

Every feature should work before it is optimized.

---

# Keep Files Small

Prefer multiple small files instead of one huge file.

Example:

```
agents/
    shopping_agent.py
    classifier_agent.py

workflows/
    search.py
    cart.py
    checkout.py
```

Avoid 1000-line Python files.

---

# Single Responsibility

Each file should have one responsibility.

Examples:

```
llm_config.py

Loads the model.
```

```
shopping_agent.py

Creates the Shopping Assistant.
```

```
search.py

Implements the search workflow.
```

Do not mix responsibilities.

---

# Introduce Complexity Only When Needed

Do not introduce:

- Multiple agents
- Memory
- Reflection
- Planning
- GroupChat
- Swarm
- Async orchestration

unless the project actually needs them.

Always ask:

> "Does this solve a real problem?"

If not, keep the simpler solution.

---

# AutoGen Usage

Prefer AutoGen's built-in features instead of custom implementations.

Examples:

Use:

- AssistantAgent
- UserProxyAgent
- Tools
- System Messages
- Termination Conditions

Avoid reinventing functionality that AutoGen already provides.

---

# Workflows First, Agents Later

Do not create a new agent for every task.

Prefer:

Shopping Assistant

↓

Intent Classification

↓

Workflow

↓

Python Tool

Only create specialized agents when they provide a clear advantage.

---

# Folder Responsibilities

agents/

Contains AI agents only.

workflows/

Contains shopping workflows.

tools/

Contains Python tools callable by agents.

backend/

Contains the fake shopping backend used during development.

mcp/

Contains Kapruka MCP integration.

prompts/

Contains prompt files.

Configuration belongs in configuration files, not inside workflows.

---

# Comments

Write comments only when they explain **why** something exists.

Avoid comments that simply repeat the code.

Good:

```python
# We store the selected product so the checkout workflow
# can access it later.
```

Bad:

```python
# Increment i
i += 1
```

---

# Naming

Use descriptive names.

Good:

```
search_products()

track_order()

shopping_agent

checkout_workflow
```

Avoid abbreviations.

Bad:

```
sp()

trk()

agt()

wf()
```

---

# Error Handling

Fail gracefully.

Never crash because:

- a product wasn't found
- an order doesn't exist
- user input is invalid

Always return a meaningful message.

---

# Teaching First

Whenever adding a new concept:

- keep the implementation as small as possible
- avoid advanced Python features
- prefer explicit code over magic

This repository is both an application and a learning resource.

---

# Future Architecture

The final architecture should remain approximately:

User

↓

Shopping Assistant

↓

Intent Classifier

↓

Workflow

↓

Python Tool

↓

Kapruka MCP

Avoid introducing unnecessary layers.

---

# Dependencies

Only add a dependency if it provides significant value.

Do not install libraries simply to reduce a few lines of code.

---

# Refactoring Rule

Do not refactor code simply to make it "cleaner."

Only refactor if it improves at least one of:

- readability
- maintainability
- functionality
- simplicity

---

# Pull Request Checklist

Before committing, verify:

- The feature works.
- The code is easy to read.
- The solution is beginner-friendly.
- No unnecessary abstractions were introduced.
- Existing functionality was not broken.
- The implementation follows the project philosophy.

---

# Golden Rule

Whenever making a design decision, ask:

> "Would a beginner understand this after reading it once?"

If the answer is "no", simplify it.

# Module Integrity

Do not implement future modules early.

Each module should introduce only the concepts required for that stage.

For example:

- Module 0 should only demonstrate basic agent setup.
- Module 1 should only introduce conversation.
- Module 2 should introduce tool calling.
- Module 3 should introduce a fake backend.
- Kapruka MCP integration should only be added in the dedicated MCP module.

Avoid adding future functionality before it is taught.

Learning progression is more important than feature completeness.