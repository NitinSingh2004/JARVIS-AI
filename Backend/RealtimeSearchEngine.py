from googlesearch import search
from groq import Groq               #importing the Groq library to use its API
from json import load, dump         #import functions to read and write JSON files
import datetime                     #importing date and time module for real time date and time information 
from dotenv import dotenv_values    #importing dotenv_values to read environment variables from a .env file



# load environment variables from the .env files
env_vars=dotenv_values(".env")


# Retrieve specific environment variables for username,assistant name,and API key
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIkey = env_vars.get("GroqAPIkey")


# Initialize the Graq client with the provided API key
client = Groq(api_key=GroqAPIkey)

# Define the system instructions for the chatbot
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Try to load the chat log from a JSON file , or create an empty one if it does not exist
try:
    with open(r"Data\ChatLog.json","r") as f:
        messages = load(f)       # load existing messages from the chat Log
except : 
    # if file does not exist ,create an empty JSON file to store chat logs
    with open(r"Data\ChatLog.json","w")  as f:
        dump([],f)  
# Function to perform a google search and format the results

def GoogleSearch(query):
    results = list(search(query,advanced=True,num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    
    for i in results:
        Answer += f"Title : {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer 
 # Predefined chatbot conversation system message and an initial user message
SystemChatBot=[
    {"role":"system","content":System},
    {"role":"user","content":"Hi"},
    {"role":"assistant","content":"Hello, How can I help you?"}
     
 ]
# Function for real time information like current date and time
def Information():
    data=""
    current_date_time = datetime.datetime.now()  # get current date and time
    day = current_date_time.strftime("%A")  # Day of the week
    date =  current_date_time.strftime("%d") # Day of the month
    month =  current_date_time.strftime("%B") # Full month name
    year =  current_date_time.strftime("%Y")  #Year
    hour =  current_date_time.strftime("%H")  # Hour in 24 hour format
    minute =  current_date_time.strftime("%M") # Minute
    second =  current_date_time.strftime("%S") # second
    
    # Format the information into a string
    data = f"Please use this real_time information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date :{date}\n"
    data +=  f"Month: {month}\n"
    data +=  f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes ,{second} second.\n"
    return data

# Function to handle real-time search and response generation

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages
    
    # Load the chat log from the JSON file
    
    with open(r"Data\ChatLog.json","r") as f:
        messages.append({"role":"user","content":f"{prompt}"})
        
        # add google search results to the system chatbot messages
        SystemChatBot.append({"role":"system","content":GoogleSearch(prompt)})
        
        # Generate a response using the groq client
        completion = client.chat.completions.create(
          model = "llama3-70b-8192" ,  # specify the API model
          messages=SystemChatBot + [{"role":"system","content":Information()}] + messages,
          max_tokens = 1024,  # limit the maximun token in the response
          temperature= 0.7, # adjust response randomness (higher means more random)
          top_p=1, # use neucleus sampling to control diversity
          stream=True  ,#Enable streaming response
          stop = None # Allow the model to determine when to stop
          )
        Answer ="" # Initialize an empty string to store the AI's response
        
        
        # Cocatenate response chunks from the streaming output
        for chunk in completion:
            if chunk.choices[0].delta.content:  # check if there's content in the current chunk
                Answer+= chunk.choices[0].delta.content # Append the content to the answer
                
                
         # For clean up response
        Answer = Answer.strip().replace("</s>","")
        
        # Append  the chatbot's response to the message list
        messages.append({"role":"assistant","content": Answer})
        
        # Save the updated chat log back to the JSON file
        with open(r"Data\ChatLog.json","w") as f:
            dump(messages,f,indent=4)
            
        # remove the most recent system message from the chatbot conversation
        SystemChatBot.pop()
        return AnswerModifier(Answer=Answer)
    
# Main entry point of the program for interactive querying
if __name__=="__main__" :
    while True:
        prompt = input("Enter your Query:")
        print(RealtimeSearchEngine(prompt))
          
        



