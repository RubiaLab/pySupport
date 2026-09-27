import os
import re
from modules.calc_data import CalcData

def read_coords(calc_output, start):
	#Read coordinate lines up to the next section header, skipping empty lines
	coords = []
	for line in calc_output[start:]:
		if '------' in line:
			break
		if line.strip():
			coords.append(line.strip())
	return coords

def analyzer(filename):
	
	file = os.path.basename(filename)

	with open(filename) as output:
		calc_output = output.readlines()

	#Check normal termination
	normal_termination = any('****ORCA TERMINATED NORMALLY****' in line for line in calc_output)
	if normal_termination:
		print(f'Calculation in file {file} terminated normally – continuing ...')
	else:
		print(f'Warning: Calculation in file {file} did not terminate normally. Moving to next file ...')
		return None
	
	coords = []
	freqs = []
	imaginary_freqs = []
	energies = []
	f_osc = []
	wavelengths = []
	orbitals = []
	orbitals_alpha = []
	orbitals_beta = []
	state_blocks = []
	spins = []
	is_closed = True
	beta_marker = False
	electrons = None
	excitation_energy = None

	#Determine input section
	for i in range(len(calc_output)):
		if 'INPUT FILE' in calc_output[i]:
			input_section_start = i+1
		if '****END OF INPUT****' in calc_output[i]:
			input_section_end = i+1
			break

	#Determine job type from the keyword lines (!) and the %tddft block of the input.
	#File names (NAME = ..., * xyzfile ...) and comments are ignored.
	keywords = ''
	tddft_found = False
	for k in range(input_section_start, input_section_end):
		input_line = calc_output[k].split('>', 1)[-1].split('#')[0].strip().casefold()
		if input_line.startswith('!'):
			keywords += f' {input_line}'
		if '%tddft' in input_line:
			tddft_found = True
	opt_found = 'opt' in keywords
	freq_found = 'freq' in keywords

	if tddft_found:
		jobtype = 'tddft'
	elif opt_found and freq_found:
		jobtype = 'opt+freq'
	elif opt_found:
		jobtype = 'opt'
	elif freq_found:
		jobtype = 'freq'
	elif '* Single Point Calculation *' in calc_output[input_section_end+3]:
		jobtype = 'sp'
	else:
		jobtype = 'other'

	for j, line in enumerate(calc_output):

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

		#Determine total energy (TD-DFT: including the excitation energy DE(CIS) of the state IRoot)
		if 'FINAL SINGLE POINT ENERGY' in line:
			total_energy = line.split()[4]
		if 'DE(CIS) =' in line:
			excitation_energy = line.split()[2]

		#Determine number of electrons
		if 'Number of Electrons' in line and 'NEL' in line:
			electrons = int(line.split()[-1])

		#Determine coordinates ORCA: final geometry of an optimization, otherwise the input geometry
		if opt_found:
			if '*** FINAL ENERGY EVALUATION AT THE STATIONARY POINT ***' in line:
				coords = read_coords(calc_output, j + 6)
		elif 'CARTESIAN COORDINATES (ANGSTROEM)' in line and not coords:
			coords = read_coords(calc_output, j + 2)

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

	#Thermochemistry of a frequency calculation, with the same terms as in Gaussian
	thermochemistry = {}
	if jobtype == 'freq' or jobtype == 'opt+freq':
		energy_terms = {}
		thermochemistry_start = max((i for i, line in enumerate(calc_output) if 'THERMOCHEMISTRY AT' in line), default=len(calc_output))
		for line in calc_output[thermochemistry_start:]:
			parts = line.split()
			if '...' in parts and 'Eh' in parts:
				energy_terms[line.split('...')[0].strip()] = parts[parts.index('Eh') - 1]
		if {'Electronic energy', 'Zero point energy', 'Total thermal energy', 'Total Enthalpy', 'Final Gibbs free energy'} <= energy_terms.keys():
			thermochemistry = {
				'Sum of electronic and zero-point Energies': f"{float(energy_terms['Electronic energy']) + float(energy_terms['Zero point energy']):.8f}",
				'Sum of electronic and thermal Energies': energy_terms['Total thermal energy'],
				'Sum of electronic and thermal Enthalpies': energy_terms['Total Enthalpy'],
				'Sum of electronic and thermal Free Energies': energy_terms['Final Gibbs free energy'],
			}

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
			#TD-DFT section: excited states of the last TD-DFT calculation (an optimization repeats it at every step).
			#With triplets true the triplets follow the singlets in their own section. Every state is labelled like in the
			#absorption spectrum: k-M for the k-th state of its section with multiplicity M.
			states = []
			spin = ''
			k = 0
			in_state = False
			for line in calc_output:
				parts = line.split()
				if re.search(r'EXCITED STATES( \(\w+\))?$', line.strip()):
					if 'TRIPLETS' not in line:
						states = []
					spin = 'T' if 'TRIPLETS' in line else 'S' if 'SINGLETS' in line else ''
					k = 0
					in_state = False
				elif re.match(r'STATE\s*\d+:', line):
					k += 1
					mult = parts[parts.index('Mult') + 1] if 'Mult' in parts else ''
					states.append({'label': f'{k}-{mult}', 'spin': spin, 'contributions': []})
					in_state = True
				#The orbital contributions follow the state line, de-excitations (<-) are skipped
				elif in_state and len(parts) >= 5 and parts[1] in ('->', '<-'):
					try:
						if parts[1] == '->':
							states[-1]['contributions'].append([parts[0], parts[2], float(parts[4])])
					except ValueError:
						continue
				else:
					in_state = False

			#Absorption spectrum of the last TD-DFT calculation, sorted by energy, e.g. '0-1A  ->  1-3A    4.187259   33772.5   296.1   0.000000000 ...'
			spectrum_start = max((i for i, line in enumerate(calc_output) if line.strip() == 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS'), default=len(calc_output)) + 5
			spectrum = []
			for line in calc_output[spectrum_start:]:
				parts = line.split()
				if len(parts) < 7 or parts[1] != '->':
					break
				spectrum.append(parts)

			#Sort the states like the spectrum by their label (without matching labels they are already in the same order)
			labels = [re.match(r'\d+-\d+', parts[2]) for parts in spectrum]
			labels = [label.group() if label else '' for label in labels]
			states_by_label = {state['label']: state for state in states}
			if all(label in states_by_label for label in labels):
				states = [states_by_label[label] for label in labels]
			states = states[:len(spectrum)]
			state_blocks = [state['contributions'] for state in states]
			spins = [state['spin'] for state in states]

			#Closed shell: all orbitals are alpha orbitals (a), so the label is dropped. Open shell: a/b are kept like in the ORCA output.
			if is_closed and not any(entry[0].endswith('b') for block in state_blocks for entry in block):
				state_blocks = [[[entry[0].removesuffix('a'), entry[1].removesuffix('a'), entry[2]] for entry in block] for block in state_blocks]

			#Keep the contributions above filter_coeff, but at least the largest one, so that no state is dropped
			filter_coeff = 0.05
			state_blocks = [
				[entry for entry in block if abs(entry[2]) > filter_coeff] or sorted(block, key=lambda entry: abs(entry[2]))[-1:]
				for block in state_blocks
			]
			for parts in spectrum:
				energies.append(float(parts[3]))
				wavelengths.append(float(parts[5]))
				f_osc.append(format(float(parts[6]), '.2f'))

	#The final single point energy of TD-DFT includes the excitation energy of the state IRoot. For a single point the
	#ground state energy is given like in Gaussian, for an excited state optimization the energy of the optimized state.
	if jobtype == 'tddft' and not opt_found and excitation_energy:
		total_energy = f'{float(total_energy) - float(excitation_energy):.9f}'

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
			print(f'Only listing orbital contributions > {filter_coeff} (at least the largest one per state).')
			print('State blocks:', state_blocks)
			print('Energies (eV):', energies)
			print('Wavelengths (nm):', wavelengths)
			print('f_osc:', f_osc)

	#HOMO counted from 0 for the alpha (a) and beta (b) electrons, closed shell: ''
	homo = {}
	if electrons:
		alpha = (electrons + int(multiplicity) - 1) // 2
		homo = {'': alpha - 1, 'a': alpha - 1, 'b': electrons - alpha - 1}

	return CalcData(filename, basis_set=basis_set, charge=charge, multiplicity=multiplicity, total_energy=total_energy, jobtype=jobtype, imaginary_freqs=imaginary_freqs,
		thermochemistry=thermochemistry, coords=coords, homo=homo, state_blocks=state_blocks, spins=spins, energies=energies, wavelengths=wavelengths, f_osc=f_osc)