#!/usr/bin/env python

from utils import net_utils, Logger, shell_colors as shell
from .LocalData import LocalData
from common.ServerThread import ServerThread
from .handler import NetworkHandler, MenuHandler, TimedResponseHandler
from utils.SpinnerThread import SpinnerThread
from .Menu import Menu
import uuid
from threading import Timer
import random
import socket


def startup():

	while True:
		# verifico se ho superpeer e file in sharing nel json (ossia se il peer è crashato)
		if LocalData.superpeer_is_empty():
			while True:
				shell.print_blue('\nThis process will allow you to add your known peer.\n')
				superpeer = net_utils.prompt_friend_request()
				LocalData.set_superpeer(superpeer)

				# 1) Lancia una SUPE al nodo conosciuto
				pktid = str(uuid.uuid4().hex[:16].upper())
				ip = net_utils.get_local_ip_for_response()
				port = str(net_utils.get_network_port()).zfill(5)
				ttl = '04'
				packet = 'SUPE' + pktid + ip + port + ttl

				super_ip4 = LocalData.get_superpeer_ip4()
				super_port = LocalData.get_superpeer_port()

				LocalData.set_sent_packet(pktid)

				server = ServerThread(net_utils.get_network_port(), TimedResponseHandler.TimedResponseHandler())
				server.start()

				spinner = SpinnerThread('Trying to login', '')
				spinner.start()

				try:
					net_utils.send_packet_and_close(super_ip4, super_port, packet)
				except socket.error as e:
					shell.print_red(f'There was an error in the login process: {e}')
					continue

				# 2) Attende ASUP per 20 sec
				timer = Timer(20, lambda: (server.stop(), spinner.stop()))
				timer.start()

				timer.join()
				spinner.join()


				# 3) Se non è possibile agganciarsi ad un super, devo far reinserire il peer all'utente
				if len(LocalData.get_superpeer_candidates()) == 0:
					shell.print_red('Cannot contact a superpeer from the peer you provide, please retry.')
					continue

				# 3) Se il peer aggiunto era veramente un superpeer, allora non lo cambio
				elif LocalData.get_superpeer() in LocalData.get_superpeer_candidates():
					break

				# 3) Se invece era un superpeer falso, pesco un super a random dalla lista dei candidati
				else:
					index = random.randint(0, len(LocalData.get_superpeer_candidates()) -1)
					superpeer = LocalData.get_superpeer_candidate_by_index(index)
					LocalData.set_superpeer(superpeer)
					break

		# Lancio una LOGI al superpeer scelto
		ip = net_utils.get_local_ip_for_response()
		port = str(net_utils.get_network_port()).zfill(5)
		packet = "LOGI" + ip + port

		super_ip4 = LocalData.get_superpeer_ip4()
		super_port = LocalData.get_superpeer_port()

		try:
			sock = net_utils.send_packet(super_ip4, super_port, packet)
			response = sock.recv(100).decode()

			if len(response) != 20:
				shell.print_red(f'There was an error in the login process: unexpected: {response}.\nPlease retry.')
				LocalData.clear_backup_data()
				continue

			session_id = response[4:20]

			if session_id == '0' * 16:
				shell.print_red(f'There was an error in the login process: unexpected session_id: {session_id}.\nPlease retry.')
				LocalData.clear_backup_data()
				continue

			LocalData.session_id = response[4:20]
			break
		except (socket.error, AttributeError):
			shell.print_yellow(f'Unable to contact {super_ip4} [{super_port}]')
			# pulisco il file json da file in sharing e superpeer vecchio
			LocalData.clear_backup_data()
			if sock is not None:
				sock.close()
			continue

	shell.print_green(f'Successfully logged to the superpeer: {super_ip4} [{super_port}]\n')

	log = Logger.Logger('peer/peer.log')

	server = ServerThread(net_utils.get_network_port(), NetworkHandler.NetworkHandler(log))
	server.daemon = True
	server.start()

	Menu(MenuHandler.MenuHandler()).show()
