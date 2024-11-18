import asyncio
import websockets
import json

# Función manejadora para cada conexión
async def handler(websocket):
    print("Nueva conexión establecida")
    try:
        async for message in websocket:
            print(f"Mensaje recibido: {message}")
            
            try:
                # Intenta parsear el mensaje como JSON
                move = json.loads(message)
                print(f"Movimiento procesado: {move}")
                
                # Procesa el mensaje dependiendo de su tipo
                if move["type"] == "movimiento":
                    # Procesa el movimiento y extrae las coordenadas
                    origen = move["origen"]
                    destino = move["destino"]
                    pieza = move["pieza"]
                    color = move["color"]
                    
                    # Aquí puedes realizar validaciones de movimiento, etc.
                    # Responder con la misma información o hacer algo con ella
                    response = {
                        "type": "movimiento",
                        "origen": origen,
                        "destino": destino,
                        "pieza": pieza,
                        "color": color
                    }
                    
                elif move["type"] == "jaque":
                    # Si es un mensaje de jaque, procesarlo de otra manera
                    response = {
                        "type": "jaque",
                        "color": move["color"],
                        "status": move["status"]
                    }
                else:
                    response = {"error": "Tipo de mensaje no reconocido"}
                
            except json.JSONDecodeError:
                # Si el mensaje no es un JSON válido, responde con un error
                response = {"error": "Mensaje no es JSON válido"}
            
            # Enviar la respuesta al cliente
            await websocket.send(json.dumps(response))
            print(f"Respuesta enviada: {response}")
            
    except websockets.ConnectionClosed:
        print("Conexión cerrada por el cliente")
    except Exception as e:
        # En caso de cualquier otro error
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
