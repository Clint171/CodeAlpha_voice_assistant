import os
import readline
import sys
import dotenv
from llamaapi import LlamaAPI
from subprocess import Popen, PIPE
import speech_recognition as sr

# Load environment variables from .env file
dotenv.load_dotenv()

# Get API token from environment variable
api_token = os.environ.get("API_TOKEN")

# Initialize LlamaAI client
llama_api = LlamaAPI(api_token)

# Initial message to user
messages = [
    {
        "role": "system",
        "content": (
            "You are a translator between natural language and terminal commands. "
            "Your goal is to respond only with relevant commands."
        ),
    }
]

def voice_to_text():
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    # Set up the microphone
    with sr.Microphone() as source:
        print("Please speak now...")
        # Adjust the recognizer sensitivity to ambient noise
        recognizer.adjust_for_ambient_noise(source)
        # Capture the audio
        audio = recognizer.listen(source)
        
        try:
            # Recognize the speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            # Speech was unintelligible
            print("Google Web Speech API could not understand the audio. Please try again")
            return None
        except sr.RequestError as e:
            # API was unreachable or unresponsive
            print(f"Could not request results from Google Web Speech API. Please ty again")
            return None

def handle_prompt(query):
    # If user wants to quit, exit the program
    if query == "quit" or query == "exit":
        sys.exit()
    
    # Add additional information to query.
    # This is a hack to make the AI more accurate.
    query = query + ", I am on platform " + sys.platform + " and my current directory is " + os.getcwd() + ". The current process id is " + str(os.getpid()) + "."
    # Add user query to message list
    messages.append({"role": "user", "content": query})

    # Prepare API request
    api_request = {
        "messages": messages,
        "temperature": 0.9,
        "stream": False,
    }

    # Send request to LlamaAI and process response
    try:
        response = llama_api.run(api_request)
        commands = response.json()["choices"][0]["message"]["content"].split("\n")
        print(commands)
        # Execute each command and stop if one fails
        for command in commands:
            # check if contains "```" or '' and skip
            if(command.find("```") != -1 or command.find("''") != -1):
                continue
            proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()

            if proc.returncode != 0:
                print(f"Error: {stderr.decode('utf-8')}")
                print("Retrying...")
                # remove last message
                messages.pop()
                # send error message to llama
                handle_prompt(query)
                break
            else:
                print(f"Output:\n{stdout.decode('utf-8')}")

        # If all commands succeed, find the next command
        else:
            messages.pop()
            find_terminal_command()
    except Exception as error:
        print(f"An error occurred: {error}")
        print(response.json())
        find_terminal_command()



def find_terminal_command():
    # Prompt user for input
    query = voice_to_text()
    if query:
        handle_prompt(query)
    else :
        find_terminal_command()

def execute(command):
    print(command)
    proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout , stderr = proc.communicate()

if __name__ == "__main__":
    find_terminal_command()