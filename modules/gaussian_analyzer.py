import os
import sys

def analyzer(filename):
	print('Running Gaussian analyzer...')

	file = os.path.basename(filename)
	
	with open(filename) as output:
		calc_output = output.readlines()

	freqs = []
	imaginary_freqs = []

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
		if 'opt' in calc_output[input_line]:
			jobtype = 'opt'
			opt_found = True
		if 'freq' in calc_output[input_line]:
			if opt_found:
				jobtype = 'opt+freq'
			else:
				jobtype = 'freq'

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

	print('Jobtype: ', jobtype)
	print('Basis set: ', basis_set)
	print('Charge: ', charge)
	print('Multiplicity: ', multiplicity)
	print(f'Total energy: {total_energy} Hartree')
	if jobtype == 'freq' or jobtype == 'opt+freq':
		print('Frequencies: ', freqs)
		print('Imaginary frequencies: ', imaginary_freqs)
	print(f'Coords: {coords}')

	return file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords