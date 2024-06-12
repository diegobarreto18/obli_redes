import socket
import sys
import time
import hashlib
import threading

# # # # # # # # # # # # # # # # # # # # # # # #
# Diego Barreto - 5.319.339-9				  #
# Paula Vidal -								  #
# Brian Montero - 5.394.683-1				  #
# Alexis Rojas - 4.679.803-9				  #
# # # # # # # # # # # # # # # # # # # # # # # #


print("Cliente.py")

#Inputs de los datos
nombre = input('Ingrese nombre \n').strip() 
password = input('Ingrese contraseña \n').strip()

#Esto es para después validar que se logueó bien
login = False

#Inicio declaracion de funciones

def password_a_md5(password):
    if not password:
        return None
    return hashlib.md5(password.encode('utf-8')).hexdigest()


def enviar_mensaje(destino):
	send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	
	#CORREGIR HARDCODE
	#send_socket.connect((destino,4300))

	to_send = input().strip()

	send_socket.send(to_send.encode())


#Fin declaracion de funciones

#Creo socket
auth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
auth_socket.connect((sys.argv[2], int(sys.argv[3])))

#Recibo saludo del Servidor
msg_in = auth_socket.recv(1024).decode('utf-8').strip()

#Inicio proceso de autenticacion
if msg_in == 'Redes 2024 - Laboratorio - Autenticacion de Usuarios':
	
	password_a_md5 = password_a_md5(password)
	msg = f"{nombre}-{password_a_md5}\r\n"

	auth_socket.send(msg.encode())
	
	time.sleep(1)
	
	msg_in = auth_socket.recv(1024).decode('utf-8').strip()

	if msg_in != 'NO':
		login = True
		print(f'Usuario válido')
		decision = input('quiere enviar mensaje? \n').strip()
		
		if decision == 'S':
			host_destino = input('Ingrese ip destino o nombre host \n').strip()
			enviar_mensaje(host_destino)
		else:
			pass
	else:
		print(f"Usuario incorrecto, cerrando conexión")
	
	auth_socket.close()

else:
	print(f"Protocolo Incorrecto")


auth_socket.close()

def manejar_ingreso(socket):
	while True:
		data = socket.recv(1024)
		if not data:
			break
		
		print(data.decode())
	

receptor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receptor_socket.bind(("192.168.32.14", int(sys.argv[1])))
receptor_socket.listen()

conexion, addr = receptor_socket.accept()
receptor_thread = threading.Thread(target=manejar_ingreso, args=(conexion,))
receptor_thread.start()
receptor_thread.join()
