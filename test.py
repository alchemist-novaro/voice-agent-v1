import time
import uuid
from dotenv import load_dotenv

from src.agent import Agent

load_dotenv()

async def disconnect():
    print("The end")

agent = Agent("./workflows/test.yaml", uuid.uuid4(), disconnect)

async def chat():
    print("Welcome to Real-time OpenAI Chatbot!")
    print("Type 'exit' to quit.\n")

    while True:
        if not agent.input_required:
            time.sleep(0.1)
            continue

        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            break

        print("AI is typing...")

        try:
            stream = agent.process(user_input)
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
            print()
        except KeyboardInterrupt:
            print("\nInterrupted!")
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    import asyncio

    asyncio.run(chat())