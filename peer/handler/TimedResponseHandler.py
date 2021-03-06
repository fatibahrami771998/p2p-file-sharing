#!/usr/bin/env python

import socket
from utils import net_utils, shell_colors as shell
from common.HandlerInterface import HandlerInterface
from peer.LocalData import LocalData


class TimedResponseHandler(HandlerInterface):

	def serve(self, sd: socket.socket) -> None:
		""" Handle the peer request

		:param sd: the socket descriptor used for read the request
		:return None
		"""

		try:
			response = sd.recv(300).decode()
		except socket.error as e:
			shell.print_red(f'Unable to read the response from the socket: {e}\n')
			sd.close()
			return
		sd.close()

		command = response[0:4]

		if command == "ASUP":

			if len(response) != 80:
				shell.print_red(f"Invalid response: : {command} -> {response}. Expected: ASUP<pkt_id><ip_peer><port_peer>")
				return

			pktid = response[4:20]
			ip4_peer = response[20:75]
			port_peer = int(response[75:80])

			if pktid != LocalData.get_sent_packet():
				return

			LocalData.add_superpeer_candidate(ip4_peer, port_peer)

		else:
			shell.print_red(f"\nInvalid response: {command} -> {response}\n")

		return
