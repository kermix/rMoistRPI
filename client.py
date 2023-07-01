import socket


host = "localhost"
port = 2137
lenth = 1024

with socket.socket() as client_socket:
    client_socket.connect((host, port))

    message = input("Message to a server: ")

    while True:
        if message.lower().strip() == 'q':
            break

        client_socket.send(message.encode()) 

        data = client_socket.recv(lenth).decode() 
        print('Received from server: ' + data)

        message = input("Message to a server: ")

