import socket
import sys
import time
import hashlib
import threading
from datetime import datetime
import os
from getpass import getpass
import subprocess

# # # # # # # # # # # # # # # # # # # # # # # #
# Diego Barreto - 5.319.339-9				  #
# Paula Vidal -								  #
# Brian Montero - 5.394.683-1				  #
# Alexis Rojas - 4.679.803-9				  #
# # # # # # # # # # # # # # # # # # # # # # # #

PUERTO = int(sys.argv[1])
IP_AUTENTICACION = sys.argv[2]
PUERTO_AUTENTICACION = int(sys.argv[3])

clients = []

def password_a_md5(password):
    if not password:
        return None
    return hashlib.md5(password.encode('utf-8')).hexdigest()

def get_server_responses(sock):
    respuestas = []

    while True:
        time.sleep(1.5)
        try:
            next_data: bytes = sock.recv(3000)
            if not next_data:
                break
            next_response = next_data.decode()
            respuestas = next_response.split('\r\n')
        except socket.error:
            raise Exception()
    return respuestas

def solicitud_server_autenticacion(nombre_de_usuario):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as auth_socket:
        auth_socket.connect((IP_AUTENTICACION, PUERTO_AUTENTICACION))

        auth_socket.sendall(b"")
        data = auth_socket.recv(3000)
        if not data.decode().startswith("Redes 2024 - Laboratorio - Autenticacion de Usuarios"):
            return None
        
        md5_password = password_a_md5(nombre_de_usuario)
        mensaje = f"{nombre_de_usuario}-{md5_password}\r\n"

        auth_socket.sendall(mensaje.encode('utf-8'))
        respuestas = get_server_responses(auth_socket)

        if respuestas[0] == 'NO':
            return None

        nombre = respuestas[1]
        return nombre

def autenticar():
    nombre = input('Usuario: ')
    password = getpass('Clave: ')

    if not nombre or not password:
        print('Por favor ingrese todos los datos requeridos')
        os._exit()

    nombre_completo = solicitud_server_autenticacion(password)
    if not nombre_completo:
        print('Usuario o clave incorrecto')
        os._exit()

    return nombre_completo

def get_destinatario(mensaje: str):
	data = mensaje.split()
	return data[0]

def get_mensaje_formateado(mensaje: str, destinatario):
	division_mensaje = mensaje.split()
	mensaje_original = ' '.join(division_mensaje[1:])
	return f"[{datetime.now().strftime('%Y.%m.%d')} {datetime.now().strftime('%H:%M')}] {destinatario} dice: {mensaje_original}".encode()

def emitir():
    mensaje = input()
    destinatario = get_destinatario(mensaje)
    mensaje_completo = get_mensaje_formateado(mensaje, destinatario)
        
    emisor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    emisor_socket.connect((destinatario, PUERTO))
    emisor_socket.sendall(mensaje_completo)

def recibir(socket):
	while True:
		data = socket.recv(1024)
        
		if not data:
			continue
        
		print(data.decode())
                
def levantar_server():
    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', PUERTO))
        server_socket.listen()
                
        cliente_socket, cliente_direccion = server_socket.accept()
        clients.append(cliente_socket)
                
        emitir_thread = threading.Thread(target=emitir, args=())
        emitir_thread.start()
        emitir_thread.join()
                
        client_thread = threading.Thread(target=recibir, args=(cliente_socket,))
        client_thread.start()
        client_thread.join()

nombre = autenticar()

if not nombre:
	pass
        
print(f"Bienvenido {nombre}")

levantar_server()
