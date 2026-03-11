import cohere
from rich import print
from dotenv import dotenv_values

evn_vars = dotenv_values(".env")

CohereAPIkey = evn_vars.get("CohereAPIKey")

co=cohere.Client(api_key=CohereAPIkey)

funcs = [
    "exit","general","realtime","open","close","play",
    "generate image","system","content","google search",
    "youtube search","reminder","3d cad","web cam","tell reminder"
]

messages =[]

preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on but if it require up-to-date information to answer. Respond with 'realtime (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', if the query is 'tell me lyrics of kabhi kabhi aditi' respond with 'realtime full lyrics of kabhi kabhi aditi', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook','open brave', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with play (song name) when the query names one specific song or artist, e.g. “play afsanay by ys”, “play let her go”, “play arijit singh”, "play kk". If the query names multiple songs or artists, respond with play 1st song name, play 2nd song name, andso on.
-> Respond with play fav_songs when no song or artist is given, e.g. “play music”, “gana chalao”.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down, volume 10, brigthnes 50, change screen, etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.For change screen or toggle screen 
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
->Respond with '3d cad(prompt)' if a query is asking to make a 3d model or a cad design.
->Respond with 'web cam(question)' if a query is asking to use web cam to see.Or if user is asking to review their outfit or describe their bueaty.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

ChatHistory = [
{"role": "User", "message": "how are you?"},
{"role": "Chatbot", "message": "general how are you?"},
{"role": "User", "message": "do you like pizza?"},
{"role": "Chatbot", "message": "general do you like pizza?"},
{"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
{"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
{"role": "User", "message": "open chrome and firefox"},
{"role": "Chatbot", "message": "open chrome, open firefox"},
{"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
{"role": "Chatbot", "message": "general what is today's date, reminder i have a dancing performance"},
{"role": "User", "message": "chat with me"},
{"role": "Chatbot", "message": "general chat with me"},
]


def FirstLayerDMM(prompt: str = "test", last_queries: list = [], depth: int = 0):
# Add the user's query to the messages list.
    messages.append({"role": "user", "content": f"{prompt}"})

    # Modify preamble to include last queries for context
    context_preamble = preamble
    if last_queries:
        context_str = "Here are the last few user queries for context to help classify the current query: " + ", ".join(last_queries)
        context_preamble += "\n" + context_str

    # Create a streaming chat session with the Cohere model.
    stream = co.chat_stream(
        model='command-r-plus-08-2024', # Specify the Conere model to use.
        message=prompt, # Pass the user's quecy.
        temperature=0.7, # Set the creativitr Level of the model.
        chat_history=ChatHistory, # Provide the crreefined chat histo
        prompt_truncation='OFF', # Ensure the drompriis cot truncated
        connectors=[], # No additionat connectars are used.
        preamble=context_preamble
    )

    response = ""

    # Iretate over events in the stream apd cactore text generatied eveote.
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text # Aobend gederated text to the resoonse.

    # Remove pewline characters and split responses into individual tasks.
    response = response.replace("\n", "")
    response = response.split(",")

    # Strip leading and trailing whitespaces from eacn task.
    response = [i.strip() for i in response]

    # Ipitialize an empty list to filter valid tasks.
    temp = []

    # Eiltet the tasks based on recognized fonctioo keywords.
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
    # Add valid rasks to the filtered list.

    # Update the response with the filtered list of tasks.
    response = temp

    if "(query)" in response and depth < 3: # Limit recursion depth
        newresponse = FirstLayerDMM(prompt=prompt, depth=depth+1)
        return newresponse # Return the clarified respogse:
    else:
        return response #
    
if __name__ == "__main__":
    while True:
        print(FirstLayerDMM(input(">>>>")))