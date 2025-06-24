
import os
import json
import base64
from io import BytesIO
from PIL import Image
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import simpleaudio as sa



load_dotenv(override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')

if openai_api_key:
    print(f"OpenAI API Key loaded and begins with {openai_api_key[:8]}")
else:
    print("OpenAI API Key not set. Please create a .env file and add your key.")

MODEL = "gpt-4o-mini"
client = OpenAI()

# System Message
system_message = """You are a helpful assistant for an Airline called FlightAI. 
 Give short, courteous answers, no more than 1 sentence. 
 Always be accurate. If you don't know the answer, say so."""

# --- Tool Functions ---

# In-memory data for ticket prices
ticket_prices = {
    "london": "$799",
    "paris": "$899",
    "tokyo": "$1400",
    "berlin": "$499",
    "new york": "$950"
}

def get_ticket_price(destination_city):
    """
    Retrieves the ticket price for a given destination city.
    """
    print(f"Tool 'get_ticket_price' called for {destination_city}")
    city = destination_city.lower()
    return ticket_prices.get(city, "Unknown")

def artist(city):
    """
    Generates an image for the given city using DALL-E-3.
    """
    print(f"Tool 'artist' called to generate image for {city}")
    try:
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=f"An image representing a vacation in {city}, showing tourist spots and everything unique about {city}, in a vibrant pop-art style.",
            size="1024x1024",
            n=1,
            response_format="b64_json",
        )
        image_base64 = image_response.data[0].b64_json
        image_data = base64.b64decode(image_base64)
        return Image.open(BytesIO(image_data))
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def talker(message):
    """
    Converts a text message to speech using OpenAI's TTS model and plays it.
    This version uses `simpleaudio` for broader compatibility.
    """
    print(f"Tool 'talker' called to speak: '{message}'")
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",  # Other voices: alloy, echo, fable, nova, shimmer
            input=message
        )
        audio_stream = BytesIO(response.content)
        audio = AudioSegment.from_file(audio_stream, format="mp3")

        # Use a temporary file to ensure compatibility
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            temp_file_name = temp_audio_file.name
            audio.export(temp_file_name, format="wav")

        # Load and play audio using simpleaudio
        wave_obj = sa.WaveObject.from_wave_file(temp_file_name)
        play_obj = wave_obj.play()
        play_obj.wait_done()

        # Clean up the temporary file
        os.remove(temp_file_name)

    except Exception as e:
        print(f"Error in audio generation or playback: {e}")
        print("Please ensure FFmpeg is installed and accessible in your system's PATH.")


# --- Tool Definition ---

price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to the destination city. Call this whenever you need to know the ticket price.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to.",
            },
        },
        "required": ["destination_city"],
    }
}

tools = [{"type": "function", "function": price_function}]


# --- Core Logic ---

def handle_tool_call(message):
    """
    Handles the logic for when the LLM decides to call a tool.
    """
    tool_call = message.tool_calls[0]
    tool_name = tool_call.function.name

    if tool_name == "get_ticket_price":
        arguments = json.loads(tool_call.function.arguments)
        city = arguments.get('destination_city')
        price = get_ticket_price(city)
        response_content = json.dumps({"destination_city": city, "price": price})

        response = {
            "role": "tool",
            "content": response_content,
            "tool_call_id": tool_call.id
        }
        return response, city
    return None, None


def chat_logic(history):
    """
    Main chat logic that interacts with the OpenAI API and orchestrates tool calls.
    """
    messages = [{"role": "system", "content": system_message}] + history
    image = None

    try:
        # First API call to get the initial response
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message

        # Check if the model wants to call a tool
        if response_message.tool_calls:
            tool_response, city = handle_tool_call(response_message)
            if tool_response and city:
                messages.append(response_message)  # Append the model's request to call the tool
                messages.append(tool_response)     # Append the tool's response

                # Generate an image for the city
                image = artist(city)

                # Second API call to get the final, user-facing response
                final_response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages
                )
                reply = final_response.choices[0].message.content
            else:
                reply = "Sorry, I encountered an error with my tools."
        else:
            reply = response_message.content

    except Exception as e:
        print(f"An error occurred in the chat logic: {e}")
        reply = "I'm sorry, I'm having trouble connecting to my services right now."

    history.append({"role": "assistant", "content": reply})

    # Generate and play audio for the final reply
    talker(reply)

    return history, image


# --- Gradio UI ---

with gr.Blocks(theme=gr.themes.Soft(), title="FlightAI Assistant") as ui:
    gr.Markdown("# ✈️ FlightAI Assistant")
    gr.Markdown("Ask me for flight prices, and I'll even show you a picture of the destination!")

    with gr.Row():
        chatbot = gr.Chatbot(
            value=[[None, "Hello! How can I help you today?"]],
            height=600,
            bubble_full_width=False,
            avatar_images=(None, "https://i.imgur.com/6p1I4sC.png") # User and Bot avatars
        )
        image_output = gr.Image(label="Destination Image", height=600, interactive=False)

    with gr.Row():
        entry = gr.Textbox(label="Your Message:", placeholder="e.g., How much is a ticket to Paris?", scale=4)
        submit_btn = gr.Button("Send", variant="primary", scale=1)

    with gr.Row():
        clear_btn = gr.ClearButton([chatbot, image_output, entry], value="Clear Conversation")

    def user_entry(message, history):
        """Adds the user's message to the chat history."""
        history.append({"role": "user", "content": message})
        return "", history

    # Connect UI events to the logic
    submit_btn.click(
        user_entry,
        inputs=[entry, chatbot],
        outputs=[entry, chatbot]
    ).then(
        chat_logic,
        inputs=[chatbot],
        outputs=[chatbot, image_output]
    )

    entry.submit(
        user_entry,
        inputs=[entry, chatbot],
        outputs=[entry, chatbot]
    ).then(
        chat_logic,
        inputs=[chatbot],
        outputs=[chatbot, image_output]
    )

if __name__ == "__main__":
    # Launch the Gradio app
    ui.launch(inbrowser=True)
