"""
get_spd.py
vygenerovať ponuku (offer) SDP (Session Description Protocol) pomocou aiortc.
SDP popisuje technické detaily spojenia.
(podporované kodeky, IP adresy kandidátov atď.).
"""
# aiortc je knižnica pre WebRTC ziskavanie ICE/SPD.
from aiortc import RTCIceCandidate, RTCIceGatherer, RTCIceTransport