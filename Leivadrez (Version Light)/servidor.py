import asyncio
import websockets
import json

# Lista de conexiones de jugadores
players = []
turno_actual = 0  # Para alternar turnos (0 para jugador 1, 1 para jugador 2)

# Función para manejar cada conexión
async def handler(websocket):
    global players, turno_actual
    
    if len(players) >= 2:
        # Si ya hay dos jugadores, rechazamos la conexión
        await websocket.send(json.dumps({"error": "La partida ya tiene dos jugadores."}))
        await websocket.close()
        return
    
    # Añadir jugador a la lista
    players.append(websocket)
    jugador_id = len(players)  # Identificador del jugador (1 o 2)
    print(f"Jugador {jugador_id} conectado.")
    
    try:
        await websocket.send(json.dumps({"message": f"Eres el Jugador {jugador_id}"}))
        
        # Escucha mensajes del cliente
        async for message in websocket:
            print(f"Mensaje recibido de Jugador {jugador_id}: {message}")
            
            try:
                # Intenta parsear el mensaje como JSON
                move = json.loads(message)
                
                if move["type"] == "movimiento":
                    # Verificar que el jugador está en su turno
                    if turno_actual != jugador_id - 1:
                        await websocket.send(json.dumps({"error": "No es tu turno"}))
                        continue
                    
                    # Procesar movimiento
                    origen = move["origen"]
                    destino = move["destino"]
                    pieza = move["pieza"]
                    color = move["color"]
                    
                    # Validar movimiento aquí si es necesario
                    response = {
                        "type": "movimiento",
                        "origen": origen,
                        "destino": destino,
                        "pieza": pieza,
                        "color": color,
                        "turno": turno_actual
                    }
                    
                    # Enviar a ambos jugadores el movimiento
                    for player in players:
                        await player.send(json.dumps(response))
                    
                    # Cambiar turno
                    turno_actual = 1 - turno_actual
                
                elif move["type"] == "jaque":
                    # Procesar un mensaje de jaque
                    response = {
                        "type": "jaque",
                        "color": move["color"],
                        "status": move["status"]
                    }
                    # Enviar a ambos jugadores
                    for player in players:
                        await player.send(json.dumps(response))
                
                elif move["type"] == "fin_partida":
                    # El juego terminó (jaque mate o empate)
                    response = {
                        "type": "fin_partida",
                        "mensaje": "El juego ha terminado. ¡Victoria!"
                    }
                    for player in players:
                        await player.send(json.dumps(response))
                    players.clear()  # Limpiar la lista de jugadores
                    
                else:
                    response = {"error": "Tipo de mensaje no reconocido"}
            
            except json.JSONDecodeError:
                # Si el mensaje no es un JSON válido, responde con un error
                response = {"error": "Mensaje no es JSON válido"}
            
    except websockets.ConnectionClosed:
        # El jugador se desconectó
        print(f"Jugador {jugador_id} se desconectó.")
        players.remove(websocket)
        
        # Si el otro jugador está esperando, se le puede notificar
        if len(players) == 1:
            await players[0].send(json.dumps({"message": "El otro jugador se desconectó. Esperando un nuevo jugador..."}))
        
    except Exception as e:
        # Manejo de cualquier otro error
        print(f"Error en el manejo de la conexión: {e}")
        response = {"error": "Ocurrió un error en el servidor"}
        await websocket.send(json.dumps(response))

# Función principal para iniciar el servidor
async def main():
    server = await websockets.serve(handler, "localhost", 12345)
    print("Servidor iniciado en ws://localhost:12345")
    await server.wait_closed()

# Iniciar el servidor
asyncio.run(main())
