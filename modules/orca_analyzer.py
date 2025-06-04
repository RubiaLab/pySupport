import os
import sys

def analyzer(filename):
	
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
	
	coords = []
	freqs = []
	imaginary_freqs = []
	states = []
	energies = []
	f_osc = []
	wavelengths = []
	orbitals = []
	orbitals_alpha = []
	orbitals_beta = []
	state_blocks = []
	is_closed = True
	beta_marker = False

	#Determine input section
	for i in range(len(calc_output)):
		if 'INPUT FILE' in calc_output[i]:
			input_section_start = i+1
		if '****END OF INPUT****' in calc_output[i]:
			input_section_end = i+1
			break

	for j, line in enumerate(calc_output):

		#Determine job type
		jobtype = 'other'
		opt_found = False
		for k in range(input_section_start, input_section_end):
			if 'opt'.casefold() in calc_output[k].casefold():
				jobtype = 'opt'
				opt_found = True
			elif 'freq'.casefold() in calc_output[k].casefold():
				if opt_found:
					jobtype = 'opt+freq'
				else:
					jobtype = 'freq'
			elif '%tddft'.casefold() in calc_output[k].casefold():
				jobtype = 'tddft'

		#Determine basis set
		if 'Your calculation utilizes the basis:' in line:
			basis_set = line.split()[5]

		#Determine charge
		if 'Total Charge' in line:
			charge = line.split()[4]

		#Determine multiplicity
		if 'Multiplicity           Mult' in line:
			multiplicity = line.split()[3]
			if int(multiplicity) > 1:
				is_closed = False

		#Determine total energy
		if 'FINAL SINGLE POINT ENERGY' in line:
			total_energy = line.split()[4]

		#Determine coordinates ORCA
		if '*** FINAL ENERGY EVALUATION AT THE STATIONARY POINT ***' in line:
			l = j + 6
			while l < len(calc_output):  
				if '------' in calc_output[l]:
					break
				coords.append(calc_output[l].strip())  
				l += 1
			coords.pop()  #removes empty line after coordinates

	#Determine frequencies
	if jobtype == 'freq' or jobtype == 'opt+freq':
		for m in range(len(calc_output)):
			if 'VIBRATIONAL FREQUENCIES' in calc_output[m]:
				break
		freq_start = m + 6

		for n in range(freq_start, len(calc_output)):
			if '---------' in calc_output[n]:
				break
		freq_end = n - 2

		for freq_line in range(freq_start, freq_end):
			if float(calc_output[freq_line].split()[1]) != 0:
				freqs.append(calc_output[freq_line].split()[1])
			if float(calc_output[freq_line].split()[1]) < 0:
				imaginary_freqs.append(calc_output[freq_line].split()[1])

	#Orbitals section
	if jobtype == 'opt' or jobtype == 'tddft':
		for o in range(len(calc_output)):
			if 'ORBITAL ENERGIES' in calc_output[o]:
				orbital_energies_start = o + 4

		for p in range(orbital_energies_start, len(calc_output)):
			if '*' in calc_output[p]:
				break
			if is_closed:
				orbitals.append(calc_output[p].split())
			if is_closed == False:
				if all(not item.strip() for item in calc_output[p]):
					beta_marker = True
				if beta_marker == False:
					orbitals_alpha.append(calc_output[p].split())
				if beta_marker == True:
					orbitals_beta.append(calc_output[p].split())

		if is_closed:
			for q in range(len(orbitals)):
				if float(orbitals[q][1]) == 0:
					homo_number = int(orbitals[q][0])-1
					lumo_number = int(orbitals[q][0])
					break

		if not is_closed:
			del orbitals_beta[0:3]
			for q in range(len(orbitals_alpha)):
				if float(orbitals_alpha[q][1]) == 0:
					somo_number = int(orbitals_alpha[q][0])-1
					sumo_number = int(orbitals_alpha[q][0])
					break
		if jobtype == 'tddft':
		# TD-DFT section
			current_block = []
			for r in range(len(calc_output)):
				if 'TD-DFT/TDA EXCITED STATES' in calc_output[r]:
					tddft_section_start = r + 7
				if 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS' in calc_output[r]:
					states_section_start = r + 5
				if 'ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS' in calc_output[r]:
					tddft_section_end = r - 2

			for s in range(tddft_section_start-2, states_section_start-17):
				line = calc_output[s].strip()
				if not line:
					continue  # überspringt leere Zeilen
				parts = line.split()
				if parts[0] == 'STATE':
					if current_block:
						state_blocks.append(current_block)
						current_block = []
				else:
					try:
						from_orb = int(parts[0][:-1])
						to_orb = int(parts[2][:-1])
						coeff = float(parts[4])
						current_block.append([from_orb, to_orb, coeff])
					except (IndexError, ValueError):
						continue

			if current_block:
				state_blocks.append(current_block)
			
			for t in range(states_section_start, tddft_section_end):
				states.append(calc_output[t].strip().split()) #evtl rausnehmen
				energies.append(float(calc_output[t].strip().split()[3]))
				wavelengths.append(float(calc_output[t].strip().split()[5]))
				f_osc.append(format(float(calc_output[t].strip().split()[6]),'.2f'))

	print('Jobtype:', jobtype)
	print('Basis set:', basis_set)
	print('Charge:', charge)
	print('Multiplicity:', multiplicity)
	print('Closed shell system:', is_closed)
	print(f'Total energy: {total_energy} Hartree')
	if jobtype == 'freq' or jobtype == 'opt+freq':
		print('Frequencies:', freqs)
		print('Imaginary frequencies:', imaginary_freqs)
	print(f'Coords: {coords}')
	if jobtype == 'opt' or jobtype == 'tddft':
		if is_closed == False:
			#print('Alpha orbitals:', orbitals_alpha)
			#print('Beta orbitals:', orbitals_beta)
			print(f'SOMO Number: {somo_number+1} (ORCA Orbital Count: {somo_number})')
			print(f'SOMO Energy: {orbitals_alpha[somo_number][2]} Hartree')
			print(f'SUMO Number: {sumo_number+1} (ORCA Orbital Count: {sumo_number})')
			print(f'SUMO Energy: {orbitals_alpha[sumo_number][2]} Hartree')
		else:
			#print('Orbitals:', orbitals)
			print(f'HOMO Number: {homo_number+1} (ORCA Orbital Count: {homo_number})')
			print(f'HOMO Energy: {orbitals[homo_number][2]} Hartree')
			print(f'LUMO Number: {lumo_number+1} (ORCA Orbital Count: {lumo_number})')
			print(f'LUMO Energy: {orbitals[lumo_number][2]} Hartree')
		if jobtype == 'tddft':
			#print('States: ', states)
			print('State blocks:', state_blocks)
			print('Energies (eV):', energies)
			print('Wavelengths (nm):', wavelengths)
			print('f_osc:', f_osc)

	return file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords, state_blocks, energies, wavelengths, f_osc