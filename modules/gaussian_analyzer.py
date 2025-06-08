import os
import sys

def analyzer(filename):
	print('Running Gaussian analyzer...')

	file = os.path.basename(filename)
	
	with open(filename) as output:
		calc_output = output.readlines()

	freqs = []
	imaginary_freqs = []
	states = []
	state_blocks = []
	energies = []
	wavelengths = []
	f_osc = []

	periodTable = ['Bq', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', \
					'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', \
					'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', \
					'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Ym', 'Yb', 'Lu', 'Ha', 'Ta', \
					'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', \
					'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', \
					'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']

	#Check normal termination
	normal_termination = any('Normal termination of Gaussian' in line for line in calc_output)
	if normal_termination:
		print(f'Calculation in file {file} terminated normally – continuing ...')
	else:
		print(f'Warning: Calculation in file {file} did not terminate normally. Exiting the program ...')
		sys.exit()

	coords = []
	geo_start_line = None
	input_line = None

	#Determine input section
	for i in range(len(calc_output)):
		if '#' in calc_output[i]:
			if not input_line:
				input_line = i

	for j, line in enumerate(calc_output):

		#Determine job type
		jobtype = 'other'
		opt_found = False
		route_line = calc_output[input_line].lower()

		if 'opt' in route_line:
			jobtype = 'opt'
			opt_found = True
		if 'freq' in route_line:
			if opt_found:
				jobtype = 'opt+freq'
			else:
				jobtype = 'freq'
		if 'td' in route_line:
			jobtype = 'tddft'

		#Determine basis set
		if 'Standard basis:' in line:
			basis_set = line.split()[2]

		#Determine charge
		if 'Charge =' in line:
			charge = line.split()[2]

		#Determine multiplicity
		if 'Multiplicity =' in line:
			multiplicity = line.split()[5]

		#Determine total energy
		if 'SCF Done:' in line:
			total_energy = line.split()[4]

		#Determine coordinates Gaussian
		if 'Standard orientation:' in line:
			geo_start_line = j

	if geo_start_line is not None:
		for m in range(geo_start_line + 5, len(calc_output)):
			if '--------' in calc_output[m]:
				geo_end_line = m
				break
			parts = calc_output[m].split()
			if len(parts) < 6:
				continue
			coords.append(f'{periodTable[int(parts[1])]} {parts[3]} {parts[4]} {parts[5]}')

	#Determine frequencies
	if jobtype == 'freq' or jobtype == 'opt+freq':
		freqs = []
		imaginary_freqs = []
		for m in range(len(calc_output)):
			if 'Harmonic frequencies' in calc_output[m]:
				break
		freq_start = m + 7
		print(freq_start)

		for n in range(freq_start, len(calc_output)):
			if 'Frequencies --' in calc_output[n]:
				try:
					freqs.append(calc_output[n].split()[2])
					freqs.append(calc_output[n].split()[3])
					freqs.append(calc_output[n].split()[4])
					if float(calc_output[n].split()[2]) < 0:
						imaginary_freqs.append(calc_output[n].split()[2])
					if float(calc_output[n].split()[3]) < 0:
						imaginary_freqs.append(calc_output[n].split()[3])
					if float(calc_output[n].split()[4]) < 0:
						imaginary_freqs.append(calc_output[n].split()[4])
				except:
					continue

	# TD-DFT section
	if jobtype == 'tddft':
		current_block = []
		for r in range(len(calc_output)):
			if 'Excited State' in calc_output[r]:
				tddft_section_start = r
				break
		for r in range(len(calc_output)):
			if 'Population analysis' in calc_output[r]:
				tddft_section_end = r - 3
				break

		for s in range(tddft_section_start, tddft_section_end):
			line = calc_output[s].strip()
			if not line:
				continue  # überspringt leere Zeilen
			parts = line.split()
			if parts[0] == 'Excited' and 'State' in parts[1]:
				print(str(s) + calc_output[s])
				energies.append(float(calc_output[s].strip().split()[4]))
				wavelengths.append(float(calc_output[s].strip().split()[6]))
				f_osc.append(format(float(calc_output[s].strip().split()[8][2:]),'.2f'))
				if current_block:
					state_blocks.append(current_block)
					current_block = []
			else:
				try:
					from_orb = int(parts[0])
					to_orb = int(parts[2])
					coeff = float(parts[3]) ** 2 * 100
					current_block.append([from_orb, to_orb, coeff])
				except (IndexError, ValueError):
					continue

		if current_block:
			state_blocks.append(current_block)		

	print('Jobtype: ', jobtype)
	print('Basis set: ', basis_set)
	print('Charge: ', charge)
	print('Multiplicity: ', multiplicity)
	print(f'Total energy: {total_energy} Hartree')
	if jobtype == 'freq' or jobtype == 'opt+freq':
		print('Frequencies: ', freqs)
		print('Imaginary frequencies: ', imaginary_freqs)
	print(f'Coords: {coords}')
	if jobtype == 'tddft':
			print('State blocks:', state_blocks)
			print('Energies (eV):', energies)
			print('Wavelengths (nm):', wavelengths)
			print('f_osc:', f_osc)

	return file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords, state_blocks, energies, wavelengths, f_osc