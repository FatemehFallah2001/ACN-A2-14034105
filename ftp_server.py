import socket
import os
from cryptography.fernet import Fernet

def load_key():
    return b'your_key_here'  # Replace this with a secure key

def encrypt_file(filename):
    key = load_key()
    fernet = Fernet(key)
    with open(filename, 'rb') as file:
        original = file.read()
    encrypted = fernet.encrypt(original)
    with open(filename, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

def decrypt_file(filename):
    key = load_key()
    fernet = Fernet(key)
    with open(filename, 'rb') as enc_file:
        encrypted = enc_file.read()
    decrypted = fernet.decrypt(encrypted)
    with open(filename, 'wb') as dec_file:
        dec_file.write(decrypted)

def handle_client(client_socket):
    while True:
        command = client_socket.recv(1024).decode()
        if not command:
            break

        if command.startswith("UPLOAD"):
            filename = command.split()[1]
            filesize = int(client_socket.recv(1024).decode())
            with open(filename, "wb") as f:
                bytes_received = 0
                while bytes_received < filesize:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    f.write(data)
                    bytes_received += len(data)
            decrypt_file(filename)
            client_socket.send("UPLOAD_SUCCESS".encode())

        elif command.startswith("DOWNLOAD"):
            filename = command.split()[1]
            if os.path.exists(filename):
                client_socket.send("FILE_EXISTS".encode())
                filesize = os.path.getsize(filename)
                client_socket.send(str(filesize).encode())
                encrypt_file(filename)
                with open(filename, "rb") as f:
                    while (chunk := f.read(1024)):
                        client_socket.send(chunk)
                client_socket.send("DOWNLOAD_SUCCESS".encode())
            else:
                client_socket.send("FILE_NOT_FOUND".encode())

        elif command.startswith("DELETE"):
            filename = command.split()[1]
            try:
                os.remove(filename)
                client_socket.send("FILE_DELETED".encode())
            except FileNotFoundError:
                client_socket.send("FILE_NOT_FOUND".encode())

        elif command.startswith("SEARCH"):
            filename = command.split()[1]
            if os.path.exists(filename):
                client_socket.send("FILE_FOUND".encode())
            else:
                client_socket.send("FILE_NOT_FOUND".encode())

        elif command == "LIST":
            files = os.listdir('.')
            files_list = '\n'.join(files)
            client_socket.send(files_list.encode())

        elif command == "EXIT":
            break

    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", 5557))  # Port 5557
    server_socket.listen(5)
    print("Server is running on port 5557...")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            handle_client(client_socket)
        except Exception as e:
            print(f"Error accepting client connection: {e}")

if __name__ == "__main__":
    start_server()
