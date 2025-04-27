from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
from typing import List, Optional, Dict, Any, AsyncGenerator

# Load environmental variables
env_vars = dotenv_values(".env")
GroqAPIkey = env_vars.get("GroqAPIkey")

# CSS classes for parsing HTML content
CLASSES = [
    "zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", 
    "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc",
    "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfKe", "VQF4g",
    "qv3Wpe", "kno-rdesc", "SPZz6b"
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client
client = Groq(api_key=GroqAPIkey) if GroqAPIkey else None

PROFESSIONAL_RESPONSES = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need - don't hesitate to ask."
]

messages: List[Dict[str, str]] = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.getenv('Username', 'AI Assistant')}. You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

def GoogleSearch(topic: str) -> bool:
    """Perform a Google search using pywhatkit."""
    try:
        search(topic)
        return True
    except Exception as e:
        print(f"[red]Error in GoogleSearch: {e}[/red]")
        return False

def Content(topic: str) -> bool:
    """Generate content using AI and save to a file."""
    def OpenNotepad(file_path: str) -> bool:
        """Open a file in Notepad."""
        try:
            subprocess.Popen(['notepad.exe', file_path])
            return True
        except Exception as e:
            print(f"[red]Error opening Notepad: {e}[/red]")
            return False

    def ContentWriterAI(prompt: str) -> str:
        """Generate content using Groq API."""
        if not client:
            raise ValueError("Groq client not initialized")
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            completion = client.chat.completions.create(
                model="Llama3-8b-8192",
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )
            
            answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content
            
            answer = answer.replace("</s>", "")
            messages.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            print(f"[red]Error in ContentWriterAI: {e}[/red]")
            raise

    try:
        clean_topic = topic.replace("Content", "").strip()
        content = ContentWriterAI(clean_topic)
        
        # Ensure Data directory exists
        os.makedirs("Data", exist_ok=True)
        
        filename = f"Data/{clean_topic.lower().replace(' ', '_')}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        
        OpenNotepad(filename)
        return True
    except Exception as e:
        print(f"[red]Error in Content: {e}[/red]")
        return False

def YouTubeSearch(topic: str) -> bool:
    """Search for a topic on YouTube."""
    try:
        url = f"https://www.youtube.com/results?search_query={topic}"
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"[red]Error in YouTubeSearch: {e}[/red]")
        return False

def PlayYoutube(query: str) -> bool:
    """Play a YouTube video."""
    try:
        playonyt(query)
        return True
    except Exception as e:
        print(f"[red]Error in PlayYoutube: {e}[/red]")
        return False

def OpenApp(app: str, sess: requests.Session = requests.Session()) -> bool:
    """Open an application or relevant webpage."""
    def extract_links(html: Optional[str]) -> List[str]:
        """Extract links from HTML content."""
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links if link.get('href')]
        except Exception as e:
            print(f"[yellow]Warning in extract_links: {e}[/yellow]")
            return []

    def search_google(query: str) -> Optional[str]:
        """Perform a Google search and return HTML."""
        try:
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": USER_AGENT}
            response = sess.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[yellow]Warning in search_google: {e}[/yellow]")
            return None

    try:
        # First try opening as an application
        appopen(app, match_closest=True, output=False, throw_error=True)
        return True
    except Exception as app_error:
        print(f"[yellow]App not found, trying web search: {app_error}[/yellow]")
        
        try:
            html = search_google(app)
            if not html:
                return False
                
            links = extract_links(html)
            if not links:
                return False
                
            # Filter and validate links
            valid_links = [link for link in links if link.startswith(('http://', 'https://'))]
            if not valid_links:
                return False
                
            webopen(valid_links[0])
            return True
        except Exception as web_error:
            print(f"[red]Error in OpenApp web search: {web_error}[/red]")
            return False

def CloseApp(app: str) -> bool:
    """Close an application."""
    if "chrome" in app.lower():
        return False
        
    try:
        close(app, match_closest=True, output=False, throw_error=True)
        return True
    except Exception as e:
        print(f"[yellow]Warning in CloseApp: {e}[/yellow]")
        return False

def System(command: str) -> bool:
    """Execute system commands."""
    command = command.lower().strip()
    
    key_commands = {
        "mute": "volume mute",
        "unmute": "volume mute",
        "volume up": "volume up",
        "volume down": "volume down"
    }
    
    if command in key_commands:
        try:
            keyboard.press_and_release(key_commands[command])
            return True
        except Exception as e:
            print(f"[red]Error in System command: {e}[/red]")
            return False
    else:
        print(f"[yellow]Unknown system command: {command}[/yellow]")
        return False

