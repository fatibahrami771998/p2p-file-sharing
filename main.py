#!/usr/bin/env python

import os
from utils import net_utils, shell_colors as shell
from superpeer import superpeer
from peer import peer


if __name__ == '__main__':
	if not os.path.exists('shared'):
		os.mkdir('shared')

	net_utils.prompt_parameters_request()

	choice = ''
	while choice != 'q':
		choice = input('Are you a super peer? (y/n): ')
		if choice == 'y':
			superpeer.startup()
			break
		elif choice == 'n':
			peer.startup()
			break
		else:
			shell.print_red('Input code is wrong. Choose y or n!\n')
