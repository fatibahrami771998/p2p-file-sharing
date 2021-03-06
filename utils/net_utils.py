#!/usr/bin/env python

import re
import ipaddress
import socket
import random
from peer.LocalData import LocalData
from utils import shell_colors

config = {
	'ipv4': '172.16.1.1',
	'ipv6': 'fc00::1:1',
	'network_port': 3000,
	'aque_port': 4000,
	'asup_port': 5000
}


def create_socket() -> socket.socket:
	""" Create the active socket

		:return: the active socket
	"""
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# sock.settimeout(2)

	return sock


def send_packet(ip4_peer: str, port_peer: int, packet: str) -> socket.socket:
	""" Send the packet to the specified host

		:param ip4_peer: host's ipv4 address
		:param port_peer: host's port
		:param packet: packet to be sent
		:return: None
	"""
	try:
		sock = create_socket()

		sock.connect((ip4_peer, port_peer))

		sock.send(packet.encode())

	except socket.error:
		sock = None

	return sock


def send_packet_and_close(ip4_peer: str, port_peer: int, packet: str) -> None:
	""" Send the packet to the specified host

		:param ip4_peer: host's ipv4 address
		:param port_peer: host's port
		:param packet: packet to be sent
		:return: None
	"""
	sock = create_socket()

	sock.connect((ip4_peer, port_peer))

	sock.send(packet.encode())
	sock.close()

	# self.log.write(f'{packet}')


# TODO:fateme
# def get_ip_pair(ip_string: str) -> tuple:
# 	"""
# 	:param ip_string: the ip address
# 	:return: ipv4
# 	"""
# 	ip_v4 = re.sub('\.[0]{1,2}', '.', ip_string[:15])
# 	ip_v6 = ipaddress.IPv6Address(ip_string[16:]).compressed
# 	return ip_v4, ip_v6


def get_local_ip_for_response() -> str:
	ipv4 = config['ipv4'].split('.')[0].zfill(3)
	for i in range(1, 4):
		ipv4 = ipv4 + '.' + config['ipv4'].split('.')[i].zfill(3)
	return ipv4


def get_local_ipv4() -> str:
	return config['ipv4']


def set_local_ipv4(ipv4: str) -> str:
	config['ipv4'] = ipv4


def get_network_port() -> int:
	return config['network_port']


def get_aque_port() -> int:
	return config['aque_port']


def get_asup_port() -> int:
	return config['asup_port']


def prompt_parameters_request() -> None:
	""" Guide the user to insert his local ip adress and port in case there are not/they are wrong

	:return: None
	"""
	if config['ipv4'] == '':
		shell_colors.print_blue('\nYou need to add your own network configuration to get started.\n')

	while True:
		if get_local_ipv4() == '':
			ip4 = input('Insert your local IPv4 address: ')
			try:
				ipaddress.IPv4Address(ip4)
			except ipaddress.AddressValueError:
				shell_colors.print_red(f'\n{ip4} is not a valid IPv4 address, please retry.\n')
				continue
			set_local_ipv4(ip4)
			break
		else:
			try:
				print("\n\nddddddddddddddddddddddddddddddddddddddddddddddddddd\n\n")
				ipaddress.IPv4Address(get_local_ipv4())
				print(get_local_ipv4())
				break
			except ipaddress.AddressValueError:
				print("\n\naaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n\n")
				shell_colors.print_red(f'\n{get_local_ipv4()} is not a valid IPv4 address, please reinsert it.\n')
				set_local_ipv4('')
				continue


def prompt_friend_request() -> tuple:
	""" Guide the user to manually insert peers in the data structure

	:return: None
	"""

	while True:
		ip4 = input('Insert a known peer (IPv4): ')
		if ip4 == 'q':
			break

		try:
			ipaddress.IPv4Address(ip4)
		except ipaddress.AddressValueError:
			shell_colors.print_red(f'{ip4} is not a valid IPv4 address, please retry.')
			continue
		break

	while True:
		port = input('Insert a known peer (port): ')
		try:
			port = int(port)
			if not 1024 < port < 65535:
				shell_colors.print_red(f'{port} must be in range 1025 - 65535')
				continue
		except ValueError:
			shell_colors.print_red(f'{port} is not a valid port number, please retry.')
			continue
		break

	return ip4, port
