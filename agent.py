import os
from openai import OpenAI
from dotenv import load_dotenv
from memory import get_customer_memory, save_customer_memory, get_or_create_customer
from datetime import datetime

load_dotenv()
# load_dotenv() reads your .env file and loads DASHSCOPE_API_KEY
# into the environment so os.getenv() can find it
# without this line, your API key would be invisible to the code

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)
# This is the same Qwen client from your test.py
# but now it reads the key from .env instead of being hardcoded
# this is the safe, production-ready way to handle API keys

def process_inquiry(email: str, name: str, message: str):
    # This is Beeleva's main function
    # It takes a customer's email, name, and message
    # and returns an intelligent response
    
    # STEP 1: Make sure the customer exists in our database
    get_or_create_customer(email=email, name=name)
    
    # STEP 2: Check if we have memory of this customer
    memory = get_customer_memory(email)
    
    if memory:
        memory_context = f"Previous interaction summary: {memory['summary']}"
        # If we know this customer, we tell Qwen what we already know
        # This is what makes Beeleva feel personal and intelligent
    else:
        memory_context = "This is a new customer with no previous interactions."
        # First time customer — no context yet
    
    # STEP 3: Build the prompt for Qwen
    system_prompt = f"""
You are Beeleva, a professional AI business operator for a small business.
Your job is to handle customer inquiries intelligently and professionally.

About this customer:
- Email: {email}
- Name: {name}
{memory_context}

Your response should:
1. Be warm, professional, and helpful
2. Directly address what the customer is asking
3. If they want a quote, provide a reasonable estimate with clear breakdown
4. If they have a complaint, acknowledge it and offer a solution
5. Always end with a clear next step for the customer

Keep responses concise — maximum 150 words.
"""
    # The system_prompt is like giving Beeleva its personality and instructions
    # before it reads the customer message
    # Notice how we inject the memory_context here —
    # that's how past knowledge flows into the current response

    # STEP 4: Send to Qwen and get a response
    response = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )
    
    ai_response = response.choices[0].message.content
    # This extracts just the text from Qwen's response object
    
    # STEP 5: Update memory with a summary of this interaction
    new_summary = f"Last contacted: {datetime.now().strftime('%Y-%m-%d')}. Customer message: '{message[:100]}'. Beeleva responded with quote/support."
    save_customer_memory(email, new_summary)
    # We save a summary (not the full conversation) to keep memory lean
    # [:100] means we only save the first 100 characters of their message
    
    return ai_response

if __name__ == "__main__":
    # This block lets us test agent.py directly
    # It only runs when you do "python agent.py" — not when imported
    test_response = process_inquiry(
        email="ada@gmail.com",
        name="Ada",
        message="Hi, I need a quote for social media management for my boutique. I have Instagram and Facebook."
    )
    print("\n--- BEELEVA RESPONSE ---")
    print(test_response)