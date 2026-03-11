import json
import os
import sys
import pywhatkit as kit

# Path to contacts JSON file
CONTACTS_FILE = os.path.join('Data', 'contacts.json')

def load_contacts():
    """Load contacts from JSON file."""
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_contacts(contacts):
    """Save contacts to JSON file."""
    os.makedirs('Data', exist_ok=True)
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=4)

def add_contact(name, phone):
    """Add a contact."""
    contacts = load_contacts()
    contacts[name] = phone
    save_contacts(contacts)
    print(f"Contact '{name}' added with phone {phone}.")

def send_message(recipient, message):
    """Send a message to a contact or phone number."""
    contacts = load_contacts()
    if recipient in contacts:
        phone = contacts[recipient]
    elif recipient.startswith('+'):
        phone = recipient
    else:
        print("Contact not found. Use full phone number with country code.")
        return
    try:
        kit.sendwhatmsg_instantly(phone, message, wait_time=10)
        print(f"Message sent to {phone}: {message}")
    except Exception as e:
        print(f"Error sending message: {e}")

def list_contacts():
    """List all contacts."""
    contacts = load_contacts()
    if contacts:
        print("Contacts:")
        for name, phone in contacts.items():
            print(f"{name}: {phone}")
    else:
        print("No contacts found.")

def print_help():
    print("Commands:")
    print("  add <name> <phone>    - Add a contact")
    print("  send <recipient> <message> - Send a message")
    print("  list                  - List all contacts")
    print("  help                  - Show this help")
    print("  exit                  - Exit the program")

if __name__ == "__main__":
    print("WhatsApp Messaging Tool")
    print_help()
    while True:
        try:
            user_input = input("\n> ").strip()
            if not user_input:
                continue
            parts = user_input.split()
            command = parts[0].lower()

            if command == 'add':
                if len(parts) != 3:
                    print("Usage: add <name> <phone>")
                    continue
                name = parts[1]
                phone = parts[2]
                add_contact(name, phone)
            elif command == 'send':
                if len(parts) < 3:
                    print("Usage: send <recipient> <message>")
                    continue
                recipient = parts[1]
                message = ' '.join(parts[2:])
                send_message(recipient, message)
            elif command == 'list':
                list_contacts()
            elif command == 'help':
                print_help()
            elif command == 'exit':
                print("Exiting...")
                break
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
