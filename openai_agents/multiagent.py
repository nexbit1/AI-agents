from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio

load_dotenv(override=True)

@function_tool
def sendEmail(body: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('EMAIL_SENDER'))
    to_email = To(os.environ.get('EMAIL_RECIEVER'))
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Hello Mate", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}
  
instructions1 = "You are a sales agent working for Nexbit Inc, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."

instructions2 = "You are a humorous, engaging sales agent working for Nexbit Inc, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."

instructions3 = "You are a busy sales agent working for Nexbit Inc, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."

salesInstruction = "You pick the best cold sales email from the given options. \
Imagine you are a customer and pick the one you are most likely to respond to. \
Do not give an explanation; reply with the selected email only."

sales_agent1 = Agent(name="Professional Sales Agent",instructions=instructions1,model="gpt-4o-mini")
sales_agent2 = Agent(name="Witty Sales Agent",instructions=instructions2,model="gpt-4o-mini")
sales_agent3 = Agent(name="Concise Sales Agent",instructions=instructions3,model="gpt-4o-mini")
sales_picker = Agent(name="sales_picker",instructions=salesInstruction,model="gpt-4o-mini")

async def salesAgentWriteMail():
    message = "Write a cold sales email"
    with trace("Parallel cold emails"):
        results = await asyncio.gather(
            Runner.run(sales_agent1,message),
            Runner.run(sales_agent2,message),
            Runner.run(sales_agent3,message),
        )

    return [result.final_output for result in results]

# outputs = asyncio.run(salesAgentWriteMail())
# emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)

async def salesPickerPickMail():
    best_email = await Runner.run(sales_picker,emails)
    return best_email.final_output

# best_email = asyncio.run(salesPickerPickMail())


description = "Write a cold sales email"
tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)
tools = [tool1, tool2, tool3, sendEmail]

manager_instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
 
3. Use the send_email tool to send the best email (and only the best email) to the user.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must send ONE email using the send_email tool — never more than one.
"""

sales_manager = Agent(name="Sales Manager", instructions=manager_instructions, tools=tools, model="gpt-4o-mini")

message = "Send a cold sales email addressed to 'Dear CEO'"
async def managerSendsMail():
    with trace("Sales manager"):
        await Runner.run(sales_manager, message)


asyncio.run(managerSendsMail())