import socket
import sys
import os
import ipaddress


socket_path = '/tmp/domain_socket'
ipv4 = "10.0.0.34"
ipv6 = "2604:3d08:597e:ef00:a21d:8635:3d84:d9d1"
server_host = ipv6
server_port = 8080
file_name = None
client = None


def main():
    check_args(sys.argv)
    handle_args(sys.argv)
    words = read_file()

    if words:
        create_socket()
        connect_client()
        send_message(words)
        receieve_response()

        close_socket_client(client)

def check_args(args):
    try:
        if len(args) != 2:
            raise Exception("Invalid number of arguments")
        elif not args[1].endswith('.txt'):
            raise Exception("Invalid file extension, please input a .txt file")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

def handle_args(args):
    global file_name
    try:
        file_name = sys.argv[1]
    except Exception as e:
        print(f"Error: Failed to retrieve inputted arguments.")

def create_socket():
    try: 
        global client
        # INET = IPv4 /// INET6 = IPv6
        client = socket.socket((socket.AF_INET6, socket.AF_INET)[is_ipv4(server_host)], socket.SOCK_STREAM)

    except Exception as e:
        print(e)
        print(f"Error: Failed to create client socket")
        exit(1)

def connect_client():
    try: 
        client.connect((server_host, server_port))
    except Exception as e:
        print(e)
        print(f"Error: Failed to connect to socket path")
        exit(1)

def send_message(words):
    try: 
        encoded = words.encode()
        # x = str(len(words)).encode()
        # client.sendall(x)
        # client.recv(1)

        client.sendall(encoded)
    except Exception as e:
        print(e)
        print(f"Error: Failed to send words")
        exit(1)

def receieve_response():
    try: 
        response = client.recv(1024)
        print(f'Received response\n{response.decode()}')
    except Exception as e:
        print(f"Error: Failed to receive response")
        exit(1)

def close_socket_client(client):
    try: 
        client.close()
    except Exception as e:
        print(f"Error: Failed to close socket")
        exit(1)

def read_file():
    try:
        with open(file_name, 'r') as file:
            content = file.read()
            if not content:
                raise Exception("File is empty.")
            formatted_data = replace_new_lines(content)
            return formatted_data
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
    except Exception as e:
        print(f"Error: {e}")

def replace_new_lines(text_data):
    try:
        res = text_data.replace('\n', ' ')
        return res
    except Exception as e:
        print(f"Error: {e}")

def is_ipv4(ip_str):
    try:
        # Try to create an IPv4 address
        ipaddress.IPv4Address(ip_str)
        return True
    except ipaddress.AddressValueError:
        # The string is not a valid IPv4 address
        pass

    try:
        # Try to create an IPv6 address
        ipaddress.IPv6Address(ip_str)
        return False
    except ipaddress.AddressValueError:
        # The string is not a valid IPv6 address
        pass
    err_message = "Invalid IP Address found."
    handle_error(err_message)
    
def handle_error(err_message):
    print(f"Error: {err_message}")
    cleanup(False)
    
def cleanup(success):
    client.close()
    if success:
        exit(0)
    exit(1)

if __name__ == "__main__":
    main()