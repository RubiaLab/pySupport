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

	print('Jobtype:', jobtype)
	print('Basis set:', basis_set)
	print('Charge:', charge)
	print('Multiplicity:', multiplicity)
	print(f'Total energy: {total_energy} Hartree')
	if jobtype == 'freq' or jobtype == 'opt+freq':
		print('Frequencies:', freqs)
		print('Imaginary frequencies:', imaginary_freqs)
	print(f'Coords: {coords}')

	return file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords