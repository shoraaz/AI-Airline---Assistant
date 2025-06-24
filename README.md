# ✈️ FlightAI - An AI Airline Assistant

This project demonstrates how to build a multi-modal AI assistant for an airline using OpenAI's models (GPT-4o mini, DALL-E 3, TTS) and Gradio for the user interface. The assistant, "FlightAI," can answer customer queries, use tools to fetch information like ticket prices, generate images of destinations, and respond with voice.

## Features

- **Conversational AI**: Engages in natural conversation with users.
- **Tool Usage**: Uses a custom function (`get_ticket_price`) to retrieve flight prices for specific destinations.
- **Image Generation**: Generates and displays vibrant, pop-art style images of travel destinations using DALL-E 3.
- **Text-to-Speech**: Converts the assistant's text responses into audible speech.
- **Web Interface**: A clean and user-friendly chat interface built with Gradio.


## 🛠️ Setup and Installation

Follow these steps to get the project running on your local machine.

### Prerequisites

- Python 3.8 or higher
- An [OpenAI API key](https://platform.openai.com/api-keys)
- **FFmpeg**: This is a crucial dependency for handling audio.
  - **macOS (using Homebrew)**:
    ```bash
    /bin/bash -c "$(curl -fsSL [https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh))"
    brew install ffmpeg
    ```
  - **Windows**:
    1. Download FFmpeg from the [official website](https://ffmpeg.org/download.html).
    2. Extract the files to a location like `C:\ffmpeg`.
    3. Add the `bin` folder (e.g., `C:\ffmpeg\bin`) to your system's PATH environment variable.
    4. Verify the installation by opening a new terminal and running `ffmpeg -version`.

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/flight-ai-assistant.git](https://github.com/your-username/flight-ai-assistant.git)
    cd flight-ai-assistant
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    Create a file named `.env` in the root directory of the project and add your OpenAI API key:
    ```
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

## 🚀 Running the Application

Once the setup is complete, you can start the application with the following command:

```bash
python app.py
```

This will launch the Gradio web interface and automatically open it in your default web browser. You can now start chatting with your FlightAI assistant!

## 🔧 How It Works

1.  **Gradio Interface**: The `app.py` script uses the Gradio library to create a `gr.Blocks` layout, which includes a chatbot window, an image display area, and a text input field.
2.  **User Input**: When a user sends a message, it's appended to the chat history.
3.  **OpenAI API Call**: The `chat_logic` function sends the entire conversation history, along with the system prompt and tool definitions, to the OpenAI Chat Completions API.
4.  **Tool Call Detection**: The model (GPT-4o mini) decides if it needs to use a tool to answer the query (e.g., if the user asks for a price).
5.  **Function Execution**: If the model signals a tool call, the application executes the corresponding Python function (`get_ticket_price`).
6.  **Image and Audio Generation**: After getting the price, the app calls the `artist` function to generate an image with DALL-E 3. It then formulates a final text response.
7.  **Final Response**: The text response is sent back to the model one last time for a natural language summary. This final text is then converted to speech using the `talker` function.
8.  **UI Update**: The chatbot history and the generated image are updated in the Gradio interface.

## 📁 Project Structure

```
.
├── .env                  # Stores environment variables (API key)
├── README.md             # This file
├── main.py                # Main application script with all logic
└── requirements.txt      # Python dependencies
```
