import socket
import json
import re

HOST = "127.0.0.1"
PORT = 5000

def send_request(client, request):
    client.send(json.dumps(request).encode())
    response = json.loads(client.recv(8192).decode())
    return response

def show_dashboard(client):
    request = {"action": "list_dashboard"}
    response = send_request(client, request)

    print("\n=== USERS ===")
    for u in response.get("users", []):
        print(f"ID: {u.get('user_id')}, Name: {u.get('name')}, Email: {u.get('email')}")

    print("\n=== GAMES ===")
    for g in response.get("games", []):
        stock = g.get("stock", "N/A")
        available = g.get("available", "N/A")
        print(f"ID: {g.get('game_id')}, Title: {g.get('title')}, Stock: {stock}, Available: {available}")

    print("\n=== RENTALS ===")
    for r in response.get("rentals", []):
        returned = r.get("returned", "N/A")
        late_fee = r.get("late_fee", "N/A")
        due_date = r.get("due_date", "N/A")
        print(f"Rental ID: {r.get('rental_id')}, User ID: {r.get('user_id')}, Game ID: {r.get('game_id')}, Returned: {returned}, Late Fee: ${late_fee}, Due: {due_date}")
    print("")

def authenticate(client):
    print("Please log in to GameHub server:")
    username = input("Username: ")
    password = input("Password: ")
    auth_request = {"type": "auth", "username": username, "password": password}
    client.send(json.dumps(auth_request).encode())
    auth_response = json.loads(client.recv(1024).decode())
    if auth_response.get("status") != "ok":
        print("Authentication failed:", auth_response.get("message"))
        return False
    print(auth_response.get("message"))
    return True

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    if not authenticate(client):
        client.close()
        return

    while True:
        print("\n--- GameHub Read-Only Menu ---")
        print("1. Show dashboard")
        print("2. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            show_dashboard(client)
        elif choice == "2":
            print("Exiting read-only client.")
            break
        else:
            print("Invalid choice. Try again.")

    client.close()

if __name__ == "__main__":
    main()
