# SkyFlow Airline Assistant

A customer-service chatbot for a fictional airline, built with **LangChain**, **Groq** and **SQLite**, with a **Streamlit** web interface. The bot chats naturally, and it looks up flight details only after the user provides their first name, last name and confirmation number.

The project follows the running-state-chain approach from the NVIDIA DLI notebook *Building RAG Agents with LLMs*, adapted to use Groq and a SQLite database.

## Features

- Friendly small talk and general questions without asking for personal data
- Extracts the user's name and confirmation number from normal conversation
- Retrieves booking details from SQLite only when all three fields are known
- Keeps a running knowledge base of the conversation
- Streams answers in a Streamlit chat interface

## How it works

```
User message
   ↓
internal_chain
   ├─ knowbase_getter  → LLM extracts name and confirmation into a KnowledgeBase
   └─ database_getter  → SQL lookup if all fields are known, otherwise "no info yet"
   ↓
external_chain (prompt + knowledge base + retrieved context)
   ↓
Reply
```

The LLM never writes SQL. It only extracts the user's details, and a fixed, parameterized query does the lookup, so private data stays gated and SQL injection is not possible.

## Project structure

```
airline-rag/
├── app.py            # Streamlit interface
├── main.py           # Terminal interface
├── chains/
│   └── chatbot.py    # Knowledge base, extractor, chains, prompts
├── retrieval.py      # SQLite lookup (get_flight_info)
├── database.py       # Creates and fills airline.db
├── settings.py       # Loads environment variables
├── .env.example      # Template for your API key
└── pyproject.toml
```

## Setup

**1. Clone the project and install dependencies** (requires [uv](https://docs.astral.sh/uv/)):

```bash
git clone https://github.com/YOUR-USERNAME/airline-rag.git
cd airline-rag
uv sync
```

**2. Create a `.env` file** from the template and add your Groq API key:

```
GROQ_API_KEY=your_key_here
GROQ_MODEL=your_model_name
```

**3. Create the database:**

```bash
uv run database.py
```

## Run

Web interface:

```bash
uv run streamlit run app.py
```

Terminal interface:

```bash
uv run main.py
```

## Try it

Sample bookings in the database:

| Name | Confirmation | Flight | Route | Status |
|---|---|---|---|---|
| Jane Doe | 12345 | TU701 | Tunis → Paris | On Time |
| John Smith | 54321 | TU702 | Tunis → London | Delayed |
| Alice Johnson | 98765 | AF123 | Paris → New York | On Time |
| Bob Brown | 56789 | TU703 | Tunis → Rome | Cancelled |

Example conversation:

```
How's it going?
Can you tell me about my flight?
My name is Jane Doe and my confirmation is 12345
When does my flight depart?
```

## Tech stack

- Python
- LangChain (runnables, prompts, Pydantic output parsing)
- Groq (LLM)
- SQLite
- Streamlit