from chains.chatbot import chat_gen

def main():
    print("Airline Customer Service Bot (type 'quit' to exit)")
    history = [{"role": "assistant", "content": "Hello! I'm your SkyFlow agent! How can I help you?"}]
    print(f"\n[ Agent ]: {history[0]['content']}")

    while True:
        message = input("\n[ You ]: ")
        if message.strip().lower() in {"quit", "exit"}:
            break
        history.append({"role": "user", "content": message})

        print("\n[ Agent ]: ", end="")
        reply = ""
        for token in chat_gen(message, history, return_buffer=False):
            print(token, end="", flush=True)
            reply += token
        print()
        history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()