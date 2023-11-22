import os
from openai import AsyncOpenAI, OpenAIError
from enum import Enum
from pydantic import BaseModel, Field
from dotenv import load_dotenv

import json
import asyncio

from assistant import Assistant, AssistantParams, Tool, ToolType
from functions.math import addTwo
from functions.fastapi import callFastAPI, inputText

from thread import Thread

load_dotenv()

FUNCTION_TEMPLATES_DIR = "function_templates"

client = AsyncOpenAI()
threads = {}

async def create_root_assistant(assistant: Assistant):
  fpath = os.path.join(FUNCTION_TEMPLATES_DIR, "assistant_function.json")
  with open(fpath, 'r') as f:
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
  fpath = os.path.join(FUNCTION_TEMPLATES_DIR, "simple_function.json")
  with open(fpath) as f:
    assistant_function = json.load(f)

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

async def create_fastapi_assistant(assistant: Assistant):
  tools = []
  fpaths = [ os.path.join(FUNCTION_TEMPLATES_DIR, fname) for fname in ["call_pyppeteer.json","input_text.json"] ]
  for fpath in fpaths:
    with open(fpath, 'r') as f:
      tools.append(Tool(type=ToolType.function, function=json.load(f)))

  params = AssistantParams(
    model="gpt-3.5-turbo-1106",
    name="FastAPI",
    description="An AI that calls FastAPI",
    instructions="You make requests to FastAPI in order to navigate to web pages perform actions such as clicking buttons, taking screenshots or inputting text.",
    tools=tools,
    metadata={'assistant_type': 'fastapi'}
  )

  assistant = await assistant.create_assistant(params)
  return assistant

async def create_assistant_with_type(assistant_type:str):
  if assistant_type == 'inception':
    assistant = Assistant(client)
    assistant = await create_root_assistant(assistant)
  elif assistant_type == 'addition':
    assistant = Assistant(client)
    assistant = await create_simple_assistant(assistant)
  elif assistant_type == 'fastapi':
    assistant = Assistant(client)
    assistant = await create_fastapi_assistant(assistant)
  elif assistant_type == 'search':
    assistant = await create_search_assistant()
  else:
    raise Exception('Invalid assistant type')

  return assistant

async def getAssistantWithType(assistant_type:str):
  my_assistants = await client.beta.assistants.list(
      order="desc",
      limit="20",
  )

  test_assistants = [a for a in my_assistants.data if a.metadata.get('assistant_type') == assistant_type]
  if len(test_assistants) > 0:
    assistant = test_assistants[0]
    print('fetched assistant:', assistant)
  else:
    print('creating new assistant')
    assistant = await create_assistant_with_type(assistant_type)

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
  # await thread.run_thread("You are a personal math tutor. When asked a question, write and run Python code to answer the question.")
  await thread.run_thread("You are a helpful assistant who can look up information online in order to answer questions.")

  messages = await thread.get_messages()
  print(messages)

  # delete the assistant?

async def getMessages(thread_id: str):
  try:
    thread = threads[thread_id]
    messages = await thread.get_messages()
    return { "messages": messages, 'thread_id': thread_id }
  except Exception as error:
    print("Error getting messages:", error)
    return { "messages": [] }

# TODO: properly url encode any passed URLs?
async def sendMessage(test_query:str = "Take a screenshot of Wikipedia.", thread_id:str = None):

  if thread_id is not None and threads.get(thread_id):
    thread = threads[thread_id]
  else:
    assistant = await getAssistantWithType('fastapi')
    functions = { "call_fastapi": callFastAPI, "input_text": inputText }
    thread = Thread(client, assistant.id, functions=functions)
    await thread.create_thread()
    threads[thread.thread.id] = thread

  # test input and output
  await thread.create_user_message(test_query)
  await thread.run_thread("You are an assistant that can call FastAPI to navigate to web pages, take screenshots and input text.")
  return { "thread_id": thread.thread.id }

async def main():
  await sendMessage("which articles are linked to on Venture Beat's homepage? ")
  
if __name__ == "__main__":
  asyncio.run(main())