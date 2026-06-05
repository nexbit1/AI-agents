import os
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
from pydantic import BaseModel

load_dotenv(override=True)

class nexbit:
    def __init__(self):
        self.openai = OpenAI()
        self.name = "Omkar Nagvekar"
        reader = PdfReader("nexbit/Profile.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("nexbit/summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()

    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
            particularly questions related to {self.name}'s career, background, skills and experience. \
            Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
            You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
            Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
            If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
            If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self,message,history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        response = self.openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
        return response.choices[0].message.content






if __name__ == "__main__":
    nexbit = nexbit()
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
        fn=nexbit.chat,
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

    demo.launch(share=True)