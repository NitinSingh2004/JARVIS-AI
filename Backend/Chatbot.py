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


# Initialize the Graq client using the provided API key
client = Groq(api_key=GroqAPIkey)

#Initialize the empty list to store the chat message
messages=[]

#Define a system message that provides context to the AI chatbot about its role and behaviour
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# A list of system instructions for the chatbot
SystemChatBot=[
    {"role":"system","content":System}
]

# Attempt to load the chat log from a JSON file
try:
    with open(r"Data\ChatLog.json","r") as f:
        messages = load(f)       # load existing messages from the chat Log
except FileNotFoundError: 
    # if file does not exist ,create an empty JSON file to store chat logs
    with open(r"Data\ChatLog.json","w")  as f:
        dump([],f)    
        
# Function to get real time date and information 
def RealtimeInformation():
    current_date_time = datetime.datetime.now()  # get current date and time
    day = current_date_time.strftime("%A")  # Day of the week
    date =  current_date_time.strftime("%d") # Day of the month
    month =  current_date_time.strftime("%B") # Full month name
    year =  current_date_time.strftime("%Y")  #Year
    hour =  current_date_time.strftime("%H")  # Hour in 24 hour format
    minute =  current_date_time.strftime("%M") # Minute
    second =  current_date_time.strftime("%S") # second
    
    # Format the information into a string
    data = f"Please use this real_time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours : {minute} minutes : {second} second.\n"
    return data

# Function to modify the chatbots response for better formatting
def AnswerModifier(Answer):
    lines = Answer.split('\n')   #split the response into lines
    non_empty_line = [line for line in lines if line.strip()]  # remove empty lines
    modified_answer = '\n'.join( non_empty_line)  # Join the cleaned lines back together
    return modified_answer 

# main chatbot function to handle user quereies
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    try:
        # LOad the existing chat log from the JSON file
        with open(r"Data\ChatLog.json","r") as f:
            messages = load(f)
        # Append the user's query to the message list.
        messages.append({"role":"user","content":f"{Query}"})
        
        # Make a request to the Groq API for a reponse
        completion = client.chat. completions.create(
          model = "llama3-70b-8192" ,  # specify the API model
          messages=SystemChatBot + [{"role":"system","content":RealtimeInformation()}] + messages,
          max_tokens = 1024,  # limit the maximun token in the response
          temperature= 0.7, # adjust response randomness (higher means more random)
          top_p=1, # use neucleus sampling to control diversity
          stream=True  ,#Enable streaming response
          stop = None # Allow the model to determine when to stop
          )
        Answer ="" # Initialize an empty string to store the AI's response
          
        # Process the streamed response chunks
        for chunk in completion:
            if chunk.choices[0].delta.content:  # check if there's content in the current chunk
                Answer+= chunk.choices[0].delta.content # Append the content to the answer
        Answer= Answer.replace("</s>","") # clean up any unwanted tokens from the response
        
        # Append  the chatbot's response to the message list
        messages.append({"role":"assistant","content": Answer})
        
        # Save the updated chat log to the JSON file
        with open(r"Data\ChatLog.json","w") as f:
            dump(messages,f,indent=4)
            
        # return the formatted response
        return AnswerModifier(Answer=Answer)
    except Exception as e:
        # Handle errors by printing  the exception and resetting the chat log
        print(f"Error:{e}")
        with open(r"Data\ChatLog.json","w") as f:
            dump([],f,indent=4)
        return ChatBot(Query)  # REtry the query after resetting the log


# main program entry point
if __name__=="__main__" :
    while True:
        user_input= input("Enter Your Question:")    # Prompt the user for a question
        print(ChatBot(user_input))  #call the chatbot function and print its response
          



