import socket
import json

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

def send_request(request_dict):
    """Send a JSON request to the server and print the response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(json.dumps(request_dict).encode())

            data = s.recv(4096)
            if not data:
                print("No response from server.")
                return

            response = json.loads(data.decode())
            print("\n--- Server Response ---")
            print(json.dumps(response, indent=2))
            print("------------------------\n")

    except ConnectionRefusedError:
        print("Error: Could not connect to the server. Is it running?")
    except Exception as e:
        print(f"Error: {e}")


def main():
    print("🎮 GameHub Mutation Client (send.py)")
    print("Connected to server at", f"{SERVER_HOST}:{SERVER_PORT}")

    while True:
        print("\nChoose an action:")
        print("1. Add user")
        print("2. Add game")
        print("3. Create rental")
        print("4. Return rental")
        print("5. Exit")

        choice = input("Enter choice (1–5): ")

        if choice == "1":
            name = input("Enter user name: ")
            send_request({"action": "add_user", "name": name})

        elif choice == "2":
            title = input("Enter game title: ")
            send_request({"action": "add_game", "title": title})

        elif choice == "3":
            try:
                user_id = int(input("Enter user ID: "))
                game_id = int(input("Enter game ID: "))
                send_request({"action": "create_rental", "user_id": user_id, "game_id": game_id})
            except ValueError:
                print("Invalid input. IDs must be numbers.")

        elif choice == "4":
            try:
                rental_id = int(input("Enter rental ID: "))
                send_request({"action": "return_rental", "rental_id": rental_id})
            except ValueError:
                print("Invalid input. ID must be a number.")

        elif choice == "5":
            print("Exiting client.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
