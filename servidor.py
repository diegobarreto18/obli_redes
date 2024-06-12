import socket
import time
import sys


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((sys.argv[1], int(sys.argv[2])))

server_socket.listen(5)

print("Servidor Hora 2024")
print(f"Escuchando en el puerto {str(sys.argv[2])}...")
while True:
	client_socket, client_address = server_socket.accept()
	print(f"conexion entrante de {client_address}")
	client_socket.send("Redes – Servidor Hora\r\n".encode())
	msg = client_socket.recv(1024).decode('utf-8').strip()
	print(msg)
	if msg == "fecha":
		fecha = time.strftime("%d/%m/%Y")
		client_socket.send(fecha.encode())
	elif msg == "hora":
		hora = time.strftime("%H:%M:%S")
		client_socket.send(hora.encode())
	else:
		client_socket.send("comando no conocido\r\n".encode())
	client_socket.close()







