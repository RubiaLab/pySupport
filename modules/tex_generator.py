def tex_escape(text):
	#Escape LaTeX special characters, e.g. underscores in file names
	special_chars = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
	return ''.join(special_chars.get(char, char) for char in text)

def write_page_head(si_out, column_header):
	#longtable: the rows written so far form the head of the first page, the column header is repeated on every further page
	si_out.write(r'\endfirsthead' + '\n')
	si_out.write(column_header + '\n')
	si_out.write(r'\endhead' + '\n')
	si_out.write(r'\hline' + '\n')
	si_out.write(r'\endfoot' + '\n')

def write_tddft_table(si_out, data):
	#TD-DFT summary in its own table below the coordinates
	tddft_header = r'\hline' + '\n' + r'\textbf{State} & \textbf{Orbital Contribution} & \textbf{HOMO/LUMO} & \textbf{Energy (eV)} & \textbf{Wavelength (nm)} & \textbf{$f_{osc}$} \\ \hline'
	si_out.write(r'\begin{longtable}{cccccc}' + '\n')
	si_out.write(tddft_header + '\n')
	write_page_head(si_out, tddft_header)
	for n in range(len(data.state_blocks)):
		for m, contribution in enumerate(data.state_blocks[n]):
			state_str = data.state_label(n) if m == 0 else ''
			energy_str = f'{data.energies[n]:.2f}' if m == 0 else ''
			wavelength_str = f'{data.wavelengths[n]:.1f}' if m == 0 else ''
			f_osc_str = f'{data.f_osc[n]}' if m == 0 else ''
			homo_lumo = data.homo_lumo(contribution, r'$\rightarrow$')
			si_out.write(f'{state_str} & {contribution[0]} ')
			si_out.write(r'$\rightarrow$ ')
			si_out.write(f'{contribution[1]} ({contribution[2]:.3f}) & {homo_lumo} & {energy_str} & {wavelength_str} & {f_osc_str}')
			si_out.write(r'\\' + '\n')
	si_out.write(r'\end{longtable}' + '\n')

def generate_tex(si_style, data):
	if si_style == 7 or si_style == 8:
		print('under construction')
	print('Generating .tex file ...')

	si_out = open(f'{data.output_base}.tex', 'w')
	si_out.write(r'\documentclass{article}' + '\n')
	si_out.write(r'\usepackage[a4paper]{geometry}' + '\n')
	si_out.write(r'\usepackage{multirow}' + '\n')
	si_out.write(r'\usepackage{longtable}' + '\n')
	si_out.write('\\begin{document}' + '\n')
	si_out.write(r'\centering' + '\n')

	#Full (7) and Simple (8): calculation details next to a space for a picture of the molecule, two atoms per row
	if si_style == 7 or si_style == 8:
		si_out.write(r'\begin{longtable}{ccclcccc}' + '\n')
		si_out.write(r'\hline' + '\n')
		si_out.write(r'\multicolumn{8}{c}{\textbf{')
		si_out.write(f'{tex_escape(data.file)}')
		si_out.write(r'}} \\ \hline' + '\n')

		details = [f'Basis set: {tex_escape(data.basis_set)}', f'Charge = {data.charge}, Multiplicity = {data.multiplicity}', f'Electronic Energy = {data.total_energy} Hartree']
		if si_style == 7 and (data.jobtype == 'opt+freq' or data.jobtype == 'freq'):
			if len(data.imaginary_freqs) == 0:
				details.append('Number of imaginary frequencies = 0')
			else:
				details.append(f'Number of imaginary frequencies = {len(data.imaginary_freqs)}, ' + r'$\nu_{i}$ = ' + f'{', '.join(data.imaginary_freqs)} ' + r'cm$^{-1}$')
			details += [f'{term} = {energy} Hartree' for term, energy in data.thermochemistry.items()]
		#The space for the picture spans eight rows
		details += [''] * (8 - len(details))
		si_out.write(r'\multicolumn{3}{c}{\multirow{8}{*}{}} & \multicolumn{5}{l}{' + details[0] + r'} \\' + '\n')
		for detail in details[1:]:
			si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{' + detail + r'} \\' + '\n')

		if len(data.coords) > 0:
			coords_header = r'\hline & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} &  & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} \\ \cline{2-4} \cline{6-8} \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \multicolumn{1}{c}{\textit{\textbf{Z}}} & \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \textit{\textbf{Z}} \\ \hline'
			si_out.write(coords_header + '\n')
			write_page_head(si_out, coords_header)

			atoms = data.atoms()
			for r in range(0, len(atoms), 2):
				if r + 1 < len(atoms):
					si_out.write(' & '.join(atoms[r] + atoms[r + 1]))
				else:
					si_out.write(' & '.join(atoms[r]) + ' & & & & ')
				si_out.write(r'\\' + '\n')

	#Coordinates only (9): one atom per row
	elif si_style == 9:
		si_out.write(r'\begin{longtable}{cccc} \hline' + '\n')
		si_out.write(r'\multicolumn{4}{c}{\textbf{')
		si_out.write(f'{tex_escape(data.file)}')
		si_out.write(r'}} \\ \hline' + '\n')
		coords_header = r' & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} \\ \cline{2-4} \\ \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \textit{\textbf{Z}} \\ \hline'
		si_out.write(coords_header + '\n')
		write_page_head(si_out, r'\hline' + coords_header)

		for atom in data.atoms():
			si_out.write(' & '.join(atom) + ' ')
			si_out.write(r'\\' + '\n')

	si_out.write(r'\end{longtable}' + '\n')
	if data.jobtype == 'tddft':
		write_tddft = input('Write TD-DFT summary ([yes]/no)? ') or ('yes')
		if write_tddft == 'yes':
			print('Writing TD-DFT summary...')
			write_tddft_table(si_out, data)
	si_out.write(r'\end{document}' + '\n')
	si_out.close()
