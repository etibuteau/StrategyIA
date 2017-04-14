# Under MIT License, see LICENSE.txt
"""
    Regroupe les services utilisant l'UDP pour la communication. Ceux-ci
    permettent l'envoie et la réceptions de paquets pour le débogage, ainsi que
    l'envoie des commandes aux robots au niveau des systèmes embarqués.
"""

from queue import Queue
from socketserver import BaseRequestHandler

from RULEngine.Communication.protobuf import messages_robocup_ssl_wrapper_pb2
from RULEngine.Communication.util.threaded_udp_server import ThreadedUDPServer


class ProtobufPacketReceiver(object):
    """
        Service qui implémente un serveur multicast UDP avec comme type de
        paquets ceux défini par la SSL en utilisant protobuf. Le serveur est
        async.
    """

    def __init__(self, host, port, packet_type):
        self.packet_queue = Queue(maxsize=100)
        handler = self.get_udp_handler(self.packet_queue, packet_type)
        self.server = ThreadedUDPServer(host, port, handler)

    def get_udp_handler(self, packet_queue, packet_type):
        class ThreadedUDPRequestHandler(BaseRequestHandler):

            def handle(self):
                data = self.request[0]
                packet = packet_type()
                packet.ParseFromString(data)
                packet_queue.put(packet)

        return ThreadedUDPRequestHandler

    # TODO change the typing here in case of refereeMGL 2017/02/24
    def pop_frames(self)->messages_robocup_ssl_wrapper_pb2:
        """ Retourne une frame de la deque. """
        packet_list = []
        while not self.packet_queue.empty():
            packet_list.append(self.packet_queue.get())
        packet_list.reverse()
        return packet_list

    # TODO change the typing here in case of referee MGL 2017/02/24
    def get_latest_frame(self)->messages_robocup_ssl_wrapper_pb2:
        """ Retourne sans erreur la dernière frame reçu. """
        last_frame = None
        while not self.packet_queue.empty():
            last_frame = self.packet_queue.get()
        return last_frame


