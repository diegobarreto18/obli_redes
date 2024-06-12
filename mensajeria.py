import socket
import sys
import time
import hashlib

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

#Fin declaracion de funciones

#Creo socket
auth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
auth_socket.connect((sys.argv[1], int(sys.argv[2])))

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
	else:
		print(f"Usuario incorrecto, cerrando conexión")
	
	auth_socket.close()

else:
	print(f"Protocolo Incorrecto")


auth_socket.close()