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

def write_tddft_table(si_out, state_blocks, energies, wavelengths, f_osc):
	#TD-DFT summary in its own table below the coordinates
	tddft_header = r'\hline' + '\n' + r'\textbf{State} & \textbf{Orbital Contribution} & \textbf{Energy (eV)} & \textbf{Wavelength (nm)} & \textbf{$f_{osc}$} \\ \hline'
	si_out.write(r'\begin{longtable}{ccccc}' + '\n')
	si_out.write(tddft_header + '\n')
	write_page_head(si_out, tddft_header)
	for n in range(len(state_blocks)):
		for m in range(len(state_blocks[n])):
			state_str = f'{n+1}' if m == 0  else ''
			energy_str = f'{format(energies[n], '.2f')}' if m == 0 else ''
			wavelength_str = f'{format(wavelengths[n], '.1f')}' if m == 0 else ''
			f_osc_str = f'{f_osc[n]}' if m == 0 else ''
			si_out.write(f'{state_str} & {state_blocks[n][m][0]} ')
			si_out.write(r'$\rightarrow$ ')
			si_out.write(f'{state_blocks[n][m][1]} ({format(state_blocks[n][m][2], '.3f')}) & {energy_str} & {wavelength_str} & {f_osc_str}')
			si_out.write(r'\\' + '\n')
	si_out.write(r'\end{longtable}' + '\n')

