# Trigger rebuild

import gradio as gr
import google.generativeai as genai
import os
from PIL import Image
from gtts import gTTS
import uuid
import random
import json
import re

API_KEY = os.environ.get("GEMINI_API_KEY")

CAREER_TIPS = [
    "**Build a Portfolio:** Even small projects showcase your skills. Start a GitHub repository for your code or a Behance profile for your designs.",
    "**Network Actively:** Connect with professionals on LinkedIn. Don't just send a request; add a personalized note about why you want to connect.",
    "**Learn to Learn:** The most valuable skill is learning how to learn effectively. Find courses, read books, and practice consistently.",
    "**Soft Skills Matter:** Communication, teamwork, and problem-solving are just as important as technical skills. Practice them daily.",
    "**Seek Feedback:** Don't be afraid of criticism. Ask mentors or peers to review your work. It's the fastest way to improve.",
    "**Stay Curious:** The world is constantly changing. Read news from your industry, follow thought leaders, and never stop asking 'why?'"
]

def get_gemini_response(api_key_from_input, system_prompt, user_input_parts=[]):
    final_api_key = API_KEY if API_KEY else api_key_from_input
    if not final_api_key:
        return "API Key not found. Please provide your key or set it up in your deployment environment."

    try:
        genai.configure(api_key=final_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        return f"API Key Configuration Error: {e}"

    full_prompt = [system_prompt] + user_input_parts
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the response: {e}"

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en', tld='co.in', slow=False)
        filename = f"/tmp/output_{uuid.uuid4()}.mp3"
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"Error in TTS: {e}")
        return None

