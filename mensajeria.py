import socket
import sys
import time
import hashlib
import threading
from datetime import datetime
import os
from getpass import getpass
import queue
import ipaddress

# # # # # # # # # # # # # # # # # # # # # # # #
# Diego Barreto - 5.319.339-9				  #
# Paula Vidal -								  #
# Brian Montero - 5.394.683-1				  #
# Alexis Rojas - 4.679.803-9				  #
# # # # # # # # # # # # # # # # # # # # # # # #

PUERTO = int(sys.argv[1])
IP_AUTENTICACION = sys.argv[2]
PUERTO_AUTENTICACION = int(sys.argv[3])
MI_IP = sys.argv[4]

MAX_LARGO_MENSAJE = 255

input_queue = queue.Queue()
clientes = []
nombre_usuario_autenticado = ''

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
        os._exit(0)

    return nombre_completo

def get_destinatario(mensaje: str):
	data = mensaje.split()
	return data[0]

def get_archivo(mensaje):
    destinatario, indicador, path = mensaje.split()
    archivo_binario = None

    if not path or not os.path.exists(path):
        return archivo_binario
    
    archivo_full_nombre = os.path.basename(path)
    nombre_archivo, extension = os.path.splitext(archivo_full_nombre)

    with open(path, 'rb') as archivo:
        all_data = b''
        while True:
            data = archivo.read(1024)
            if not data:
                break
            all_data += data

    return [all_data, nombre_archivo + extension + '\n']

def get_mensaje_formateado(mensaje, destinatario = None):
	division_mensaje = mensaje.split()
	mensaje_original = ' '.join(division_mensaje[1:])
	return f"[{datetime.now().strftime('%Y.%m.%d')} {datetime.now().strftime('%H:%M')}] {MI_IP if not destinatario else destinatario} {nombre_usuario_autenticado} dice: {mensaje_original}".encode()

def input_thread():
    while True:
        mensaje = input()
        input_queue.put(mensaje)

def emitir():
    while True:
        mensaje = input_queue.get()
        destinatario = get_destinatario(mensaje)
        archivo_a_mandar = None
        nombre_archivo_a_mandar = None

        if mensaje.find('&file') > -1:
            tupla = get_archivo(mensaje)
            if not tupla:
                print('El archivo no existe o no se encontro')
                return

            archivo_a_mandar, nombre_archivo_a_mandar = tupla

        if destinatario == '*':
            broadcast(mensaje, archivo_a_mandar, nombre_archivo_a_mandar)
            return

        emisor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        emisor_socket.connect((destinatario, PUERTO))
        
        if bool(archivo_a_mandar):
            emisor_socket.sendall(b'ARCHIVO\n')
            time.sleep(1)
            emisor_socket.sendall(nombre_archivo_a_mandar.encode())
            time.sleep(1)
            emisor_socket.sendall(b'\n')
            time.sleep(1)
            emisor_socket.sendall(archivo_a_mandar)
            time.sleep(1)
            emisor_socket.sendall(b'ENDOFFILE')
        else:
            mensaje_completo = get_mensaje_formateado(mensaje)
            emisor_socket.sendall(b'TEXTO\n')
            time.sleep(1)
            emisor_socket.sendall(mensaje_completo)
            time.sleep(1)
            emisor_socket.sendall(b'\n')

def guardar_archivo(cliente_socket):
    nombre_archivo = get_nombre_de_archivo(cliente_socket)

    if not nombre_archivo:
        return None

    path_a_guardar = os.path.join(os.getcwd(), nombre_archivo)

    with open(path_a_guardar, 'wb') as archivo:
        total_data = b''
        primer_chunk = True
        while True:
            data = cliente_socket.recv(1024)
            if primer_chunk:
                data = data.lstrip(b'\n')
                primer_chunk = False
            if b'ENDOFFILE' in data:
                break
            total_data += data
        
        archivo.write(total_data)

    return nombre_archivo

def get_nombre_de_archivo(cliente_socket):
    nombre_archivo = b''
    while True:
        char = cliente_socket.recv(1)
        if char == b'\n':
            break
        nombre_archivo += char
    nombre_archivo = nombre_archivo.decode()
    return nombre_archivo

def broadcast(mensaje, archivo_a_mandar, nombre_archivo_a_mandar):
    for cliente in clientes:
        if bool(archivo_a_mandar):
            cliente.sendall(b'ARCHIVO\n')
            time.sleep(1)
            cliente.sendall(nombre_archivo_a_mandar.encode())
            time.sleep(1)
            cliente.sendall(b'\n')
            time.sleep(1)
            cliente.sendall(archivo_a_mandar)
            time.sleep(1)
            cliente.sendall(b'ENDOFFILE')
        else:
            mensaje_completo = get_mensaje_formateado(mensaje)
            cliente.sendall(b'TEXTO\n')
            time.sleep(1)
            cliente.sendall(mensaje_completo)
            time.sleep(1)
            cliente.sendall(b'\n')

def recibir_mensaje(cliente_socket) -> bytes:
    respuestas = []

    while True:
        data = cliente_socket.recv(1024)
        if not data or data.endswith(b'\n'):
            break
        respuestas.append(data.decode())
    
    return respuestas[0]

def recibir(cliente_socket):
    while True:
        data = cliente_socket.recv(1024)

        if not data.decode() or data.decode() == '\r\n':
            continue

        if data.startswith(b'ARCHIVO\n'):
            archivo_nombre = guardar_archivo(cliente_socket)
            if not archivo_nombre:
                print(f"[{datetime.now().strftime('%Y.%m.%d')} {datetime.now().strftime('%H:%M')}] <Error recibiendo archivo>")
            else:
                print(f"<Recibido ./{archivo_nombre}>")
        if data.startswith(b'TEXTO\n'):
            print(recibir_mensaje(cliente_socket))
                
def levantar_server():
    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((MI_IP, PUERTO))
        server_socket.listen()
                
        cliente_socket, cliente_direccion = server_socket.accept()
        clientes.append(cliente_socket)
                                
        client_thread = threading.Thread(target=recibir, args=(cliente_socket,))
        client_thread.start()

nombre_usuario_autenticado = autenticar()

if not nombre_usuario_autenticado:
	pass
        
print(f"Bienvenido {nombre_usuario_autenticado}")

input_var_thread = threading.Thread(target=input_thread, args=())
input_var_thread.start()

emitir_thread = threading.Thread(target=emitir, args=())
emitir_thread.start()

levantar_server()
