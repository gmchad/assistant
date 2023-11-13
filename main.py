from openai import AsyncOpenAI, OpenAIError
from enum import Enum
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json
import asyncio

from assistant import Assistant, AssistantParams, Tool, ToolType
from functions.math import addTwo

from thread import Thread

load_dotenv()

client = AsyncOpenAI()

async def create_root_assistant(assistant: Assistant):
  with open('assistant_function.json', 'r') as f:
    assistant_function = json.load(f)

    params = AssistantParams(
      model="gpt-4-1106-preview",
      name= "Assistant Inception",
      description="An Assistant that creates more Assistant",
      instructions="Your job is to create more OpenAI Assistants. You can use your function calling tool to create assistants. Default to gpt-4-1106-preview as the model if not specified.",
      tools=[Tool(type=ToolType.function, function=assistant_function)],
      metadata={'assistant_type': 'inception'}
      )

  assistant = await assistant.create_assistant(params)
  return assistant


async def create_simple_assistant(assistant: Assistant):
  with open('simple_function.json', 'r') as f:
    assistant_function = json.load(f)

    # create_root_assistant()
  params = AssistantParams(
    model="gpt-4-1106-preview",
    name="Function Test",
    description="An AI that adds numbers",
    instructions="You add numbers together",
    tools=[Tool(type=ToolType.function, function=assistant_function)],
    metadata={'assistant_type': 'addition'}
  )

  assistant = await assistant.create_assistant(params)
  return assistant

async def testAdditionAssistant(test_query:str = "what's 8+9?"):
  # fetch available assistants to see if we already have an addition Assistant.
  my_assistants = await client.beta.assistants.list(
      order="desc",
      limit="20",
  )

  math_assistants = [a for a in my_assistants.data if a.metadata.get('assistant_type') == 'addition']
  if len(math_assistants) > 0:
    simple_assistant = math_assistants[0]
    print('fetched math assistant:', simple_assistant)
  else:
    print('creating new math assistant')
    assistant = Assistant(client)
    simple_assistant = await create_simple_assistant(assistant)

  asst_id = simple_assistant.id  
  # create a new thread
  functions = {"addTwo": addTwo}
  thread = Thread(client, asst_id, functions=functions)
  await thread.create_thread()

  # test input and output
  await thread.create_user_message(test_query)
  await thread.run_thread("You are a personal math tutor. When asked a question, write and run Python code to answer the question.")
  messages = await thread.get_messages()
  print(messages)

  # delete the assistant?

async def main():
  await testAdditionAssistant()
  
if __name__ == "__main__":
  asyncio.run(main())