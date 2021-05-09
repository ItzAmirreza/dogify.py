from asyncio.tasks import Task
import logging
import sys
import json
import asyncio
from typing import List, Optional, Dict, Any, TypeVar
from asyncio.futures import Future

from pymediasoup.device import Device
from pymediasoup.handlers.aiortc_handler import AiortcHandler
from pymediasoup.models.transport import DtlsParameters
from pymediasoup.rtp_parameters import RtpParameters
from pymediasoup.transport import Transport
from pymediasoup.consumer import Consumer
from pymediasoup.producer import Producer
from pymediasoup.data_consumer import DataConsumer
from pymediasoup.data_producer import DataProducer

from aiortc.mediastreams import AudioStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaBlackhole, MediaRecorder

from random import random

T = TypeVar("T")
# logging.basicConfig(level=logging.INFO)

# logger = logging.getLogger('pymediasoup')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(
#     filename='pymediasoup.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter(
#     '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)


class AudioConnection:
    def __init__(self, handlers, recorder=MediaBlackhole()):
        self._player = MediaPlayer(
            'http://download.tsi.telecom-paristech.fr/'
            'gpac/dataset/dash/uhd/mux_sources/hevcds_720p30_2M.mp4')
        # self._player = None
        self._recorder: MediaRecorder = recorder
        self._handlers = handlers
        # Save answers temporarily
        self._answers: Dict[str, Future] = {}
        self._device = None

        self._tracks = []

        if self._player and self._player.audio:
            audioTrack = self._player.audio
        else:
            audioTrack = AudioStreamTrack()
        # audioTrack = self._player

        self._audioTrack = audioTrack
        self._tracks.append(audioTrack)

        self._sendTransport: Optional[Transport] = None
        self._recvTransport: Optional[Transport] = None

        self._producers: List[Producer] = []
        self._consumers: List[Consumer] = []
        self._tasks: List[Task] = []
        self._closed = False

        # await self.load()
        # await self.createSendTransport()
        # await self.createRecvTransport()
        # await self.produce()

    async def init(self, data):
        # Init device
        self._device = Device(
            handlerFactory=AiortcHandler.createFactory(tracks=self._tracks))

        # Load Router RtpCapabilities
        await self._device.load(data['routerRtpCapabilities'])
        self.loop = asyncio.get_running_loop()

        if 'sendTransportOptions' in data:
            await self.createSendTransport(data['sendTransportOptions'])
        if 'recvTransportOptions' in data:
            await self.createRecvTransport(data['recvTransportOptions'])

        await self.produce()

    async def createSendTransport(self, data):
        # Create sendTransport
        self._sendTransport = self._device.createSendTransport(
            id=data['id'],
            iceParameters=data['iceParameters'],
            iceCandidates=data['iceCandidates'],
            dtlsParameters=data['dtlsParameters'],
            sctpParameters=None
        )

        @ self._sendTransport.on('connect')
        async def on_connect(dtlsParameters: DtlsParameters):

            await self._handlers['connect-transport']({
                "direction": "send",
                "dtlsParameters": {
                    'role': dtlsParameters.role,
                    'fingerprints': [{"algorithm": fingerprint.algorithm, "value": fingerprint.value} for fingerprint in dtlsParameters.fingerprints]
                },
                "transportId": self._sendTransport.id
            })

        @self._sendTransport.on('produce')
        async def on_produce(kind: str, rtpParameters: RtpParameters, appData: dict):
            rtpCapabilities = {
                "codecs": [{
                    "channels": codec.channels,
                    "clockRate": codec.clockRate,
                    "kind": codec.kind,
                    "mimeType": codec.mimeType,
                    "parameters": codec.parameters,
                    "preferredPayloadType": codec.preferredPayloadType,
                    "rtcpFeedback": [{
                        "type": feedBack.type,
                        "parameter": feedBack.parameter
                    } for feedBack in codec.rtcpFeedback]

                } for codec in self._device.rtpCapabilities.codecs],
                "headerExtensions": [{
                    "direction": headerExtension.direction,
                    "kind": headerExtension.kind,
                    "preferredEncrypt": headerExtension.preferredEncrypt,
                    "preferredId": headerExtension.preferredId,
                    "uri": headerExtension.uri
                } for headerExtension in self._device.rtpCapabilities.headerExtensions],
                "fecMechanisms": self._device.rtpCapabilities.fecMechanisms
            }
            RtpParameters = {
                "codecs": [{
                    "channels": codec.channels,
                    "clockRate": codec.clockRate,
                    "mimeType": codec.mimeType,
                    "parameters": codec.parameters,
                    "payloadType": codec.payloadType,
                    "rtcpFeedback": [{
                        "type": feedBack.type,
                        "parameter": feedBack.parameter
                    } for feedBack in codec.rtcpFeedback]

                } for codec in rtpParameters.codecs],
                "encodings": [{
                    "ssrc": encoding.ssrc,
                    "rid": encoding.rid,
                    "codecPayloadType": encoding.codecPayloadType,
                    "dtx": encoding.dtx,
                    "scalabilityMode": encoding.scalabilityMode,
                    "scaleResolutionDownBy": encoding.scaleResolutionDownBy,
                    "maxBitrate": encoding.maxBitrate,
                    "maxFramerate": encoding.maxFramerate,
                    "adaptivePtime": encoding.adaptivePtime,
                    "priority": encoding.priority,
                    "networkPriority": encoding.networkPriority

                } for encoding in rtpParameters.encodings],
                "headerExtensions": [{
                    "encrypt": headerExtension.encrypt,
                    "id": headerExtension.id,
                    "uri": headerExtension.uri,
                    "parameters": headerExtension.parameters
                } for headerExtension in rtpParameters.headerExtensions],
                "mid": rtpParameters.mid,
                "rtcp": {
                    "cname": rtpParameters.rtcp.cname,
                    "reducedSize": rtpParameters.rtcp.reducedSize,
                    "mux": rtpParameters.rtcp.mux
                }
            }
            res = await self._handlers['tracks']('send', {
                "appData": appData,
                "direction": "send",
                "kind": kind,
                "paused": False,
                "rtpCapabilities": rtpCapabilities,
                "rtpParameters": RtpParameters,
                "transportId": self._sendTransport.id
            })
            return res['d']['id']

    async def produce(self):
        if self._sendTransport == None:
            await self.createSendTransport()
        audioProducer: Producer = await self._sendTransport.produce(
            self._audioTrack,
            stopTracks=False,
            appData={}
        )
        self._producers.append(audioProducer)

    async def createRecvTransport(self, data):
        if self._recvTransport != None:
            return
        # Create recvTransport
        self._recvTransport = self._device.createRecvTransport(
            id=data['id'],
            iceParameters=data['iceParameters'],
            iceCandidates=data['iceCandidates'],
            dtlsParameters=data['dtlsParameters'],
        )

        @ self._recvTransport.on('connect')
        async def on_connect(dtlsParameters):
            await self._handlers['connect-transport']({
                "direction": "recv",
                "dtlsParameters": {
                    'role': dtlsParameters.role,
                    'fingerprints': [{"algorithm": fingerprint.algorithm, "value": fingerprint.value} for fingerprint in dtlsParameters.fingerprints]
                },
                "transportId": self._recvTransport.id
            })

        rtpCapabilities = {
            "codecs": [{
                "channels": codec.channels,
                "clockRate": codec.clockRate,
                "kind": codec.kind,
                "mimeType": codec.mimeType,
                "parameters": codec.parameters,
                "preferredPayloadType": codec.preferredPayloadType,
                "rtcpFeedback": [{
                    "type": feedBack.type,
                    "parameter": feedBack.parameter
                } for feedBack in codec.rtcpFeedback]

            } for codec in self._device.rtpCapabilities.codecs],
            "headerExtensions": [{
                "direction": headerExtension.direction,
                "kind": headerExtension.kind,
                "preferredEncrypt": headerExtension.preferredEncrypt,
                "preferredId": headerExtension.preferredId,
                "uri": headerExtension.uri
            } for headerExtension in self._device.rtpCapabilities.headerExtensions],
            "fecMechanisms": self._device.rtpCapabilities.fecMechanisms
        }
        await self._handlers['tracks']('recv', {"rtpCapabilities": rtpCapabilities})

    async def consumeArr(self, data):
        for consumer in data["consumerParametersArr"]:
            consumer_data = consumer['consumerParameters']

            id = consumer_data['id']
            producerId = consumer_data["producerId"]
            kind = consumer_data['kind']
            rtpParameters = consumer_data["rtpParameters"]
            await self.consume(id, producerId, kind, rtpParameters)

    async def consume(self, id, producerId, kind, rtpParameters):
        if self._recvTransport == None:
            await self.createRecvTransport()
        consumer: Consumer = await self._recvTransport.consume(
            id=id,
            producerId=producerId,
            kind=kind,
            rtpParameters=rtpParameters
        )
        self._consumers.append(consumer)
        self._recorder.addTrack(consumer.track)
        await self._recorder.start()

    async def close(self):
        for consumer in self._consumers:
            await consumer.close()
        for producer in self._producers:
            await producer.close()
        for task in self._tasks:
            task.cancel()
        if self._sendTransport:
            await self._sendTransport.close()
        if self._recvTransport:
            await self._recvTransport.close()
        await self._recorder.stop()
