import socket
import sys
import time
import hashlib


print("Cliente.py")

nombre = input('Ingrese nombre \n').strip() 
password = input('Ingrese contraseña \n').strip()

def password_a_md5(password):
    if not password:
        return None
    return hashlib.md5(password.encode('utf-8')).hexdigest()

password_a_md5 = password_a_md5(password)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((sys.argv[2], int(sys.argv[3])))

msg_in = client_socket.recv(1024).decode('utf-8').strip()

"{nombre}-{clavenemd5}\r\n"


if msg_in == 'Redes 2024 - Laboratorio - Autenticacion de Usuarios':
	msg = nombre + "-" + password_a_md5 + "\r\n"
	client_socket.send(msg.encode())
	time.sleep(1)
	msg_in = client_socket.recv(1024).decode('utf-8').strip()

	#if msg_in == 'SI':
	#	login = true
	#	client_socket.close() 
	#else
	#	print(f"Usuario incorrecto, cerrando conexión")
	#client_socket.close()
	print(msg_in)
else:
	print(f"Protocolo Incorrecto")
client_socket.close()


