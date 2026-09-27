def generate_txt(si_style, data):
	print('Generating .txt file ...')
	si_out = open(f'{data.output_base}.txt', 'w')
	si_out.write(f'{data.file}\n')
	if si_style == 1 or si_style == 2:
		si_out.write(f'Basis set = {data.basis_set}\n')
		si_out.write(f'Charge = {data.charge}, Multiplicity = {data.multiplicity}\n')
		si_out.write(f'Electronic energy = {data.total_energy} Hartree\n')
	if si_style == 1 and (data.jobtype == 'opt+freq' or data.jobtype == 'freq'):
		si_out.write(f'Number of imaginary frequencies = {len(data.imaginary_freqs)}\n')
		if data.imaginary_freqs:
			si_out.write(f'v_i = {', '.join(data.imaginary_freqs)} cm-1\n')
		for term, energy in data.thermochemistry.items():
			si_out.write(f'{term} = {energy} Hartree\n')
	if len(data.coords) > 0:
		si_out.write('\n---------------------------------------------------\n')
		si_out.write('                  Coordinates (Angstroems)\n')
		si_out.write(' Atoms        X              Y              Z\n')
		si_out.write('---------------------------------------------------\n')
		for symbol, x, y, z in data.atoms():
			si_out.write(f'   {symbol:<2}{x:>14}{y:>15}{z:>15}\n')
		si_out.write('---------------------------------------------------\n')
	if data.jobtype == 'tddft':
		write_tddft = input('Write TD-DFT summary ([yes]/no)? ') or ('yes')
		if write_tddft == 'yes':
			print('Writing TD-DFT summary...')
			row = '{:<7}{:<24}{:<14}{:<13}{:<17}{}'
			si_out.write('\n' + '-' * 80 + '\n')
			si_out.write(row.format('State', 'Orbital Contribution', 'HOMO/LUMO', 'Energy (eV)', 'Wavelength (nm)', 'f_osc') + '\n')
			si_out.write('-' * 80 + '\n')
			for n in range(len(data.state_blocks)):
				for m, contribution in enumerate(data.state_blocks[n]):
					state_str = data.state_label(n) if m == 0 else ''
					orbital_contribution_str = f'{contribution[0]} -> {contribution[1]} ({contribution[2]:.3f})'
					energy_str = f'{data.energies[n]:.2f}' if m == 0 else ''
					wavelength_str = f'{data.wavelengths[n]:.1f}' if m == 0 else ''
					f_osc_str = f'{data.f_osc[n]}' if m == 0 else ''
					si_out.write(row.format(state_str, orbital_contribution_str, data.homo_lumo(contribution, '->'), energy_str, wavelength_str, f_osc_str).rstrip() + '\n')
			si_out.write('-' * 80 + '\n')
	si_out.close()
