from openai import OpenAI, OpenAIError
from enum import Enum
from typing import List, Dict, Union, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json
import os

load_dotenv()

ROOT_ASSISTANT_NAME = "Assistant Inception"

client = OpenAI()

class Function(BaseModel):
    name: str
    description: str
    parameters: Dict[Any, Any]

class ToolType(str, Enum):
    function = "function"
    code_interpreter = "code_interpreter"
    retrieval = "retrieval"

class Tool(BaseModel):
    type: ToolType
    function: Optional[Dict]
    
class AssistantParams(BaseModel):
    model: str = Field(..., description="ID of the model to use.")
    name: Optional[str] = Field(None, max_length=256, description="The name of the assistant.")
    description: Optional[str] = Field(None, max_length=512, description="The description of the assistant.")
    instructions: Optional[str] = Field(None, max_length=32768, description="The system instructions that the assistant uses.")
    tools: Optional[List[Tool]] = Field(None, description="A list of tool enabled on the assistant.")
    file_ids: Optional[List[str]] = Field(None, description="A list of File IDs attached to this assistant.")
    metadata: Optional[dict] = Field(None, description="Set of 16 key-value pairs that can be attached to an object.")

def create_assistant(params: AssistantParams):
    tools=[{'type': tool.type.value, 'function': tool.function} for tool in params.tools] if params.tools else []
    print(tools)
    assistant = client.beta.assistants.create(
        name=params.name if params.name else "",
        description=params.description if params.description else "",
        instructions=params.instructions if params.instructions else "",
        tools=[{'type': tool.type.value, 'function': tool.function} for tool in params.tools] if params.tools else [],
        model=params.model if params.model else "gpt-4-1106-preview",
        file_ids=params.file_ids if params.file_ids else [],
        metadata=params.metadata if params.metadata else {}
    )
    return assistant

def create_root_assistant():
    with open('assistant_function.json', 'r') as f:
      assistant_function = json.load(f)

    params = AssistantParams(
      model="gpt-4-1106-preview",
      name= ROOT_ASSISTANT_NAME,
      description="An Assistant that creates more Assistant",
      instructions="Your job is to create more OpenAI Assistants. You can use your function calling tool to create assistants. Default to gpt-4-1106-preview as the model if not specified.",
      tools=[Tool(type=ToolType.function, function=assistant_function)],
      )

    assistant = create_assistant(params)
    print(assistant)

def create_assistant_thread():
    thread = client.beta.threads.create(
        messages = [
            {
                "role": "user",
                "content": "please create a new assistant that can give me live weather reports. You may need to implement a function that can call the correct api"
            }
        ]
    )
    print(thread)
    return thread

def invoke_root_assistant():
    thread = create_assistant_thread()
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id="asst_VlCwS6nWjKERsar8Y6nnTMRh"
    )
    print(run)
    return run

if __name__ == "__main__":
    create_root_assistant()
