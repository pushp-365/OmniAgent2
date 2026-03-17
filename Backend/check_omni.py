from Backend.ask_model import askOmni

system_prompt = """You are a helpful AI assistant.
Always be respectful."""

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye")
        break

    response = askOmni(user_input, system_prompt)
    print("Omni:", response)