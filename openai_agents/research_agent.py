from agents import Agent,WebSearchTool,trace,Runner,function_tool
from agents.model_settings import ModelSettings
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

load_dotenv(override=True)

HOW_MANY_SEARCHES = 2
OPENAI_MODEL="gpt-5-nano"

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")

    query: str = Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")


planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model=OPENAI_MODEL,
    output_type=WebSearchPlan,
)


INSTRUCTIONS = "You are a research assistant. Given a search term, you search the web for that term and \
        produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 \
        words. Capture the main points. Write succintly, no need to have complete sentences or good \
        grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
        essence and ignore any fluff. Do not include any additional commentary other than the summary itself."
search_agent = Agent(
    name="Search_agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model=OPENAI_MODEL,
    model_settings=ModelSettings(tool_choice="required"),
)
    
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

INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)

class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")

    markdown_report: str = Field(description="The final report")

    follow_up_questions: list[str] = Field(description="Suggested topics to research further")

writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model=OPENAI_MODEL,
    output_type=ReportData,
)

async def plan_searches(query: str):
    """ Use the planner_agent to plan which searches to run for the query """
    print("Planning searches...")
    result = await Runner.run(planner_agent, f"Query: {query}")
    print(f"Will perform {len(result.final_output.searches)} searches")
    return result.final_output

async def perform_searches(search_plan: WebSearchPlan):
    """ Call search() for each item in the search plan """
    print("Searching...")
    tasks = [asyncio.create_task(search(item)) for item in search_plan.searches]
    results = await asyncio.gather(*tasks)
    print("Finished searching")
    return results

async def search(item: WebSearchItem):
    """ Use the search agent to run a web search for each item in the search plan """
    input = f"Search term: {item.query}\nReason for searching: {item.reason}"
    result = await Runner.run(search_agent, input)
    return result.final_output

async def write_report(query: str, search_results: list[str]):
    """ Use the writer agent to write a report based on the search results"""
    print("Thinking about report...")
    input = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await Runner.run(writer_agent, input)
    print("Finished writing report")
    return result.final_output

async def send_email(report: ReportData):
    """ Use the email agent to send an email with the report """
    print("Writing email...")
    result = await Runner.run(email_agent, report.markdown_report)
    print("Email sent")
    return report

query ="Latest Technologies and AI tools in 2026"

async def run_research():
    with trace("Research trace"):
        print("Starting research...")
        search_plan = await plan_searches(query)
        search_results = await perform_searches(search_plan)
        report = await write_report(query, search_results)
        await send_email(report)  
        print("Hooray!")

asyncio.run(run_research())