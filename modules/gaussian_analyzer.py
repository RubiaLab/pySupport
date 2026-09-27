import os

def orca_style_contribution(from_label, to_label, coeff):
	#Same format as ORCA: orbitals counted from 0 and weights instead of CI coefficients
	if from_label[-1] in 'AB':
		#Unrestricted: orbitals labelled a/b like in ORCA, the squared coefficients add up to 1
		return [f'{int(from_label[:-1]) - 1}{from_label[-1].lower()}', f'{int(to_label[:-1]) - 1}{to_label[-1].lower()}', coeff ** 2]
	#Restricted closed shell: only the alpha part is printed, the squared coefficients add up to 0.5
	return [str(int(from_label) - 1), str(int(to_label) - 1), 2 * coeff ** 2]

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
					'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', \
					'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', \
					'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', \
					'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']

	#Check normal termination
	normal_termination = any('Normal termination of Gaussian' in line for line in calc_output)
	if normal_termination:
		print(f'Calculation in file {file} terminated normally – continuing ...')
	else:
		print(f'Warning: Calculation in file {file} did not terminate normally. Moving to next file ...')
		return None

	coords = []
	geo_start_line = None
	input_geo_start_line = None
	input_line = None
	basis_set = 'unknown'

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

		#Determine basis set (gen/genecp: basis set is defined in the input file)
		if 'Standard basis:' in line:
			basis_set = line.split()[2]
		elif 'General basis read from cards' in line:
			basis_set = 'genecp' if 'genecp' in route_line else 'gen'

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
		elif 'Input orientation:' in line:
			input_geo_start_line = j

	#Without symmetry (e.g. nosymm) Gaussian only prints the input orientation
	if geo_start_line is None:
		geo_start_line = input_geo_start_line

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

		#All values of the "Frequencies --" lines after the header (up to three modes per line)
		for n in range(m, len(calc_output)):
			if 'Frequencies --' in calc_output[n]:
				freqs.extend(calc_output[n].split()[2:])
		imaginary_freqs = [freq for freq in freqs if float(freq) < 0]

	# TD-DFT section
	if jobtype == 'tddft':
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
				energies.append(float(parts[4]))
				wavelengths.append(float(parts[6]))
				f_osc.append(format(float(parts[8][2:]),'.2f'))
				state_blocks.append([])
			#Excitations "i -> a" only, de-excitations "i <- a" are skipped
			elif state_blocks and len(parts) == 4 and parts[1] == '->':
				try:
					state_blocks[-1].append(orca_style_contribution(parts[0], parts[2], float(parts[3])))
				except ValueError:
					continue

		#Keep the contributions above filter_coeff, but at least the largest one, so that no state is dropped
		filter_coeff = 0.05
		state_blocks = [
			[entry for entry in block if abs(entry[2]) > filter_coeff] or sorted(block, key=lambda entry: abs(entry[2]))[-1:]
			for block in state_blocks
		]

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