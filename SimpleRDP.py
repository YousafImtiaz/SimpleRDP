import os
import json
import subprocess
import signal
import sys
import termios
import tty

# File to store saved connections
SAVE_FILE = 'saved_connections.json'

# Load saved connections from the file
def load_connections():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save connections to the file
def save_connections(connections):
    with open(SAVE_FILE, 'w') as f:
        json.dump(connections, f, indent=4)

# Function to display the banner
def print_banner():
    print("\n\033[1;94mSimpleRDP\033[0m")  # Brighter Bold Blue Text with an extra newline

# List saved connections
def list_connections(connections):
    if not connections:
        print("No saved connections found.")
    else:
        print("\nSaved Connections:")
        for idx, (key, value) in enumerate(connections.items(), 1):
            domain_info = f", Domain: {value['domain']}" if value['domain'] else ""
            print(f"{idx}. IP: {key}, Username: {value['username']}, Password: {value['password']}{domain_info}")

# Delete a saved connection
def delete_connection(connections):
    if not connections:
        print("No saved connections found. \n")
        return

    list_connections(connections)
    try:
        idx = int(input("\nEnter the number of the connection to delete: "))
        ip = list(connections.keys())[idx - 1]
        del connections[ip]
        save_connections(connections)
        print(f"Connection to {ip} deleted.")
    except (ValueError, IndexError):
        print("Invalid selection. No changes made.")

# Add or update a saved connection
def add_connection(connections):
    print("\nAdding a new connection:")

    # Adjusting spaces to have the colon immediately after the text, no space before input
    ip = input("Enter IP address: ")
    username = input("Enter username: ")
    password = input("Enter password: ")
    domain = input("Enter domain (optional): ").strip()

    connections[ip] = {'username': username, 'password': password, 'domain': domain}
    save_connections(connections)
    print(f"Connection to {ip} saved.")

    connect_now = input("  Connect now? (y/n): ").strip().lower()
    if connect_now == 'y':
        run_xfreerdp(ip, username, password, domain)

# Run xfreerdp with selected details in the required order
def run_xfreerdp(ip, username, password, domain):
    domain_option = f"/d:{domain} " if domain else ""
    command = f"xfreerdp /cert-ignore /compression /auto-reconnect {domain_option}/u:{username} /p:{password} /v:{ip} /dynamic-resolution /clipboard"
    print(f"Running: {command}")
    subprocess.run(command, shell=True)

# Handle Ctrl+C (KeyboardInterrupt) gracefully
def handle_exit(signal_received, frame):
    print("\nExiting...")
    exit(0)

# Get input while ignoring scroll wheel actions
def get_input(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()

    return input()

# Main function for CLI interaction
def main():
    signal.signal(signal.SIGINT, handle_exit)  # Handle Ctrl+C
    
    while True:
        print_banner()
        
        connections = load_connections()
        
        print("\n--- RDP Connection Manager ---")
        print("1. List saved connections")
        print("2. Add new connection")
        print("3. Delete a connection")
        print("4. Connect to a saved connection")
        print("5. Exit")
        
        choice = get_input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            list_connections(connections)
        elif choice == '2':
            add_connection(connections)
        elif choice == '3':
            delete_connection(connections)
        elif choice == '4':
            list_connections(connections)
            try:
                idx = int(input("\nEnter the number of the connection to connect: "))
                ip = list(connections.keys())[idx - 1]
                username = connections[ip]['username']
                password = connections[ip]['password']
                domain = connections[ip].get('domain', '')
                run_xfreerdp(ip, username, password, domain)
            except (ValueError, IndexError):
                print("Invalid selection. No changes made.")
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
