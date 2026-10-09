from typing import TypeVar
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

load_dotenv()

T = TypeVar("T", bound=BaseModel)

def web_search(messages: list[BaseMessage], model: str | None, output: type[T], **model_options) -> T:
    model = model or os.getenv("OPENAI_MODEL")
    llm = init_chat_model(model, **model_options)
    structured_llm = llm.with_structured_output(
        output,
        tools=[{"type": "web_search"}],
        strict=True,
        include_raw=True,
    )
    result = structured_llm.invoke(messages)
    if result["parsing_error"]:
        raise result["parsing_error"]
    return result["parsed"]
