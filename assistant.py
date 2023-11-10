from openai import OpenAI
from enum import Enum
from typing import List, Dict, Union, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

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
  name: Optional[str] = Field(
    None, max_length=256, description="The name of the assistant.")
  description: Optional[str] = Field(
    None, max_length=512, description="The description of the assistant.")
  instructions: Optional[str] = Field(
    None, max_length=32768, description="The system instructions that the assistant uses.")
  tools: Optional[List[Tool]] = Field(
    None, description="A list of tool enabled on the assistant.")
  file_ids: Optional[List[str]] = Field(
    None, description="A list of File IDs attached to this assistant.")
  metadata: Optional[dict] = Field(
    None, description="Set of 16 key-value pairs that can be attached to an object.")
  
class Assistant():
  def __init__(self, client):
    self.client = client
    
  async def create_assistant(self, params: AssistantParams):
    assistant = await self.client.beta.assistants.create(
      name=params.name if params.name else "",
      description=params.description if params.description else "",
      instructions=params.instructions if params.instructions else "",
      tools=[{'type': tool.type.value, 'function': tool.function}
          for tool in params.tools] if params.tools else [],
      model=params.model if params.model else "gpt-4-1106-preview",
      file_ids=params.file_ids if params.file_ids else [],
      metadata=params.metadata if params.metadata else {}
    )
    return assistant