def build_interface():
    dark_theme = gr.themes.Base(primary_hue=gr.themes.colors.purple, secondary_hue=gr.themes.colors.blue, neutral_hue=gr.themes.colors.gray).set(
        body_background_fill="#121212", body_text_color="#FFFFFF", background_fill_primary="#1E1E1E",
        border_color_primary="#333333", link_text_color="#A084E8", button_secondary_background_fill="#2B2B2B",
        button_secondary_background_fill_hover="#3C3C3C", button_primary_background_fill="#6D28D9",
        button_primary_background_fill_hover="#5B21B6",
    )

    with gr.Blocks(theme=dark_theme, css="""
        .gradio-container { background-color: #121212; } #chatbot .user { background-color: #1E1E1E !important; }
        #chatbot .bot { background-color: #282A36 !important; } .gradio-audio>div>audio{ background-color: #2B2B2B; }
        """) as demo:

        gr.Markdown(
            """
            <div style="text-align: center; padding-bottom: 10px;">
                <h1 style="color: #D8B4FE;">🧘 VMPX</h1>
                <p style="color: #A0A0A0; font-size: 1.1em;">The Complete AI Career Guide</p>
            </div>
            """
        )

        with gr.Tabs():
            with gr.TabItem("Chat with VMPX"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🛠️ Controls")
                        api_key_box = gr.Textbox(label="Google AI Studio API Key", type="password", placeholder="Paste your API key...", visible=not API_KEY)
                        file_box = gr.File(label="Upload Image or PDF", file_types=["image", ".pdf"])
                        voice_input = gr.Audio(sources=["microphone"], type="filepath", label="Speak to VMPX")
                        gr.Markdown("---")
                        gr.Markdown("### 💡 Daily Career Tip")
                        daily_tip = gr.Markdown(value=random.choice(CAREER_TIPS))
                        gr.Markdown("---")
                        gr.Markdown("### ⚙️ Chat Actions")
                        clear_chat_btn = gr.Button("🗑️ Clear Chat")
                        export_chat_btn = gr.Button("📄 Export Chat (.txt)")
                        download_file = gr.File(visible=False)

                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(elem_id="chatbot", label="VMPX Counsel", height=600,
                            value=[[None, "Hello! I am VMPX. Use the controls on the left or type your question below."]],
                            avatar_images=(None, "https://i.ibb.co/3fdnJpD/nirvana-logo.png"))
                        audio_output = gr.Audio(visible=False, autoplay=True)
                        with gr.Row():
                            msg_textbox = gr.Textbox(label="Your Question", placeholder="Type your question here... (Shift+Enter for new line)", scale=4, container=False, elem_id="chat_input")
                            submit_button = gr.Button("Ask", variant="primary", scale=1, min_width=150, elem_id="submit_button")

            with gr.TabItem("🧠 Mind Map Visualizer"):
                gr.Markdown("## Create a Mind Map")
                gr.Markdown("Enter a topic or paste a block of text, and NIRVANA will generate a visual mind map to help you organize your thoughts.")
                with gr.Row():
                    mind_map_input = gr.Textbox(label="Topic or Text", lines=10, placeholder="e.g., Key concepts of Machine Learning")
                    generate_map_btn = gr.Button("Generate Mind Map", variant="primary")
                mind_map_output = gr.Markdown("Your mind map will appear here...")

            with gr.TabItem("📺 Learning Hub"):
                gr.Markdown("## Find Top YouTube Tutorials")
                gr.Markdown("Ask for a tutorial on any topic, and NIRVANA will find the 5 best videos for you.")
                video_topic_input = gr.Textbox(label="What do you want to learn about?", placeholder="e.g., Introduction to Python for beginners")
                find_video_btn = gr.Button("Find Videos", variant="primary")
                video_recommendations_output = gr.Markdown("Your video recommendations will appear here.")

            with gr.TabItem("📄 Resume Analyzer"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Get Instant Feedback on Your Resume")
                        gr.Markdown("Upload your resume (PDF format) and NIRVANA will provide a detailed analysis and suggestions for improvement.")
                        resume_file_input = gr.File(label="Upload Your Resume", file_types=[".pdf"])
                        analyze_resume_btn = gr.Button("Analyze My Resume", variant="primary")
                    with gr.Column():
                        gr.Markdown("### Resume Analysis")
                        resume_output = gr.Markdown("Your feedback will appear here...")

            with gr.TabItem("🎙️ Mock Interview"):
                gr.Markdown("## Practice Your Interview Skills")
                interview_state = gr.State([])
                interview_role = gr.Dropdown(["Software Engineer", "Data Scientist", "Data Analyst", "Product Manager", "UX/UI Designer", "Marketing Manager", "Cybersecurity Analyst", "DevOps Engineer", "AI/ML Engineer"], label="Select a Job Role")
                start_interview_btn = gr.Button("Start Interview", variant="primary")
                interview_chatbot = gr.Chatbot(label="Interview Session", height=400)
                interview_answer = gr.Textbox(label="Your Answer", placeholder="Type your answer here...")
                submit_interview_answer_btn = gr.Button("Submit Answer")

            with gr.TabItem("📊 Skill Gap Analyzer"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Find Your Path to a New Career")
                        gr.Markdown("Tell us your current skills and your desired job role. NIRVANA will create a personalized learning plan to bridge the gap.")
                        current_skills = gr.Textbox(label="Your Current Skills", placeholder="e.g., Python, SQL, Communication")
                        desired_role = gr.Textbox(label="Your Desired Job Role", placeholder="e.g., Data Scientist")
                        analyze_gap_btn = gr.Button("Analyze Skill Gap", variant="primary")
                    with gr.Column():
                        gr.Markdown("### Your Personalized Learning Plan")
                        skill_gap_output = gr.Markdown("Your plan will appear here...")

            with gr.TabItem("✍️ Cover Letter Writer"):
                gr.Markdown("## Generate a Professional Cover Letter")
                with gr.Row():
                    with gr.Column():
                        job_desc = gr.Textbox(label="Paste Job Description Here", lines=10)
                        user_skills = gr.Textbox(label="Your Key Skills & Experiences", lines=5, placeholder="e.g., 3 years of Python experience, Led a team project...")
                        generate_letter_btn = gr.Button("Write My Cover Letter", variant="primary")
                    with gr.Column():
                        gr.Markdown("### Your Generated Cover Letter")
                        cover_letter_output = gr.Markdown("Your letter will appear here...")

            with gr.TabItem("🔗 LinkedIn Optimizer"):
                gr.Markdown("## Optimize Your LinkedIn 'About' Section")
                linkedin_about = gr.Textbox(label="Paste Your Current 'About' Section Here", lines=10)
                optimize_linkedin_btn = gr.Button("Optimize My Profile", variant="primary")
                linkedin_output = gr.Markdown("### Your Optimized 'About' Section")

            with gr.TabItem("🎯 Career Goal Planner"):
                gr.Markdown("## Break Down Your Career Goals")
                career_goal = gr.Textbox(label="What is your long-term career goal?", placeholder="e.g., Become a Senior AI Engineer at a top tech company in 5 years.")
                plan_goal_btn = gr.Button("Create My Action Plan", variant="primary")
                goal_plan_output = gr.Markdown("### Your Actionable Steps")

            with gr.TabItem("✨ Career Personality Quiz"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Discover Your Career Archetype")
                        q1 = gr.Radio(["Solving complex puzzles", "Creating something new", "Helping and guiding people", "Organizing and planning"], label="1. Which activity energizes you the most?")
                        q2 = gr.Radio(["Working with data and numbers", "Working with designs and visuals", "Working in a team", "Working independently"], label="2. What is your ideal work environment?")
                        q3 = gr.Radio(["A clear, logical problem", "An open-ended creative brief", "A social or community issue", "A complex project with many moving parts"], label="3. What kind of challenge do you enjoy tackling?")
                        quiz_submit_btn = gr.Button("Analyze My Personality", variant="primary")
                    with gr.Column():
                        gr.Markdown("### Your Personalized Suggestion")
                        quiz_output = gr.Markdown("Your results will appear here...")

        def main_chat_respond(user_message, chat_history, api_key, uploaded_file, voice_file):
            input_for_history = user_message if user_message else "[Voice Input]"
            if uploaded_file: input_for_history += f"\n*[File: {os.path.basename(uploaded_file.name)}]*"
            chat_history.append((input_for_history, None))
            yield "", chat_history, None, None, None

            system_prompt = "You are 'VMPX', an expert AI Career Counselor..."
            user_parts = []
            if user_message: user_parts.append(user_message)
            if uploaded_file: user_parts.append(genai.upload_file(path=uploaded_file.name))
            if voice_file: user_parts.append(genai.upload_file(path=voice_file))

            bot_response_text = get_gemini_response(api_key, system_prompt, user_parts)
            chat_history[-1] = (chat_history[-1][0], bot_response_text)
            audio_response_path = text_to_speech(bot_response_text)
            yield "", chat_history, audio_response_path, None, None

        submit_button.click(main_chat_respond, [msg_textbox, chatbot, api_key_box, file_box, voice_input], [msg_textbox, chatbot, audio_output, file_box, voice_input])
        msg_textbox.submit(main_chat_respond, [msg_textbox, chatbot, api_key_box, file_box, voice_input], [msg_textbox, chatbot, audio_output, file_box, voice_input])

        def clear_chat(): return [], None, random.choice(CAREER_TIPS)
        clear_chat_btn.click(clear_chat, outputs=[chatbot, audio_output, daily_tip])

        def export_chat(chat_history):
            history_str = "VMPX Chat History\n\n"
            for turn in chat_history:
                user = f"You: {turn[0]}\n" if turn[0] else ""
                bot = f"NIRVANA: {turn[1]}\n\n" if turn[1] else ""
                history_str += f"{user}{bot}"
            filepath = f"/tmp/VMPX_chat_{uuid.uuid4()}.txt"
            with open(filepath, "w") as f: f.write(history_str)
            return gr.File(value=filepath, visible=True)
        export_chat_btn.click(export_chat, inputs=chatbot, outputs=download_file)

        def generate_mind_map(topic, api_key):
            system_prompt = """
            You are a mind map generation expert. The user will provide a topic or text. Your task is to generate a structured mind map for it using Mermaid syntax. The mind map should be hierarchical, logical, and easy to read.
            IMPORTANT: Your ONLY output should be the Mermaid code block. Do not include any other text or explanation.
            Example:
            ```mermaid
            mindmap
              root((Main Topic))
                (Child 1)
                  (Grandchild 1.1)
                  (Grandchild 1.2)
                (Child 2)
            ```
            """
            return get_gemini_response(api_key, system_prompt, [topic])
        generate_map_btn.click(generate_mind_map, [mind_map_input, api_key_box], mind_map_output)

        def find_youtube_videos(topic, api_key):
            system_prompt = """
            You are a YouTube video search expert. A user will provide a topic. Find 5 relevant, high-quality, and popular tutorial or explanation videos for that topic on YouTube.
            IMPORTANT: Your ONLY output should be a JSON string representing a list of objects. Each object should have two keys: "title" and "video_id" (the 11-character YouTube Video ID). Do not include any other text or explanation.
            Example:
            [
              {"title": "Python for Beginners - Full Course", "video_id": "eWRfhZ_sgpM"},
              {"title": "Learn Python - Full Course for Beginners [Tutorial]", "video_id": "rfscVS0vtbw"}
            ]
            """
            response_text = get_gemini_response(api_key, system_prompt, [topic]).strip()
            try:
                if response_text.startswith("```json"):
                    response_text = response_text[7:-3].strip()

                videos = json.loads(response_text)

                markdown_output = "### Top 5 Video Recommendations:\n\n"
                for i, video in enumerate(videos):
                    title = video.get("title", "No Title")
                    video_id = video.get("video_id", "")
                    if video_id and re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                        markdown_output += f"{i+1}. [{title}](https://www.youtube.com/watch?v={video_id})\n"
                return markdown_output
            except (json.JSONDecodeError, TypeError, AttributeError) as e:
                print(f"Error parsing video list: {e}")
                return "Sorry, I couldn't retrieve a valid list of videos for that topic. Please try again."
        find_video_btn.click(find_youtube_videos, [video_topic_input, api_key_box], video_recommendations_output)

        def start_interview(role, api_key):
            if not role: return "Please select a role first.", [], []
            system_prompt = f"You are a hiring manager conducting a mock interview for a '{role}' position. Start the interview by greeting the candidate and asking the first behavioral or technical question. Be encouraging."
            first_question = get_gemini_response(api_key, system_prompt)
            interview_history = [ (None, first_question) ]
            return interview_history, interview_history
        start_interview_btn.click(start_interview, inputs=[interview_role, api_key_box], outputs=[interview_chatbot, interview_state])

        def continue_interview(answer, history, role, api_key):
            history.append( (answer, None) )
            system_prompt = f"You are a hiring manager continuing a mock interview for a '{role}' position. The candidate's previous answers are in the chat history. Ask the next logical question based on their last answer, or provide brief feedback and then ask the next question. Keep the interview flowing."
            user_parts = [json.dumps(history)]
            next_question = get_gemini_response(api_key, system_prompt, user_parts)
            history[-1] = (answer, next_question)
            return history, history, ""
        submit_interview_answer_btn.click(continue_interview, [interview_answer, interview_state, interview_role, api_key_box], [interview_chatbot, interview_state, interview_answer])

        def generate_cover_letter(job_desc, skills, api_key):
            system_prompt = "You are a professional cover letter writer..."
            user_parts = [f"Job Description:\n{job_desc}\n\nMy Skills/Experience:\n{skills}"]
            return get_gemini_response(api_key, system_prompt, user_parts)
        generate_letter_btn.click(generate_cover_letter, [job_desc, user_skills, api_key_box], cover_letter_output)

        def optimize_linkedin(about_text, api_key):
            system_prompt = "You are a LinkedIn profile optimization expert..."
            return get_gemini_response(api_key, system_prompt, [about_text])
        optimize_linkedin_btn.click(optimize_linkedin, [linkedin_about, api_key_box], linkedin_output)

        def plan_goal(goal, api_key):
            system_prompt = "You are a career coach and productivity expert..."
            return get_gemini_response(api_key, system_prompt, [goal])
        plan_goal_btn.click(plan_goal, [career_goal, api_key_box], goal_plan_output)

        def analyze_resume(resume_file, api_key):
            if not resume_file: return "Please upload a resume to analyze."
            system_prompt = "You are a world-class career coach specializing in resume feedback..."
            return get_gemini_response(api_key, system_prompt, [genai.upload_file(path=resume_file.name)])
        analyze_resume_btn.click(analyze_resume, inputs=[resume_file_input, api_key_box], outputs=resume_output)

        def analyze_gap(skills, role, api_key):
            if not skills or not role: return "Please fill in both your current skills and desired role."
            system_prompt = "You are a career development expert..."
            return get_gemini_response(api_key, system_prompt, [f"Current Skills: {skills}\nDesired Role: {role}"])
        analyze_gap_btn.click(analyze_gap, inputs=[current_skills, desired_role, api_key_box], outputs=skill_gap_output)

        def run_quiz(q1, q2, q3, api_key):
            if not q1 or not q2 or not q3: return "Please answer all questions."
            dominant_trait = "analytical"
            quiz_prompt = f"A user's dominant personality trait is '{dominant_trait}'. Suggest 3-4 suitable career paths."
            return get_gemini_response(api_key, quiz_prompt)
        quiz_submit_btn.click(run_quiz, inputs=[q1, q2, q3, api_key_box], outputs=quiz_output)

    return demo

if __name__ == "__main__":
    chatbot_app = build_interface()
    chatbot_app.queue()
    chatbot_app.launch(share=True, debug=True)