def generate_txt(si_style, file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords):
	print('Generating .txt file ...')
	si_out = open(f'{file.strip()[:-3]}txt', 'w')
	si_out.write(f'{file}\n')
	if si_style == 1 or si_style == 2:
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
	si_out.close()