def generate_tex(si_style, file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords, state_blocks, energies, wavelengths, f_osc):
	if si_style == 7:
		print('under construction')
		print('Generating .tex file ...')
		
		si_out = open(f'{file.strip()[:-3]}tex', 'w')
		si_out.write(r'\documentclass{article}' + '\n')
		si_out.write(r'\usepackage[a4paper]{geometry}' + '\n')
		si_out.write(r'\usepackage{multirow}' + '\n')
		si_out.write(r'\usepackage{longtable}' + '\n')
		si_out.write('\\begin{document}' + '\n')
		si_out.write(r'\centering' + '\n')
		si_out.write(r'\begin{longtable}{ccclcccc}' + '\n')
		si_out.write(r'\hline' + '\n')
		si_out.write(r'\multicolumn{8}{c}{\textbf{')
		si_out.write(f'{tex_escape(file)}')
		si_out.write(r'}} \\ \hline' + '\n')
		si_out.write(r'\multicolumn{3}{c}{\multirow{8}{*}{}} & \multicolumn{5}{l}{Basis set: ')
		si_out.write(f'{tex_escape(basis_set)}')
		si_out.write(r'} \\' + '\n')
		si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{')
		si_out.write(f'Charge = {charge}, Multiplicity = {multiplicity}')
		si_out.write(r'} \\' + '\n')
		si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{')
		si_out.write(f'Electronic Energy = {total_energy} Hartree')
		si_out.write(r'} \\' + '\n')
		if jobtype == 'opt+freq' or jobtype == 'freq':
			if len(imaginary_freqs) == 0:
				si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{Number of imaginary frequencies = 0} \\' +  '\n')
			else:
				si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{')
				si_out.write(f'Number of imaginary frequencies = {len(imaginary_freqs)}, ')
				si_out.write(r'$\nu_{i}$ = ')
				si_out.write(f'{', '.join(imaginary_freqs)} ')
				si_out.write(r'cm$^{-1}$} \\' +  '\n')
		if len(coords) > 0:
			si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
			si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
			si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
			si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
			coords_header = r'\hline & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} &  & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} \\ \cline{2-4} \cline{6-8} \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \multicolumn{1}{c}{\textit{\textbf{Z}}} & \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \textit{\textbf{Z}} \\ \hline'
			si_out.write(coords_header + '\n')
			write_page_head(si_out, coords_header)

			if len(coords) % 2 == 0:
				tex_coordsLineNumber = int(len(coords) / 2)
				for r in range(0, len(coords), 2):
					si_out.write(f'{coords[r].split()[0]} & ')
					si_out.write(f'{coords[r].split()[1]} & ')
					si_out.write(f'{coords[r].split()[2]} & ')
					si_out.write(f'{coords[r].split()[3]} & ')
					si_out.write(f'{coords[r+1].split()[0]} & ')
					si_out.write(f'{coords[r+1].split()[1]} & ')
					si_out.write(f'{coords[r+1].split()[2]} & ')
					si_out.write(f'{coords[r+1].split()[3]}')
					si_out.write(r'\\')
					si_out.write('\n')
			elif len(coords) % 2 == 1:
				tex_coordsLineNumber = int((len(coords) + 1) / 2)
				for r in range(0, len(coords) - 1, 2):
					si_out.write(f'{coords[r].split()[0]} & ')
					si_out.write(f'{coords[r].split()[1]} & ')
					si_out.write(f'{coords[r].split()[2]} & ')
					si_out.write(f'{coords[r].split()[3]} & ')
					si_out.write(f'{coords[r+1].split()[0]} & ')
					si_out.write(f'{coords[r+1].split()[1]} & ')
					si_out.write(f'{coords[r+1].split()[2]} & ')
					si_out.write(f'{coords[r+1].split()[3]}')
					si_out.write(r'\\' + '\n')
				si_out.write(f'{coords[-1].split()[0]} & ')
				si_out.write(f'{coords[-1].split()[1]} & ')
				si_out.write(f'{coords[-1].split()[2]} & ')
				si_out.write(f'{coords[-1].split()[3]} & & & & ')
				si_out.write(r'\\' + '\n')
		si_out.write(r'\end{longtable}' + '\n')
		if jobtype == 'tddft':
			write_tddft = input('Write TD-DFT summary ([yes]/no)? ') or ('yes')
			if write_tddft == 'yes':
				print('Writing TD-DFT summary...')
				write_tddft_table(si_out, state_blocks, energies, wavelengths, f_osc)
		si_out.write(r'\end{document}' + '\n')
		si_out.close()

	elif si_style == 8:
		print('under construction')
		print('Generating .tex file ...')

		si_out = open(f'{file.strip()[:-3]}tex', 'w')
		si_out.write(r'\documentclass{article}' + '\n')
		si_out.write(r'\usepackage[a4paper]{geometry}' + '\n')
		si_out.write(r'\usepackage{multirow}' + '\n')
		si_out.write(r'\usepackage{longtable}' + '\n')
		si_out.write('\\begin{document}' + '\n')
		si_out.write(r'\centering' + '\n')
		si_out.write(r'\begin{longtable}{ccclcccc}' + '\n')
		si_out.write(r'\hline' + '\n')
		si_out.write(r'\multicolumn{8}{c}{\textbf{')
		si_out.write(f'{tex_escape(file)}')
		si_out.write(r'}} \\ \hline' + '\n')
		si_out.write(r'\multicolumn{3}{c}{\multirow{8}{*}{}} & \multicolumn{5}{l}{Basis set: ')
		si_out.write(f'{tex_escape(basis_set)}')
		si_out.write(r'} \\' + '\n')
		si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{')
		si_out.write(f'Charge = {charge}, Multiplicity = {multiplicity}')
		si_out.write(r'} \\' + '\n')
		si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{')
		si_out.write(f'Electronic Energy = {total_energy} Hartree')
		si_out.write(r'} \\' + '\n')
		si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' +  '\n')
		si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
		si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
		si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
		si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
		coords_header = r'\hline & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} &  & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} \\ \cline{2-4} \cline{6-8} \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \multicolumn{1}{c}{\textit{\textbf{Z}}} & \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \textit{\textbf{Z}} \\ \hline'
		si_out.write(coords_header + '\n')
		write_page_head(si_out, coords_header)

		if len(coords) % 2 == 0:
			tex_coordsLineNumber = int(len(coords) / 2)
			for r in range(0, len(coords), 2):
				si_out.write(f'{coords[r].split()[0]} & ')
				si_out.write(f'{coords[r].split()[1]} & ')
				si_out.write(f'{coords[r].split()[2]} & ')
				si_out.write(f'{coords[r].split()[3]} & ')
				si_out.write(f'{coords[r+1].split()[0]} & ')
				si_out.write(f'{coords[r+1].split()[1]} & ')
				si_out.write(f'{coords[r+1].split()[2]} & ')
				si_out.write(f'{coords[r+1].split()[3]}')
				si_out.write(r'\\')
				si_out.write('\n')
		elif len(coords) % 2 == 1:
			tex_coordsLineNumber = int((len(coords) + 1) / 2)
			for r in range(0, len(coords) - 1, 2):
				si_out.write(f'{coords[r].split()[0]} & ')
				si_out.write(f'{coords[r].split()[1]} & ')
				si_out.write(f'{coords[r].split()[2]} & ')
				si_out.write(f'{coords[r].split()[3]} & ')
				si_out.write(f'{coords[r+1].split()[0]} & ')
				si_out.write(f'{coords[r+1].split()[1]} & ')
				si_out.write(f'{coords[r+1].split()[2]} & ')
				si_out.write(f'{coords[r+1].split()[3]}')
				si_out.write(r'\\' + '\n')
			si_out.write(f'{coords[-1].split()[0]} & ')
			si_out.write(f'{coords[-1].split()[1]} & ')
			si_out.write(f'{coords[-1].split()[2]} & ')
			si_out.write(f'{coords[-1].split()[3]} & & & & ')
			si_out.write(r'\\' + '\n')
		si_out.write(r'\end{longtable}' + '\n')
		if jobtype == 'tddft':
			write_tddft = input('Write TD-DFT summary ([yes]/no)? ') or ('yes')
			if write_tddft == 'yes':
				print('Writing TD-DFT summary...')
				write_tddft_table(si_out, state_blocks, energies, wavelengths, f_osc)
		si_out.write(r'\end{document}' + '\n')
		si_out.close()

	elif si_style == 9:
		print('Generating .tex file ...')

		si_out = open(f'{file.strip()[:-3]}tex', 'w')
		si_out.write(r'\documentclass{article}' + '\n')
		si_out.write(r'\usepackage[a4paper]{geometry}' + '\n')
		si_out.write(r'\usepackage{multirow}' + '\n')
		si_out.write(r'\usepackage{longtable}' + '\n')
		si_out.write('\\begin{document}' + '\n')
		si_out.write(r'\centering' + '\n')
		si_out.write(r'\begin{longtable}{cccc} \hline' + '\n')
		si_out.write(r'\multicolumn{4}{c}{\textbf{')
		si_out.write(f'{tex_escape(file)}')
		si_out.write(r'}} \\ \hline' + '\n')
		coords_header = r' & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} \\ \cline{2-4} \\ \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \textit{\textbf{Z}} \\ \hline'
		si_out.write(coords_header + '\n')
		write_page_head(si_out, r'\hline' + coords_header)

		for n in range(len(coords)):
			si_out.write(f'{coords[n].split()[0]} & ')
			si_out.write(f'{coords[n].split()[1]} & ')
			si_out.write(f'{coords[n].split()[2]} & ')
			si_out.write(f'{coords[n].split()[3]} ')
			si_out.write(r'\\' + '\n')
		
		si_out.write(r'\end{longtable}' + '\n')
		if jobtype == 'tddft':
			write_tddft = input('Write TD-DFT summary ([yes]/no)? ') or ('yes')
			if write_tddft == 'yes':
				print('Writing TD-DFT summary...')
				write_tddft_table(si_out, state_blocks, energies, wavelengths, f_osc)
		si_out.write(r'\end{document}' + '\n')
		si_out.close()