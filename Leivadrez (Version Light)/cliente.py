import socket
import threading

SERVER_HOST = 'localhost'  
SERVER_PORT = 12345

# Crear y conectar el socket del cliente al servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))
print("Conectado al servidor de ajedrez")

def send_move(move):
    """Envía el movimiento al servidor."""
    client_socket.send(move.encode('utf-8'))

def receive_move():
    """Recibe los movimientos del oponente y los imprime."""
    while True:
        try:
            move = client_socket.recv(1024).decode('utf-8')
            if move == "FIN":
                print("El juego ha terminado.")
                break
            print(f"Movimiento del oponente: {move}")
            # Aquí puedes agregar código para actualizar el tablero con el movimiento recibido
        except:
            print("Conexión perdida.")
            break
    client_socket.close()

# Hilo separado para escuchar los movimientos del oponente
threading.Thread(target=receive_move).start()

# Bucle para enviar movimientos
while True:
    move = input("Introduce tu movimiento (o escribe 'FIN' para terminar): ")
    send_move(move)
    if move == "FIN":
        print("Terminando la partida...")
        break

client_socket.close()
