import socket
import hashlib

# constantes de ip/hostname y port del servidor de autenticación 

SERVIDOR_AUTENTICACION_HOST = "ti.esi.edu.uy"
SERVIDOR_AUTENTICACION_PORT = 33

# toma un string `password` y retorna el hash de ese string

def password_a_md5(password):
    if not password:
        return None
    return hashlib.md5(password.encode('utf-8')).hexdigest()

# toma el socket de autenticación y drena el buffer de respuestas, cuando el socket no retorna más respuestas, rompe el while y retorna el array `respuestas` 
# (`respuestas` es un array con todo lo que retornó el server decodeado) 

def get_server_responses(sock):
    respuestas = []

    while True:
        try:
            next_data = sock.recv(3000)
            if not next_data:
                break
            next_response = next_data.decode('utf-8')
            respuestas = next_response.split('\r\n')
        except socket.error:
            raise Exception()
        
    return respuestas

# toma un username y autentica al user

def solicitud_server_autenticacion(nombre_de_usuario):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as auth_socket:
        auth_socket.connect((SERVIDOR_AUTENTICACION_HOST, SERVIDOR_AUTENTICACION_PORT))

        auth_socket.sendall(b"")
        data = auth_socket.recv(3000)
        if not data:
            return None
        
        md5_password = password_a_md5(nombre_de_usuario)
        mensaje = f"{nombre_de_usuario}-{md5_password}\r\n"

        auth_socket.sendall(mensaje.encode('utf-8'))
        respuestas = get_server_responses(auth_socket)

        if respuestas[0] == 'NO':
            return None

        nombre = respuestas[1]
        return nombre or "User"

solicitud_server_autenticacion("aturing")
