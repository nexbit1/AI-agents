from dotenv import load_dotenv
from agents import Agent, Runner, trace
import asyncio

load_dotenv(override=True)

agent = Agent(name="Doctor", instructions="You are a Doctor", model="gpt-4o-mini")

async def doctor_agent():
    result = await Runner.run(agent, "I feel dizzy, eyes feel tired is it because of vitamin D deficiency ")
    print(result.final_output)

asyncio.run(doctor_agent())
