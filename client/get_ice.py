"""
get_ice.py
WebRTC vyžaduje, aby si peer-to-peer uzly našli spoločnú cestu,
cez rôzne sieťové prekážky (NAT, firewally).
Na to slúži ICE (Interactive Connectivity Establishment).
"""
# aiortc je knižnica pre WebRTC ziskavanie ICE/SPD.
from aiortc import RTCIceCandidate, RTCIceGatherer, RTCIceTransport

