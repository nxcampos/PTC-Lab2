import json
import socket
from cryptography.fernet import Fernet

# O problema no código apresentado ocorre porque o estado da tarefa (completo ou incompleto) não está a ser carregado corretamente a partir do ficheiro todo_list.fernet.
# A solução para este problema passa por alterar o método de leitura do ficheiro todo_list.fernet para incluir a informação sobre o estado da tarefa.
# Assim, a função TodoList.init() deve ser modificada para aceitar uma linha do ficheiro todo_list.fernet como argumento e inicializar o objeto TodoItem com o estado da tarefa correto. 
# A função TodoList.save_cipher() também deve ser modificada para incluir o estado da tarefa na linha do ficheiro todo_list.fernet.


class TodoItem:
    def __init__(self, title, description, completed=False):
        self.title = title
        self.description = description
        self.completed = completed

    def __str__(self):
        status = "[ ]"
        if self.completed:
            status = "[x]"
        return f"{status} {self.title}: {self.description}"

class TodoList:
    def __init__(self):
        self.items = []

    def add_item(self, title, description):
        item = TodoItem(title, description)
        self.items.append(item)

    def complete_item(self, index):
        if (index < 0 or index >= len(self.items)):
            raise IndexError("Invalid index")
        item = self.items[index]
        item.completed = True

    def count_items(self):
        return len(self.items)

    def save_cipher(self, key):
        cipher = Fernet(key)
        with open('todo_list.fernet', 'w') as file:
            for i, item in enumerate(self.items):
                plain_item = f"{item.title},{item.description},{item.completed}"
                c_item = cipher.encrypt(plain_item.encode()).decode()
                file.write(f"{c_item}\n")

    def get_list_of_items(self):
        result = ""
        for i, item in enumerate(self.items):
            result += f"{i}. {str(item)}\n"
        return result

host = 'localhost'
port = 8888

# load key
with open('key.fernet', 'rb') as key_file:
    key = key_file.read()
    print("Loaded key: ", key)

# verifica se todo_list.fernet existe
try:
    with open('todo_list.fernet', 'r') as file:
        todo_list = TodoList()
        for line in file:
            cipher = Fernet(key)
            c_item = line.strip()
            plain_item = cipher.decrypt(c_item.encode()).decode()
            title, description, completed = plain_item.split(",")
            todo_list.items.append(TodoItem(title, description, completed == "True"))
except FileNotFoundError:
    todo_list = TodoList()

# create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()

print(f"Server started on port {port}...")
print("Serving todo list...")
print(todo_list.get_list_of_items())

# Loop forever, waiting for client commands
while True:
    # Accept a connection
    print("Waiting for connection...")
    client_socket, address = server_socket.accept()
    print(f"Connected to {address}")

    # receive operation and numbers and make calculation
    command = client_socket.recv(1024).decode()
    print(f"Received command: {command}")
    choice, data = command.split("-")
    if choice == "1":
        title, description = data.split(",")
        todo_list.add_item(title, description)
        result = "Todo added."
    elif choice == "2":
        result = todo_list.get_list_of_items()
    elif choice == "3":
        index = int(data)
        todo_list.complete_item(index)
        result = "Todo completed."
    else:
        result = "Invalid command."
    print("Logging: " + result)
    client_socket.send(result.encode())
    client_socket.close()
    todo_list.save_cipher(key)
