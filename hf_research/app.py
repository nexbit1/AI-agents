import gradio as gr
from dotenv import load_dotenv
from research import research

load_dotenv(override=True)

async def run(query: str):
    async for chunk in research().run(query):
        yield chunk

# Added custom CSS classes for rounded corners and padding
custom_css = """
.container { max-width: 850px !important; margin: auto; padding-top: 2rem; }
.header-text { text-align: center; margin-bottom: 1rem; }
.subtitle { text-align: center; color: #666; margin-bottom: 2rem; font-size: 1.1em; }

/* Gives the textbox a soft rounded corner and slight inner padding */
.rounded-box textarea, .rounded-box {
    border-radius: 24px !important;
}

/* Gives the button a matching soft rounded corner */
.rounded-btn {
    border-radius: 24px !important;
}
.report-card {
    padding: 2rem 2.5rem !important; /* Generous breathing room for reading */
    border-radius: 16px !important;
    background-color: var(--background-fill-primary) !important; 
    border: 1px solid var(--border-color-primary) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important; /* Soft floating shadow */
    margin-top: 1.5rem !important;
    line-height: 1.6 !important; /* Better readability for long reports */
}
"""

theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "sans-serif"]
)

with gr.Blocks(theme=theme, css=custom_css, title='Research with Omkar') as ui:
    with gr.Column(elem_classes="container"):
        gr.Markdown("# ✨ Research with me", elem_classes="header-text")
        gr.Markdown("Enter a topic below to generate a comprehensive, in-depth research report.", elem_classes="subtitle")
        with gr.Row():
            ex1 = gr.Button("🔍 The Future of Quantum Computing", size="sm")
            ex2 = gr.Button("🌍 Global Economic Impact of AI", size="sm")
            ex3 = gr.Button("🧬 Recent Breakthroughs in CRISPR", size="sm")

        with gr.Row(equal_height=True):
            query_textbox = gr.Textbox(
                show_label=False, 
                placeholder="What topic would you like to research? Ask anything...", 
                scale=10, 
                container=False, 
                lines=1,
                max_lines=5,
                elem_classes="rounded-box" 
            )
            run_button = gr.Button(
                "Research", 
                variant="primary", 
                scale=0, 
                min_width=120,
                elem_classes="rounded-btn" 
            )
        with gr.Column(elem_classes="report-card"):
            report = gr.Markdown(
                "Your generated research report will appear here. "
                "Select an example above or type a topic to get started.",
                elem_classes="report-text"
            )
        ex1.click(fn=lambda: "The Future of Quantum Computing", outputs=query_textbox)
        ex2.click(fn=lambda: "Global Economic Impact of AI", outputs=query_textbox)
        ex3.click(fn=lambda: "Recent Breakthroughs in CRISPR", outputs=query_textbox)       
        run_button.click(fn=run, inputs=query_textbox, outputs=report)
        query_textbox.submit(fn=run, inputs=query_textbox, outputs=report)

        

ui.launch(inbrowser=True)