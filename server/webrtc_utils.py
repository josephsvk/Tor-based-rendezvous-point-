from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
import asyncio


async def create_offer(send_offer):
    """Vytvorenie ponuky.

    Returns:
        pc: _description_
        offer: _description_
    """
    pc = RTCPeerConnection()
    
    channel = pc.createDataChannel("chat")

    # vytvorenie ponuky
    offer = await pc.createOffer()

    # Nastavenie lokálnej ponuky
    await pc.setLocalDescription(offer)

    # zavoláme callback z FastAPI, aby to poslal klientovi
    await send_offer(pc, offer)
    
    print("SPD ponuka:")
    print(pc.localDescription.sdp)
    print("Typ SPD:", pc.localDescription.type)

    # Tu by si mal odoslať 'offer' Používateľovi B cez signalizačný mechanizmus (napr. FastAPI)

    # Neskôr budeš potrebovať spracovať odpoveď (answer) od Používateľa B
    # await pc.setRemoteDescription(answer)

    return pc, offer


async def main():

    peer_connection, offer_sdp = await create_offer()


if __name__ == "__main__":
    asyncio.run(main())
