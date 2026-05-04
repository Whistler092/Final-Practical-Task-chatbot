# Final Practical Task - Chatbot

**What should be done***

Create a chatbot, that will be composed from two of your previous tasks: from RAG module and from Agent/MCP module, however, extended with additional functionallity: ability to query infromation on natural disaster. In order to do that, create an MCP server, that will query [CSV file](https://www.kaggle.com/datasets/brsdincer/all-natural-disasters-19002021-eosdis) ﻿[](https://www.kaggle.com/datasets/brsdincer/all-natural-disasters-19002021-eosdis)with Pandas and return user responses to their question from chat.

Test coverage is mandatory.

You can replace that CSV with any other from [the list](https://www.kaggle.com/datasets?search=csv&page=2).﻿[](https://www.kaggle.com/datasets?search=csv&page=2)

**At least one evaluation metric is defined, evaluated, and demonstrated** (quantitative or qualitative measure used to assess the performance, quality, and safety of generative model outputs). You need to have at least small evaluation data set and for at least one criterion


## List of commands executed to run the project:

```
# Verify python installation
> python --version

# Create virtual environment
> python -m venv venv
> .\venv\Scripts\Activate.ps1

# Install dependencies
> pip install -r requirements.txt

# Create .env file
> notepad .env
# Paste your environment variables and save

# Open VS Code
> code .

# Or start Jupyter
> jupyter lab
```

Commands to create the mcp server:

``` 
> create-mcp-server
Creating a new MCP server project using uv.
This will set up a Python project with MCP dependency.

Let's begin!

Project name (required): disasters-server
Project description [A MCP server project]: ALL NATURAL DISASTERS 1900-2021 / EOSDIS from kagglehub
Project version [0.1.0]: 
Project will be created at: D:\ws\AI\Final-Practical-Task-chatbot\disasters-server
Is this correct? [Y/n]: Y
warning: `VIRTUAL_ENV=D:\ws\AI\agents\.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
Using CPython 3.13.12 interpreter at: C:\Users\WinterOS\miniconda3\python.exe
Creating virtual environment at: .venv
Resolved 32 packages in 272ms
      Built disasters-server @ file:///D:/ws/AI/Final-Practical-Task-chatbot/disasters-server
Prepared 1 package in 32ms
░░░░░░░░░░░░░░░░░░░░ [0/32] Installing wheels...                                                                                                                        warning: Failed to hardlink files; falling back to full copy. This may lead to degraded performance.
         If the cache and target directories are on different filesystems, hardlinking may not be supported.
         If this is intentional, set `export UV_LINK_MODE=copy` or use `--link-mode=copy` to suppress this warning.
Installed 32 packages in 2.08s
 + annotated-types==0.7.0
 + anyio==4.13.0
 + attrs==26.1.0
 + certifi==2026.4.22
 + cffi==2.0.0
 + click==8.3.3
 + colorama==0.4.6
 + cryptography==47.0.0
 + disasters-server==0.1.0 (from file:///D:/ws/AI/Final-Practical-Task-chatbot/disasters-server)
 + h11==0.16.0
 + httpcore==1.0.9
 + httpx==0.28.1
 + httpx-sse==0.4.3
 + idna==3.13
 + jsonschema==4.26.0
 + jsonschema-specifications==2025.9.1
 + mcp==1.27.0
 + pycparser==3.0
 + pydantic==2.13.3
 + pydantic-core==2.46.3
 + pydantic-settings==2.14.0
 + pyjwt==2.12.1
 + python-dotenv==1.2.2
 + python-multipart==0.0.27
 + pywin32==311
 + referencing==0.37.0
 + rpds-py==0.30.0
 + sse-starlette==3.4.1
 + starlette==1.0.0
 + typing-extensions==4.15.0
 + typing-inspection==0.4.2
 + uvicorn==0.46.0
✅ Created project disasters-server in disasters-server
ℹ️ To install dependencies run:
   cd disasters-server
   uv sync --dev --all-extras
```