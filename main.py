from openai import AsyncOpenAI
from enum import Enum
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json
import asyncio

from assistant import Assistant, AssistantParams, Tool, ToolType
from thread import Thread

load_dotenv()

client = AsyncOpenAI()

### sample functions
def addTwo(num_one: int, num_two: int) -> int:
  """
  Add two numbers together.

  Args:
      num_one (int): The first number to add.
      num_two (int): The second number to add.

  Returns:
      int: The sum of num_one and num_two.
  """
  return num_one + num_two

async def create_root_assistant(assistant: Assistant):
  with open('assistant_function.json', 'r') as f:
    assistant_function = json.load(f)

  params = AssistantParams(
    model="gpt-4-1106-preview",
    name="Assistant Inception",
    description="An Assistant that creates more Assistant",
    instructions="Your job is to create more OpenAI Assistants. You can use your function calling tool to create assistants. Default to gpt-4-1106-preview as the model if not specified.",
    tools=[Tool(type=ToolType.function, function=assistant_function)],
  )

  assistant = await assistant.create_assistant(params)
  return assistant


async def create_simple_assistant(assistant: Assistant):
  with open('simple_function.json', 'r') as f:
    assistant_function = json.load(f)

  params = AssistantParams(
    model="gpt-4-1106-preview",
    name="Function Test",
    description="An that adds nuumbers",
    instructions="You add numbers together",
    tools=[Tool(type=ToolType.function, function=assistant_function)],
  )

  assistant = await assistant.create_assistant(params)
  return assistant

async def main():
  #assistant = Assistant(client)
  #simple_assistant = await create_simple_assistant(assistant)
  #print(simple_assistant)
  
  functions = {"addTwo": addTwo}
  thread = Thread(client, "asst_vOQzvZ6gLNOPYnUyxgI98WWY", functions=functions) # simple assistant "asst_vOQzvZ6gLNOPYnUyxgI98WWY"
  await thread.create_thread()
  await thread.create_user_message("what's 8+9?")
  await thread.run_thread("You are a personal math tutor. When asked a question, write and run Python code to answer the question.")
  messages = await thread.get_messages()
  print(messages)
  
if __name__ == "__main__":
  asyncio.run(main())
  