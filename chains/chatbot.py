from pprint import pprint
from typing import Optional
from retrieval import get_flight_info

from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableAssign
from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel, Field

from settings import GROQ_API_KEY, GROQ_MODEL

llm = ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0)
chat_llm = llm | StrOutputParser()
instruct_llm = llm | StrOutputParser()

# ---------- Knowledge base ----------
class KnowledgeBase(BaseModel):
    first_name: str = Field("unknown", description="User's first name, `unknown` if unknown")
    last_name: str = Field("unknown", description="User's last name, `unknown` if unknown")
    confirmation: Optional[int] = Field(None, description="Flight confirmation number, null if unknown")
    discussion_summary: str = Field("", description="Short summary of the discussion so far")

def get_key_fn(base: KnowledgeBase) -> dict:
    return {
        "first_name": base.first_name,
        "last_name": base.last_name,
        "confirmation": base.confirmation,
    }

# ---------- RExtract (from the notebook) ----------
def RExtract(pydantic_class, llm, prompt):
    parser = PydanticOutputParser(pydantic_object=pydantic_class)
    instruct_merge = RunnableAssign({"format_instructions": lambda x: parser.get_format_instructions()})

    def preparse(string):
        if "{" not in string: string = "{" + string
        if "}" not in string: string = string + "}"
        return string.replace("\\_", "_").replace("\n", " ")

    repair_prompt = prompt + [("human", "Return exactly one valid JSON object matching the schema. "
                                         "No extra braces, second object, or commentary.")]
    chain = instruct_merge | prompt | llm | preparse | parser
    repair = instruct_merge | repair_prompt | llm | preparse | parser
    return chain.with_fallbacks([repair], exceptions_to_handle=(OutputParserException,))

parser_prompt = ChatPromptTemplate.from_template(
    "You track info about a conversation with an airline customer. "
    "Update the knowledge base using the user's new message. "
    "Keep old values unless the user gives new ones. Never invent details."
    "\n\n{format_instructions}"
    "\n\nOLD KNOWLEDGE BASE: {know_base}"
    "\n\nASSISTANT LAST MESSAGE: {output}"
    "\n\nUSER MESSAGE: {input}"
    "\n\nNEW KNOWLEDGE BASE:"
)

knowbase_getter = RExtract(KnowledgeBase, instruct_llm, parser_prompt)

def database_getter(d: dict) -> str:
    kb = d["know_base"]
    if kb.first_name == "unknown" or kb.last_name == "unknown" or kb.confirmation is None:
        return "No booking information is available yet."
    return get_flight_info(get_key_fn(kb))

internal_chain = (
    RunnableAssign({"know_base": knowbase_getter})
    | RunnableAssign({"context": database_getter})
)

# ---------- External chain ----------
external_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly chatbot for SkyFlow Airlines. Be concise and warm. "
     "Your running knowledge base is: {know_base}. It is for you only; do not mention it. "
     "Retrieved booking information: {context}. "
     "\n\nRules:"
     "\n1. For greetings and small talk (hello, how are you), reply naturally and briefly, "
     "then offer help. Do NOT ask for any personal details."
     "\n2. For general questions about SkyFlow or travel, answer normally. Do not ask for personal details."
     "\n3. Only if the user asks about THEIR OWN flight or booking, and no booking information "
     "is available, ask for their first name, last name and confirmation number."
     "\n4. Never ask for the same thing twice in a row. If the user says they do not have "
     "their confirmation number, explain that for privacy you can only share booking details "
     "with it, suggest checking their confirmation email or ticket, and offer to help with "
     "general questions instead."
     "\n5. Only discuss booking details that appear in the retrieved booking information. "
     "The check happens automatically; you cannot run it manually."),
    ("user", "{input}"),
])

external_chain = external_prompt | chat_llm

# ---------- State + chat function ----------
state = {"know_base": KnowledgeBase()}

def chat_gen(message, history=None, return_buffer=True):
    global state
    history = [] if history is None else history
    state["input"] = message
    state["history"] = history

    last_assistant_msg = ""
    for entry in reversed(history):
        if entry.get("role") == "assistant":
            last_assistant_msg = entry.get("content", "")
            break
    state["output"] = last_assistant_msg

    state = internal_chain.invoke(state)

    print("\n--- Internal State Update ---")
    pprint({k: v for k, v in state.items() if k != "history"})

    buffer = ""
    for token in external_chain.stream(state):
        buffer += token
        yield buffer if return_buffer else token

def update_state(state: dict, message: str, history: list) -> dict:
    """Run the internal chain on a copy of the state and return the new state."""
    state = dict(state)
    state["input"] = message
    state["history"] = history

    last_assistant_msg = ""
    for entry in reversed(history):
        if entry.get("role") == "assistant":
            last_assistant_msg = entry.get("content", "")
            break
    state["output"] = last_assistant_msg

    return internal_chain.invoke(state)