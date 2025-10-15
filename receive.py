import socket
import json

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

def send_request(request_dict):
    """Send a JSON request to the server and return the response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(json.dumps(request_dict).encode())

            data = s.recv(8192)
            if not data:
                print("No response from server.")
                return None

            response = json.loads(data.decode())
            return response

    except ConnectionRefusedError:
        print("Error: Could not connect to the server. Is it running?")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def display_dashboard():
    response = send_request({"action": "list_dashboard"})
    if not response or response.get("status") != "success":
        print("Failed to fetch dashboard.")
        return

    users = response.get("users", [])
    games = response.get("games", [])
    rentals = response.get("rentals", [])

    print("\n🎮 GameHub Dashboard\n")

    print("📌 Users:")
    if users:
        for u in users:
            print(f"  ID: {u['user_id']} | Name: {u['name']}")
    else:
        print("  No users found.")

    print("\n🎲 Games:")
    if games:
        for g in games:
            status = "Available" if g.get("available", True) else "Rented"
            print(f"  ID: {g['game_id']} | Title: {g['title']} | Status: {status}")
    else:
        print("  No games found.")

    print("\n📋 Rentals:")
    if rentals:
        for r in rentals:
            returned = "Yes" if r.get("returned") else "No"
            print(f"  Rental ID: {r['rental_id']} | User ID: {r['user_id']} | Game ID: {r['game_id']} | Returned: {returned}")
    else:
        print("  No rentals found.")

    print("\n---------------------------\n")


def main():
    print("🎮 GameHub Dashboard Client (receive.py)")
    print("Connected to server at", f"{SERVER_HOST}:{SERVER_PORT}")

    while True:
        print("\nOptions:")
        print("1. Show Dashboard")
        print("2. Exit")

        choice = input("Enter choice (1–2): ")

        if choice == "1":
            display_dashboard()
        elif choice == "2":
            print("Exiting client.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
