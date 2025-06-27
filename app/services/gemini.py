import google.generativeai as genai 
import os 
import asyncio

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def stream_gemini(prompt: str):
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat()
    
    response = chat.send_message(prompt, stream=True)
    
    for chunk in response:
        text = chunk.text.strip()
        if text:
            yield text
            await asyncio.sleep(0.05)


        