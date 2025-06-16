#!/usr/bin/env python3
"""
FastAPI aplikácia pre Tor hidden service.
"""
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import uvicorn
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate

# Importuj pomocné funkcie z webrtc_utils.py
# Predpokladám, že webrtc_utils.py je v rovnakom adresári
from webrtc_utils import create_offer  # Upravený import

app = FastAPI(
    title="Tor Hidden Service API",
    description="API pre Tor hidden service, nasadená na porte 5000.",
    version="1.0.0"
)

# Globálny slovník pre ukladanie WebSocket spojení
# Kľúčom bude ID klienta (napríklad), hodnotou bude WebSocket
connected_clients: dict = {}


@app.get("/", response_class=JSONResponse)
def read_root():
    """
    Root endpoint.

    Returns:
        JSONResponse: Vítacia správa.
    """
    return {"message": "Ahoj z Tor hidden service!"}


@app.get("/health", response_class=JSONResponse)
def health_check():
    """
    Health check endpoint.

    Returns:
        JSONResponse: Stavová správa.
    """
    return {"status": "ok"}


@app.websocket("/webrtc/sdp/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint pre WebRTC signalizáciu.

    Args:
        websocket (WebSocket): WebSocket spojenie.
        client_id (str): Jednoznačný identifikátor klienta.
    """
    await websocket.accept()
    connected_clients[client_id] = websocket  # Uloženie WebSocket spojenia
    print(f"Klient {client_id} sa pripojil na /webrtc/sdp.")

    try:
        # Vytvorenie ponuky na pripojenie
        peer_connection = RTCPeerConnection()

        async def send_offer_to_client(pc: RTCPeerConnection, offer: RTCSessionDescription):
            """Odoslanie SDP ponuky klientovi."""
            try:
                await websocket.send_json({
                    "type": "offer",
                    "sdp": offer.sdp
                })
            except Exception as e:
                print(f"Error pri odosielani offeru {e}")

        pc, offer = await create_offer(send_offer_to_client) # Pass the send offer

        # Store the RTCPeerConnection
        websocket.pc = peer_connection

        # Send offer to the client
        # await websocket.send_json({"type": "offer", "sdp": offer.sdp}) # Send initial offer

        while True:
            message = await websocket.receive_json()
            if message["type"] == "answer":
                answer = RTCSessionDescription(sdp=message["sdp"], type="answer")
                await websocket.pc.setRemoteDescription(answer)
                print("Answer from client was set as remote description")

            elif message["type"] == "ice_candidate":
                    candidate = RTCIceCandidate(
                        sdpMid=message["sdpMid"],
                        sdpMLineIndex=message["sdpMLineIndex"],
                        candidate=message["candidate"],
                    )
                    await websocket.pc.addIceCandidate(candidate)
            else:
                print(f"Unknown message type {message['type']}")

    except WebSocketDisconnect:
        # Odpojenie klienta
        print(f"Klient {client_id} sa odpojil.")
        del connected_clients[client_id]  # Odstránenie WebSocket spojenia
    except Exception as e:
        # Chyba pri spracovaní správy
        print(f"Chyba pri spracovaní správy od {client_id}: {e}")
        await websocket.send_json({"error": f"Chyba: {e}"})
    finally:
        if client_id in connected_clients:
            del connected_clients[client_id]


if __name__ == "__main__":
    # Spustenie aplikácie na porte 5000
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )
