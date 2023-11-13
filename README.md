# OpenAI Assistant

Create OpenAI Assistants and Manage Threads

🚧 under development 🚧

## Features

- asyncio for asynchronous calls to openai
- custom assistant creation 
- thread management
	- handles polling
	- function call support
- function to openapi converter

## Installation
```
pip install openai pydantic python-dotenv
```

## Usage
### Creating Assistants
see `assistant.py`   
example of creating a simple assistant with custom function
```
params = AssistantParams(
	model="gpt-4-1106-preview",
	name="Function Test",
	description="An that adds nuumbers",
	instructions="You add numbers together",
	tools=[Tool(type=ToolType.function, function=assistant_function)],
)

assistant = await assistant.create_assistant(params
```

### Managing Threads
see `thread.py`   
example of a full thread flow
```
thread = Thread(client, ASST_ID, functions=functions)
await thread.create_thread()
await thread.create_user_message("what's 8+9?")
await thread.run_thread("You are a personal math tutor. When asked a question, write and run Python code to answer the question.")
messages = await thread.get_messages()
```

### Try it Out
1. Define a function in `main.py`
2. Create openapi definition using `function_to_openapi` in `utils.py`
3. Create an assistant - see samples in `main.py`
4. Create and run a thread on assistant 
