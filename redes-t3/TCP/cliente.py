import socket
import sys
import time

print("Cliente Hora 2024")

msg = input("fecha/hora: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((sys.argv[1], int(sys.argv[2])))

time.sleep(1)

msg_in = client_socket.recv(1024).decode('utf-8').strip()

if msg_in == "Redes – Servidor Hora":
	time.sleep(1)
	client_socket.send(msg.encode())
	msg_in = client_socket.recv(1024).decode('utf-8').strip()
	print(msg_in)
else:
	print(f"Protocolo Incorrecto")
client_socket.close()




