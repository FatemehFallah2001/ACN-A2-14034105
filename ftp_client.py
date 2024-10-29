import socket
import os
from cryptography.fernet import Fernet


def load_key():
    return b'your_key_here'  # Replace this with a secure key


def upload_files(client_socket, filenames):
    for filename in filenames:
        if not os.path.exists(filename):
            print(f"File {filename} does not exist.")
            continue

        client_socket.send(f"UPLOAD {filename}".encode())
        filesize = os.path.getsize(filename)
        client_socket.send(str(filesize).encode())

        with open(filename, "rb") as f:
            bytes_sent = 0
            while (chunk := f.read(1024)):
                client_socket.send(chunk)
                bytes_sent += len(chunk)

        confirmation = client_socket.recv(1024).decode()
        if confirmation == "UPLOAD_SUCCESS":
            print(f"Upload successful: {filename}")


def download_files(client_socket, filenames):
    for filename in filenames:
        client_socket.send(f"DOWNLOAD {filename}".encode())
        response = client_socket.recv(1024).decode()

        if response == "FILE_EXISTS":
            filesize = int(client_socket.recv(1024).decode())
            with open(filename, "wb") as f:
                bytes_received = 0
                while bytes_received < filesize:
                    data = client_socket.recv(1024)
                    f.write(data)
                    bytes_received += len(data)
            client_socket.send("DOWNLOAD_SUCCESS".encode())
            print(f"Download successful: {filename}")
        elif response == "FILE_NOT_FOUND":
            print(f"File {filename} not found on server.")


def delete_file(client_socket, filename):
    client_socket.send(f"DELETE {filename}".encode())
    response = client_socket.recv(1024).decode()
    print(f"Delete response: {response}")


def search_file(client_socket, filename):
    client_socket.send(f"SEARCH {filename}".encode())
    response = client_socket.recv(1024).decode()
    print(f"Search response: {response}")


def list_files(client_socket):
    client_socket.send("LIST".encode())
    files_list = client_socket.recv(4096).decode()
    print("Files on server:\n" + files_list)


def main():
    server_ip = "127.0.0.1"  # Server IP
    server_port = 5557  # Server port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((server_ip, server_port))
        print("Connected to server.")

        while True:
            print("\nSelect an action:")
            print("1: Upload files")
            print("2: Download files")
            print("3: Delete a file")
            print("4: Search for a file")
            print("5: List files")
            print("6: Exit")
            choice = input("Enter your choice (1-6): ")

            if choice == "1":
                filenames = input("Enter filenames to upload (space-separated): ").split()
                upload_files(client_socket, filenames)

            elif choice == "2":
                filenames = input("Enter filenames to download (space-separated): ").split()
                download_files(client_socket, filenames)

            elif choice == "3":
                filename = input("Enter filename to delete: ")
                delete_file(client_socket, filename)

            elif choice == "4":
                filename = input("Enter filename to search: ")
                search_file(client_socket, filename)

            elif choice == "5":
                list_files(client_socket)

            elif choice == "6":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please choose a number between 1 and 6.")

    except ConnectionRefusedError:
        print("Connection to server failed. Ensure the server is running.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
