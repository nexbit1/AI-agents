from config import OPENAI_MODEL
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from agents import Agent,function_tool
import os

@function_tool
def sendEmail(subject: str,body: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('EMAIL_SENDER'))
    to_email = To(os.environ.get('EMAIL_RECIEVER'))
    content = Content("text/html", body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}

INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[sendEmail],
    model=OPENAI_MODEL,
)

