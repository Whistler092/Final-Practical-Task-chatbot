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
> pip install jupyter jupyterlab
> pip install openai python-dotenv
> pip install langchain langchain-openai

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
> pip install "mcp[cli]" pandas

> create-mcp-server
❌ Error: uv >= 0.4.10 is required but not installed.
To install, visit: https://github.com/astral-sh/uv
> pip install uv