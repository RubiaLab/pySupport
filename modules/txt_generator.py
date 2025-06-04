def generate_txt(si_style, file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords, state_blocks, energies, wavelengths, f_osc):
	print('Generating .txt file ...')
	si_out = open(f'{file.strip()[:-3]}txt', 'w')
	si_out.write(f'{file}\n')
	if si_style == 1 or si_style == 2 or si_style == 12:
		si_out.write(f'Basis set = {basis_set}\n')
		si_out.write(f'Charge = {charge}, Multiplicity = {multiplicity}\n')
		si_out.write(f'Electronic energy = {total_energy} Hartree\n')
	if si_style == 1:
		if jobtype == 'opt+freq' or jobtype == 'freq':
			if len(imaginary_freqs) == 0:
				si_out.write(f'Number of imaginary frequencies = 0')
			else:
				si_out.write(f'Number of imaginary frequencies = {len(imaginary_freqs)}\n')
				si_out.write(f'v_i = {', '.join(imaginary_freqs)} cm-1')
			#si_out.write(f'Sum of electronic and zero-point Energies = {freqZPE}\n')
			#si_out.write(f'Sum of electronic and thermal Energies = {freqThr}\n')
			#si_out.write(f'Sum of electronic and thermal Enthalpies = {freqH}\n')
			#si_out.write(f'Sum of electronic and thermal Free Energies = {freqFE}\n')
	if len(coords) > 0:		
		si_out.write('\n---------------------------------------------------\n')
		si_out.write('                  Coordinates (Angstroems)\n')
		si_out.write(' Atoms        X              Y              Z\n')
		si_out.write('---------------------------------------------------\n')

		for n in range(len(coords)):
			si_out.write(f'   {coords[n].split()[0]}')
			if coords[n].split()[1][0] == '-':
				si_out.write(f'      {coords[n].split()[1]}')
			else:
				si_out.write(f'       {coords[n].split()[1]}')
			if coords[n].split()[2][0] == '-':
				si_out.write(f'      {coords[n].split()[2]}')
			else:
				si_out.write(f'       {coords[n].split()[2]}')
			if coords[n].split()[3][0] == '-':
				si_out.write(f'      {coords[n].split()[3]}\n')
			else:
				si_out.write(f'       {coords[n].split()[3]}\n')
		si_out.write('---------------------------------------------------\n')
	if jobtype == 'tddft':
		write_tddft = input('Write TD-DFT summary ([yes]/no)? ') or ('yes')
		if write_tddft == 'yes':
			print('Writing TD-DFT summary...')
			si_out.write('\n---------------------------------------------------------------------------\n')
			si_out.write('State\tOrbital Contribution\tEnergy (eV)\t\tWavelength (nm)\t\tf_osc\n')
			si_out.write('---------------------------------------------------------------------------\n')
			for n in range(len(state_blocks)):
				for m in range(len(state_blocks[n])):
					state_str = f'{n+1}' if m == 0  else ''
					orbital_contribution_str = f'{state_blocks[n][m][0]} -> {state_blocks[n][m][1]} ({state_blocks[n][m][2]:.3f})'
					energy_str = f'{energies[n]:.2f}' if m == 0 else ''
					wavelength_str = f'{wavelengths[n]:.1f}' if m == 0 else ''
					f_osc_str = f'{f_osc[n]}' if m == 0 else ''
					si_out.write(f'{state_str}\t\t{orbital_contribution_str}\t\t{energy_str}\t\t\t{wavelength_str}\t\t\t\t{f_osc_str}\n')
			si_out.write('---------------------------------------------------------------------------\n')
	si_out.close()