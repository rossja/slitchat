# SlitChat - Streamlit Ollama Chat Interface

A simple Streamlit application that provides a chat interface for interacting with AI models served by Ollama.

## Features

- Choose from available Ollama models via dropdown menu
- Chat with selected models
- Reset chat history
- Message streaming for supported models

## Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- [uv](https://github.com/astral-sh/uv) for package management

## Setup

1. Clone this repository
2. Set up a virtual environment and install dependencies using uv:

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Unix/MacOS
# Or on Windows: .venv\Scripts\activate

# Install package and dependencies
uv sync
```

## Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The app will be available at http://localhost:8501 by default.

## Usage

1. Select a model from the dropdown menu in the sidebar
2. Type your message in the chat input
3. View the model's response
4. Use the "Reset Chat" button to clear the conversation history

## Project Structure

```
slitchat/
├── slitchat/
│   ├── __init__.py
│   └── app.py     # Main application code
├── app.py         # Entry point
├── pyproject.toml # Dependencies and build configuration
└── README.md
```

## Notes

- Ensure Ollama is running and serving models on the default port (11434)
- The application will fetch available models using the `ollama list` command 