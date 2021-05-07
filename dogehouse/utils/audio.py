import asyncio, os,traceback,logging
from typing import List
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling
from aiortc.contrib.media import MediaPlayer
from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCDtlsParameters,
    RTCDtlsFingerprint,
    RTCDtlsTransport,
    RTCIceTransport,
    RTCRtpReceiver,
    RTCRtpCodecParameters,
    RTCIceParameters,
    RTCConfiguration,
    RTCRtpParameters,
    RTCRtpTransceiver,
    RTCIceGatherer,
    RTCCertificate,
    RTCIceServer
)
from aiortc.contrib.media import MediaPlayer
from aiortc.rtcrtpsender import RTCRtpSender
from aiortc.rtcrtpparameters import RTCRtcpFeedback,RTCRtpHeaderExtensionParameters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('aiortc')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='aiortc.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class AudioConnection:
    def __init__(self,data):
        self._data = data

    async def getFromObj(self,origin,item):
        if item in origin:
            return origin[item]
        return None


    async def init(self):
        self.ice_servers = RTCIceServer("stun:stun.l.google.com:19302")

        self.peer_connection = RTCPeerConnection(RTCConfiguration([self.ice_servers]))
        self.player = MediaPlayer(
            'http://download.tsi.telecom-paristech.fr/'
            'gpac/dataset/dash/uhd/mux_sources/hevcds_720p30_2M.mp4')

        
    async def add_candidates(self,transport:RTCIceTransport, type: str):
        for ice_candidate_data in self._data[type]['iceCandidates']:
            foundation = ice_candidate_data['foundation']
            ip = ice_candidate_data['ip']
            port = ice_candidate_data['port']
            priority = ice_candidate_data['priority']
            protocol = ice_candidate_data['protocol']
            type = ice_candidate_data['type']
            tcpType = await self.getFromObj(ice_candidate_data,'tcpType')

            ice_candidate = RTCIceCandidate(1,foundation,ip,port,priority,protocol,type,tcpType=tcpType)
            await transport.addRemoteCandidate(ice_candidate)
        await transport.addRemoteCandidate(None)
            


    async def get_dtls_transport(self,type):
        ice_gatherer = RTCIceGatherer([self.ice_servers])
        await ice_gatherer.gather()
        ice_transport = RTCIceTransport(ice_gatherer)
        await self.add_candidates(ice_transport,type)

        ice_parameters = await self.get_ice_parameters(type)
        await ice_transport.start(ice_parameters)

        rtc_certificate = RTCCertificate.generateCertificate()
        dtls_transport = RTCDtlsTransport(ice_transport,[rtc_certificate])

        dtls_parameters = await self.get_dtls_parameters(type)
        print('Connecting!')
        await dtls_transport.start(dtls_parameters)
        print('Connected!')

        return dtls_transport

    async def get_dtls_fingerprints(self,list):
        fingerprints = []
        for fingerprint_data in list:
            algorithm =  fingerprint_data['algorithm']
            value = fingerprint_data['value']
            fingerprints.append(RTCDtlsFingerprint(algorithm,value))
        return fingerprints
            
    async def get_dtls_parameters(self,type):
        dtls_parameters_data = self._data[type]['dtlsParameters']
        fingerprints_data = dtls_parameters_data['fingerprints']

        fingerprints = await self.get_dtls_fingerprints(fingerprints_data)
        role = dtls_parameters_data['role']

        return RTCDtlsParameters(fingerprints,role)


    async def get_ice_parameters(self,type):
        ice_parameters_data = self._data[type]['iceParameters']
        usernameFragment= ice_parameters_data['usernameFragment']
        password= ice_parameters_data['password']
        ice_lite = ice_parameters_data['iceLite']
        ice_parameters = RTCIceParameters(usernameFragment,password,ice_lite)
        return ice_parameters
            # await self.peer_connection.addIceCandidate(ice_candidate)

    async def get_codecs(self,data):
        codecs:List[RTCRtpCodecParameters] = []
        for codec_data in data:
            mime_type = codec_data['mimeType']
            clock_rate = codec_data['clockRate']
            channels = codec_data['channels']
            payload_type = codec_data['preferredPayloadType']
            rtcp_feedbacks = []
            for rtcp_feedback_data in codec_data['rtcpFeedback']:
                type = rtcp_feedback_data['type']
                parameter = rtcp_feedback_data['parameter'] if rtcp_feedback_data['parameter'] else None
                rtcp_feedback = RTCRtcpFeedback(type,parameter)
                rtcp_feedbacks.append(rtcp_feedback)
            parameters = codec_data['parameters']

            codec = RTCRtpCodecParameters(mime_type,clock_rate,channels,payload_type,rtcp_feedbacks,parameters)
            codecs.append()
        return codecs
            
    async def get_header_extensions(self,data):
        header_extensions: List[RTCRtpHeaderExtensionParameters] = []
        for header_extension_data in data:
            id = header_extension_data["preferredId"]
            uri = header_extension_data['uri']
            header_extension = RTCRtpHeaderExtensionParameters(id,uri)
            header_extensions.append(header_extension)
        return header_extensions

    async def get_rtp_parameters(self,type):
        rtp_parameters_data = self._data[type]['routerRtpCapabilities']
        
        codecs = await self.get_codecs(rtp_parameters_data['codecs'])
        header_extensions = await self.get_header_extensions(rtp_parameters_data['headerExtensions'])

        return RTCRtpParameters(codecs,header_extensions)

    async def get_receiver(self):
        type = 'recvTransportOptions'
        transport = await self.get_dtls_transport(type)
        receiver = RTCRtpReceiver('audio',transport)

        rtp_receiver_parameters = await self.get_rtp_parameters(type)
        await receiver.receive(rtp_receiver_parameters)

        return receiver

    async def get_sender(self):
        type = 'sendTransportOptions'
        transport = await self.get_dtls_transport(type)
        sender = RTCRtpSender('audio',transport)

        rtp_sender_parameters = await self.get_rtp_parameters
        await sender.send(rtp_sender_parameters)

        return sender

    async def get_transceiver(self):
        receiver = await self.get_receiver()
        sender = await self.get_sender()
        return RTCRtpTransceiver('audio',receiver,sender)

    async def run(self):
        try:
            logger.debug("connecting:")
            transceiver = await self.get_transceiver()
            self.peer_connection.__transceivers.append(transceiver)
            logger.debug(self.peer_connection.createAnswer())
        except Exception as e:
            print(e)
            
        # # self.signaling = create_signaling()
        # self.player = MediaPlayer()
        # self.peer_connection.addTransceiver('audio')

                

        # await self.signaling.connect()

        # if self.role == "offer":
        # self.sender = self.peer_connection.addTrack(self.player.audio)
        # await self.peer_connection.setLocalDescription(await self.peer_connection.createOffer())
        # # await self.signaling.send(self.peer_connection.localDescription)

        # while True:
        #     obj = await self.signaling.receive()

            # if isinstance(obj, RTCSessionDescription):
            #     await self.peer_connection.setRemoteDescription(obj)

            #     if obj.type == "offer":
            #         # send answer
            #         add_tracks()
            #         await self.peer_connection.setLocalDescription(await self.peer_connection.createAnswer())
            #         await self.signaling.send(self.peer_connection.localDescription)
            # elif isinstance(obj, RTCIceCandidate):
            #     await self.peer_connection.addIceCandidate(obj)
            # elif obj is BYE:
            #     print("Exiting")
            #     break