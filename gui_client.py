import tkinter as tk
from tkinter import messagebox
import socket
import json

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

# --- Helper function to send JSON requests to server ---
def send_request(request_dict):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            s.sendall(json.dumps(request_dict).encode())
            data = s.recv(8192)
            if not data:
                messagebox.showerror("Error", "No response from server")
                return None
            return json.loads(data.decode())
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None

# --- GUI actions ---
def show_dashboard():
    response = send_request({"action": "list_dashboard"})
    if response:
        dashboard_text.delete("1.0", tk.END)
        dashboard_text.insert(tk.END, "=== USERS ===\n")
        for user in response.get("users", []):
            dashboard_text.insert(tk.END, f"ID: {user['user_id']}, Name: {user['name']}\n")

        dashboard_text.insert(tk.END, "\n=== GAMES ===\n")
        for game in response.get("games", []):
            dashboard_text.insert(tk.END, f"ID: {game['game_id']}, Title: {game['title']}, "
                                         f"Stock: {game['stock']}, Available: {game['available']}\n")

        dashboard_text.insert(tk.END, "\n=== RENTALS ===\n")
        for rental in response.get("rentals", []):
            dashboard_text.insert(tk.END, f"Rental ID: {rental['rental_id']}, User ID: {rental['user_id']}, "
                                         f"Game ID: {rental['game_id']}, Returned: {rental['returned']}, "
                                         f"Late Fee: ${rental['late_fee']}, Due: {rental['due_date']}\n")

def create_rental():
    try:
        user_id = int(user_id_entry.get())
        game_id = int(game_id_entry.get())
        response = send_request({"action": "create_rental", "user_id": user_id, "game_id": game_id})
        if response:
            messagebox.showinfo("Rental", response.get("message"))
            show_dashboard()
    except ValueError:
        messagebox.showerror("Error", "User ID and Game ID must be numbers")

def return_rental():
    try:
        rental_id = int(rental_id_entry.get())
        response = send_request({"action": "return_rental", "rental_id": rental_id})
        if response:
            messagebox.showinfo("Return Rental", response.get("message"))
            show_dashboard()
    except ValueError:
        messagebox.showerror("Error", "Rental ID must be a number")

# --- Main window ---
root = tk.Tk()
root.title("GameHub GUI Client")
root.geometry("500x600")

# --- Inputs ---
tk.Label(root, text="User ID:").pack()
user_id_entry = tk.Entry(root)
user_id_entry.pack()

tk.Label(root, text="Game ID:").pack()
game_id_entry = tk.Entry(root)
game_id_entry.pack()

tk.Label(root, text="Rental ID (for return):").pack()
rental_id_entry = tk.Entry(root)
rental_id_entry.pack()

# --- Buttons ---
tk.Button(root, text="Create Rental", command=create_rental).pack(pady=5)
tk.Button(root, text="Return Rental", command=return_rental).pack(pady=5)
tk.Button(root, text="Show Dashboard", command=show_dashboard).pack(pady=5)

# --- Dashboard display ---
dashboard_text = tk.Text(root, height=20, width=60)
dashboard_text.pack(pady=10)

# --- Start GUI ---
root.mainloop()
