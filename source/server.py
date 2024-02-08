import socket
import os
import re
import select
import queue

connection = None
server = None
server_host = "::"
server_port = 8080
buffer_size = 1024
inputs = []
outputs = []
message_queues = {}

def main():
    create_socket()
    listen_connections()
    try:
        while True:
            
            data = accept_connection()
            # decode and manipulate data
            decoded_data = check_data(data)
            words = get_words(decoded_data)
            word_count = get_word_count(words)
            char_count = get_char_count(words)
            char_freq = get_char_freq(words)
            sorted_chars = sort_dict(char_freq)
            response = format_response(word_count, char_count, sorted_chars)
            # Send a response back to the client
            send_response(response)
    except Exception as e:
        print(f"Error: Failed to receive data from client")

def create_socket():
    try:
        global server, inputs
        addr = (server_host, server_port)
        if socket.has_dualstack_ipv6():
            server = socket.create_server(addr, family=socket.AF_INET6, dualstack_ipv6=True)
            print("Server running on dual-stack mode (IPv4 and IPv6).")
        else:
            server = socket.create_server(addr)
            print("Server running on default mode.")
        inputs = [server]
        server.setblocking(0)
            
    except Exception as e:
        print(e)
        print(f"Error: Failed to create socket server")
        exit(1)
        

def listen_connections():
    try:
        server.listen(5)
        print(f'Server is listening on port {server_port} for incoming connections...')
    except Exception as e:
        print(f"Error: Failed to listen to connections")
        exit(1)

def accept_connection():
    try:
        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)

            for s in readable:
                if s is server:
                    connection, client_addr = s.accept()
                    print('Connection Received: ', client_addr)
                    connection.setblocking(0)
                    inputs.append(connection)

                    message_queues[connection] = queue.Queue()
                else:
                    data = s.recv(1024)
                    if data:
                        # print(f"Receieved data from: ", s.getpeername())
                        message_queues[s].put(data)
                        if s not in outputs:
                            outputs.append(s)
                    else:
                        # print(f"Closing: ", client_addr)
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()

                        del message_queues[s]

            for s in writable:
                try:
                    message_data = message_queues[s].get_nowait()
                except queue.Empty:
                    # print(f"Output queue for", s.getpeername(), "is empty")
                    outputs.remove(s)
                else:
                    # print(f"Sending data to: ", s.getpeername())
                    next_msg = handle_data(message_data)
                    s.send(next_msg)
            
            for s in exceptional:
                # print(f"Handling exceptional condition for: ", s.getpeername())
                inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)
                s.close()

                del message_queues[s]
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

def handle_data(data):
    decoded_data = check_data(data)
    words = get_words(decoded_data)
    word_count = get_word_count(words)
    char_count = get_char_count(words)
    char_freq = get_char_freq(words)
    sorted_chars = sort_dict(char_freq)
    response = format_response(word_count, char_count, sorted_chars)
    response = response.encode()
    response = decoded_data.encode()
    return response

def check_data(data):
    try:
        if not data:
            raise Exception("Failed to receive data")
            
        res = data.decode()
        return res
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

def send_response(response):
    try:
        connection.sendall(response.encode())
    except Exception as e:
        print(e)
        print(f"Error: Failed to send response to client")
        exit(1)

def close_socket_server(connection, socket_path):
    try:
        connection.close()
        os.unlink(socket_path)
    except Exception as e:
        print(f"Error: Failed to close the socket")
        exit(1)

def get_words(word_string):
    formatted_string = remove_whitespace(word_string)
    words = formatted_string.split(" ")
    words = [x for x in words if x]
    return words

def get_word_count(words):
    return len(words)

def remove_whitespace(word_string):
    try:
        return re.sub(' +', ' ', word_string)
    except Exception as e:
        print(f"Error: Failed to remove whitespaces in data")
        exit(1)

def get_char_count(words):
    count = 0
    for word in words:
        count += len(word)
    return count

def get_char_freq(words):
    char_dict = {}
    words = [word.lower() for word in words]
    words = "".join(words)
    for c in words:
        if c in char_dict:
            char_dict[c] += 1
        else:
            char_dict[c] = 1
    return char_dict

def format_response(word_count, char_count, char_freq):
    response = "Word Count: %d\nCharacter Count: %d\nCharacter Frequencies:"%(word_count, char_count)

    for key, value in char_freq.items():
        response += "\n%s: %d"%(key, value)
    return response

def sort_dict(char_freq):
    keys = list(char_freq.keys())
    keys.sort()
    return {i: char_freq[i] for i in keys}

main()