async def TranslateAndExecute(commands: List[str]) -> AsyncGenerator[Any, None]:
    """Translate and execute commands asynchronously."""
    funcs = []
    
    for command in commands:
        command = command.strip()
        if not command:
            continue
            
        try:
            if command.startswith("open "):
                if "open it" in command or "open file" in command:
                    continue
                app_name = command.removeprefix("open").strip()
                funcs.append(asyncio.to_thread(OpenApp, app_name))
                
            elif command.startswith("close "):
                app_name = command.removeprefix("close").strip()
                funcs.append(asyncio.to_thread(CloseApp, app_name))
                
            elif command.startswith("play "):
                query = command.removeprefix("play").strip()
                funcs.append(asyncio.to_thread(PlayYoutube, query))
                
            elif command.startswith("content "):
                topic = command.removeprefix("content").strip()
                funcs.append(asyncio.to_thread(Content, topic))
                
            elif command.startswith("google search "):
                query = command.removeprefix("google search").strip()
                funcs.append(asyncio.to_thread(GoogleSearch, query))
                
            elif command.startswith("system "):
                sys_command = command.removeprefix("system").strip()
                funcs.append(asyncio.to_thread(System, sys_command))
                
            else:
                print(f"[yellow]No handler for command: {command}[/yellow]")
                
        except Exception as e:
            print(f"[red]Error processing command {command}: {e}[/red]")
    
    if funcs:
        try:
            results = await asyncio.gather(*funcs, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    print(f"[red]Command execution error: {result}[/red]")
                else:
                    yield result
        except Exception as e:
            print(f"[red]Error in command execution: {e}[/red]")

async def Automation(commands: List[str]) -> bool:
    """Automate command execution."""
    try:
        async for _ in TranslateAndExecute(commands):
            pass
        return True
    except Exception as e:
        print(f"[red]Error in Automation: {e}[/red]")
        return False
    
    
    
    
    
    
    
    
# # Imort required Libraries
# from AppOpener import close , open as appopen # Import fuctions to open and close apps
# from webbrowser import open as webopen # Import webbrowser functionality
# from pywhatkit import search ,playonyt # Import functions from google search and youtube playback
# from dotenv import dotenv_values # Import dotenv to manage environmental variables
# from bs4 import BeautifulSoup # Import BeautifulSoup for parsing the HTML content
# from rich import print  # import rich for styled console output
# from groq import Groq # Import Groq for AI chat functionality
# import webbrowser # import webbrowser for opening url files
# import subprocess # import subprocess for interacting with subsystem
# import requests # import requests for making HTTP requests 
# import keyboard # import keyboard for keyboard related actions
# import asyncio # import asyncio for asynchronous programming
# import os # Import os for operating system functionalities


# # Load environmental variables from the .env files
# env_vars = dotenv_values(".env")
# GroqAPIkey= env_vars.get("GroqAPIkey")  # Retrieve the Grpq API Key


# # Define css classes for parsing specific elements in HTML content 
# classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", 
#            "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table",
#            "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# #Define a user-agent for making web requests.

# useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# #Initialize the Groq client with the API key.

# client = Groq(api_key=GroqAPIkey)

# # Predefined professional responses for user interactions.

# professional_responses =[
# "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with."
# "I'm at your service for any additional questions or support you may need-don't hesitate to ask."]


# # List to store the chatbot messages
# messages = []

# # system message to provide context to the chatbot


# SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like  letters , codes, applications , essays , notes , songs , poems etc."}]

# #Function to perform a Google search.

# def GoogleSearch(Topic):

#     search(Topic) # Use pywhatkit's search function to perform a Google search.

#     return True # Indicate success.

# # Function to generate content using AI and save it to a file.

# def Content(Topic):

# #Nested function to open a file in Notepad.

#     def OpenNotepad(File):

#         default_text_editor = 'notepad.exe' # Default text editor

#         subprocess.Popen([default_text_editor, File]) # Open the file in Notepad.

# # Nested function to generate content using the AI chatbot.

#     def ContentWriterAI(prompt):

#         messages.append({"role": "user", "content": f"{prompt}"}) # Add the user's prompt to messages.
        
#         completion = client.chat.completions.create(
       
#         # model="mixtral-8-7b-32768",
#         model="Llama3-8b-8192",
#         # Specify the AI model.
       

#         messages=SystemChatBot + messages,# Include system instructions and chat history.
#         max_tokens=2048,# Limit the maximum tokens in the response.
#         temperature=0.7, #Adjust response randomness. top_p=1, Use nucleus sampling for response diversity.
#         stream=True, #Enable streaming response.
#         stop=None #Allow the model to determine stopping conditions.
#         )
        
#         Answer = "" # initialize an empty string for the response
        
#         # Process streamed response chunks
        
#         for chunk in completion:

#             if chunk.choices[0].delta.content: #Check for content in the current chunk.

#                Answer += chunk.choices[0].delta.content # Append the content to the answer.

#         Answer = Answer.replace("</s>", "") # Remove unwanted tokens from the response.

#         messages.append({"role": "assistant", "content": Answer}) # Add the AI's response to messages.

#         return Answer

#     Topic: str = Topic.replace("Content", "") # Remove "Content from the topic. 
#     ContentByAI = ContentWriterAI(Topic)# Generate content using AI.

# #Save the generated content to a text file.

#     with open(rf"Data\{Topic.lower().replace('','')}.txt", "w", encoding="utf-8") as file:

#          file.write(ContentByAI) # Write the content to the file
#          file.close()
#     OpenNotepad(rf"Data\{Topic.lower().replace('','')}.txt") # Open the file in Notepad.

#     return True #Indicate success.

# # Function to search for a topic on YouTube.

# def YouTubeSearch(Topic):
#     Url4Search = f"https://www.youtube.com/results?search_query={Topic}" # Construct the YouTube search URL.
#     webbrowser.open(Url4Search) # Open the search URL in a web browser.
#     return True  #Indicate success.


# #Function to play a video on YouTube.

# def PlayYoutube(query):
#     playonyt(query)# Use pywhatkit's playonyt function to play the video.
#     return True    # Indicate success.

# # Function to open an application or a relevant webpage.

# def OpenApp(app, sess=requests.session()):

#     try:
#         appopen(app, match_closest=True, output=True, throw_error=True) # Attempt to open the app.
#         return True #Indicate success.

#     except:
#         # Nested function to extract links from HTML content.
#         def extract_links(html):

#             if html is None:
#                return []

#             soup = BeautifulSoup(html, 'html.parser') #Parse the HTML content. 
#             links= soup.find_all('a', {'jsname': 'UWckNb'}) #Find relevant links.
#             return [link.get('href') for link in links] # Return the links.

#         #Nested function to perform a Google search and retrieve HTML.

#         def search_google(query):
#             url=f"https://www.google.com/search?q={query}"  # Construct the Google search URL.
#             headers={"User-Agent": useragent}# Use the predefined user-agent.
#             response =sess.get(url, headers=headers) # Perform the GET request.

#             if response.status_code == 200:
#                 return response.text # Return the HTNL content
#             else:
#                 print("Failed to Recieve search Results.") # Print an error message
#             return None
        
#         html = search_google(app) # perform the google sesrch
#         if html:
#             link = extract_links(html)[0]  # Extract the first link from the search results
#             webopen(link)    # Open the link in browser
#         return True

# def CloseApp(app):
#     if "chrome" in app:
#         pass # Skip if the app is chrome
#     else:
#         try:
#             close(app,match_closest=True,output=True,throw_error=type) # attempt to close the app
#             return True # Indicate success
#         except:
#             return False # Indicate failure
        
# # Function to execute system level command
# def System(command):
    
#     # nested function to mute the system volume 
#     def mute():
#         keyboard.press_and_release("volume mute") # Simulate the mute key press
        
#     def unmute():
#         keyboard.press_and_release("volume mute") # Simulate the unmute key press
    
#     # Nested function to increase system volume
#     def volume_up():
#         keyboard.press_and_release("volume up") # Simulate the volume up key press
        
#     def volume_down():
#         keyboard.press_and_release("volume down")  # Simulate the volume down key press
        
#     # Execute the appropriate command
#     if command == "mute":
#         mute()
#     elif command == "unmute":
#         unmute()
#     elif command == "volume up":
#         volume_up()
#     elif command == "volume down":
#         volume_down()
        

#     return True # Indicate sucess

# # Asynchronous  function to translate and execute user commands
# async def TranslateAndExecute(commands: list[str]):
    
#     funcs = [] # List to store Asynchronous tasks
    
#     for command in commands:
#         if command.startswith("open "): # Handle "open" commands
#             if "open it" in command: # ignore "open it" commands
#                 pass 
#             if "open file" == command: #ignore "open file" commands
#                 pass
#             else:
#                 fun = asyncio.to_thread(OpenApp,command.removeprefix("open")) # schedule app opening
#                 funcs.append(fun)
#         elif command.startswith("general ")  : # Placeholder for general command
#             pass    
#         elif command.startswith("realtime ")  : # Placeholder for realtime command  
#             pass
#         elif command.startswith("close ")  : # Handle "close" commands
#             fun = asyncio.to_thread(CloseApp,command.removeprefix("close ")) # schedule app closing
#             funcs.append(fun)
#         elif command.startswith("play ")  : # Handle "play" commands
#             fun = asyncio.to_thread(PlayYoutube,command.removeprefix("play ")) # schedule app closing
#             funcs.append(fun)
#         elif command.startswith("content ")  : # Handle "content" commands
#             fun = asyncio.to_thread(Content,command.removeprefix("content ")) # schedule content creation
#             funcs.append(fun)
#         elif command.startswith("google search ")  : # Handle googlesearch  commands
#             fun = asyncio.to_thread(GoogleSearch,command.removeprefix("google search ")) # schedule googlesearch commands
#             funcs.append(fun)
#         elif command.startswith("system ")  : # Handle system  commands
#             fun = asyncio.to_thread(YouTubeSearch,command.removeprefix("system ")) # schedule system commands
#             funcs.append(fun)
#         else:
#             print(f"No function found. For {command}") # Print ab error for unrecognized command
            
#     results = await asyncio.gather(*funcs) # Execute all tasks concurrently
    
#     for result in results: # Process the results
#         if isinstance(result,str):
#             yield result
#         else:
#             yield result
            
# # Asynchronous function to automate command execution
# async def Automation(commands: list[str]):
#     async for result in TranslateAndExecute(commands): # Translate and execute the commands
#         pass
#     return True # Indicate sucess
# if __name__=="__main__":
#     asyncio.run(Automation(["play tu jaane na song"]))
