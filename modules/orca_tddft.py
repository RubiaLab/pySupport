import os
import sys

def tddft_analyzer(filename):
	
	file = os.path.basename(filename)

	with open(filename) as output:
		calc_output = output.readlines()

	#Check normal termination
	normal_termination = any('****ORCA TERMINATED NORMALLY****' in line for line in calc_output)
	if normal_termination:
		print(f'Calculation in file {file} terminated normally – continuing ...')
	else:
		print(f'Warning: Calculation in file {file} did not terminate normally. Exiting the program ...')
		sys.exit()

	jobtype = 'tddft'

	homo_number = int(calc_output[p-1].split()[0])
	lumo_number = int(calc_output[p].split()[0])
	print('HOMO Number:', homo_number)
	print('LUMO Number:',lumo_number)

	for q in range(p, len(calc_output)):
		if 'TD-DFT/TDA EXCITED STATES (SINGLETS)' in calc_output[q]:							#fragt aktuell erste TDDFT ab
			break
	tddft_section_start = q + 5

	for r in range(tddft_section_start, len(calc_output)):
		if 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS' in calc_output[r]:
			break
	states_section_start = r + 5

	states = []
	energies = []
	f_osc = []
	for s in range(states_section_start, states_section_start+10):								#hier noch den richtigen Wert anpassen
		states.append(int(calc_output[s].strip().split()[0]))
		energies.append(float(calc_output[s].strip().split()[2]))
		f_osc.append(format(float(calc_output[s].strip().split()[3]), '.2f'))

	print('States:', states)
	print('TDDFT Energies [nm]:', energies)
	print('f_osc:', f_osc)
