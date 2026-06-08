import os
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
from pydantic import BaseModel


load_dotenv(override=True)
gemini = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"), 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

reader = PdfReader("nexbit/Profile.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

# print(linkedin)

with open("nexbit/summary.txt","r",encoding="utf-8") as f:
    summary = f.read();
# print(summary)

name = 'Nexbit'
system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer, say so."

system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."


# def chat(message,history):
#     messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
#     response = gemini.chat.completions.create(model="gemini-2.5-flash", messages=messages)
#     return response.choices[0].message.content


# gr.ChatInterface(chat).launch(share=True)

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
The Agent is playing the role of {name} and is representing {name} on their website. \
The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
The Agent has been provided with context on {name} in the form of their summary and LinkedIn details. Here's the information:"

evaluator_system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
evaluator_system_prompt += f"With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."

def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt


def evaluate(reply, message, history) -> Evaluation:
    messages = [{"role": "system", "content": evaluator_system_prompt}] + [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]
    response = gemini.beta.chat.completions.parse(model="gemini-2.5-flash-lite", messages=messages, response_format=Evaluation)
    return response.choices[0].message.parsed

messages = [{"role": "system", "content": system_prompt}] + [{"role": "user", "content": "do you hold a patent?"}]
response = gemini.chat.completions.create(model="gemini-2.5-flash", messages=messages)
reply = response.choices[0].message.content

evaluate(reply, "do you hold a patent?", messages[:1])


def rerun(reply, message, history, feedback):
    updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    response = gemini.chat.completions.create(model="gemini-2.5-flash", messages=messages)
    return response.choices[0].message.content

def chat(message, history):
    if "patent" in message:
        system = system_prompt + "\n\nthere is patent"
    else:
        system = system_prompt
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": message}]
    response = gemini.chat.completions.create(model="gemini-2.5-flash", messages=messages)
    reply =response.choices[0].message.content

    evaluation = evaluate(reply, message, history)
    
    if evaluation.is_acceptable:
        print("Passed evaluation - returning reply")
    else:
        print("Failed evaluation - retrying")
        print(evaluation.feedback)
        reply = rerun(reply, message, history, evaluation.feedback)       
    return reply

# gr.ChatInterface(chat).launch(share=True)

css = """
footer {display:none !important;}

.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
}

h1 {
    text-align:center;
    font-size:42px !important;
    margin-top:40px;
    margin-bottom:10px;
}

.subtitle {
    text-align:center;
    color:#888;
    margin-bottom:30px;
}

.prompt-card {
    padding:16px;
    border-radius:16px;
    border:1px solid #ddd;
    cursor:pointer;
    transition:0.2s;
}

.prompt-card:hover {
    transform:translateY(-2px);
}

.message {
    border-radius:18px !important;
}
"""

with gr.Blocks(
    theme=gr.themes.Soft(),
    css=css
) as demo:

    gr.Markdown( """ <h1 align="center">👨‍💻 Hi, I'm Omkar</h1>""")

    gr.HTML("""
    <div class='subtitle'>
        Ask me anything ;)
    </div>
    """)

    chatbot = gr.ChatInterface(
        fn=chat,
        show_progress="hidden",
        chatbot=gr.Chatbot(
            show_label=False,
            height=650
        ),
        textbox=gr.Textbox(
            placeholder="Chat with me..",
            container=False
        ),
        examples=[
            "Build a PHP REST API",
            "What are your skills",
            "Explain SQL and write a complex query.",
            "Tell me about you self"
        ]
    )

demo.launch()