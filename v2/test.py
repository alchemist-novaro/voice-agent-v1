import time
import uuid
from dotenv import load_dotenv

from src.workflow import Workflow

load_dotenv()

running = True

async def disconnect():
    global running
    running = False

workflow = Workflow(disconnect)

async def chat():
    print("Welcome to Real-time OpenAI Chatbot!")
    print("Type 'exit' to quit.\n")

    global running

    while running:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            running = False
            continue

        print("AI is typing...")

        try:
            stream = workflow.process(user_input)
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
            print()
        except KeyboardInterrupt:
            print("\nInterrupted!")
        # except Exception as e:
        #     print(f"\nError: {e}")

if __name__ == "__main__":
    import asyncio

    asyncio.run(chat())