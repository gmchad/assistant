from enum import Enum
from typing import List, Dict, Union, Any, Optional
import json
import asyncio

class Thread:
  def __init__(self, client, assistant_id, functions={}):
    self.assistant_id = assistant_id
    self.functions = functions
    self.client = client
    self.thread = None
    self.run = None

  async def create_thread(self):
    try:
      thread = await self.client.beta.threads.create()
      self.thread = thread
      return thread
    except Exception as error:
      print("Error creating thread:", error)
      raise

  async def create_user_message(self, content):
    try:
      message = await self.client.beta.threads.messages.create(
        self.thread.id,
        role="user",
        content=content
      )
      return message
    except Exception as error:
      print("Error creating user message:", error)
      raise

  async def run_thread(self, instructions=""):
    try:
      run = await self.client.beta.threads.runs.create(
        self.thread.id,
        assistant_id=self.assistant_id,
        instructions=instructions
      )
      self.run = run
      await self.poll_run()
    except Exception as error:
      print("Error running thread:", error)
      raise
  
  async def get_messages(self):
    try:
      messages = await self.client.beta.threads.messages.list(self.thread.id, order="asc")
      messages = messages.data
      # Now, iterate over the messages and extract the content.
      extracted_messages = []
      for message in messages:
        for content in message.content:
          if content.type == 'text':
            extracted_messages.append(content.text.value)
      return extracted_messages
    except Exception as error:
      print("Error getting messages:", error)
      raise

  async def poll_run(self):
    try:
      self.run = await self.client.beta.threads.runs.retrieve(self.run.id, thread_id=self.thread.id)
      while self.run.status not in ['expired', 'completed', 'failed', 'cancelled']:
      # while self.run.status not in ['expired', 'failed', 'cancelled']:
        print(f'Current status: {self.run.status}')
        # check for function call
        if self.run.status == "requires_action":
          tool_outputs = []
          for tool_call in self.run.required_action.submit_tool_outputs.tool_calls:
            function = tool_call.function
            args = json.loads(function.arguments)
            tool_outputs.append({
              "tool_call_id": tool_call.id,
              "output": self.functions[function.name](**args)
            })
          self.run = await self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=self.run.id,
            tool_outputs=tool_outputs
          )
        self.run = await self.client.beta.threads.runs.retrieve(self.run.id, thread_id=self.thread.id)
        await asyncio.sleep(1)
    except Exception as error:
      print("Error polling run status:", error)
      raise