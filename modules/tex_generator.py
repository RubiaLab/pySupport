def generate_tex(si_style, file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords, state_blocks, energies, wavelengths, f_osc):
	if si_style == 7:
		print('under construction')
		print('Generating .tex file ...')
		
		si_out = open(f'{file.strip()[:-3]}tex', 'w')
		si_out.write(r'\documentclass{article}' + '\n')
		si_out.write(r'\usepackage[a4paper]{geometry}' + '\n')
		si_out.write(r'\usepackage{multirow}' + '\n')
		si_out.write('\\begin{document}' + '\n')
		si_out.write(r'\centering' + '\n')
		si_out.write(r'\begin{tabular}{ccclcccc}' + '\n')
		si_out.write(r'\hline' + '\n')
		si_out.write(r'\multicolumn{8}{c}{\textbf{out.log}} \\ \hline' + '\n')
		si_out.write(r'\multicolumn{3}{c}{\multirow{8}{*}{}} & \multicolumn{5}{l}{Basis set: ')
		si_out.write(f'{basis_set}')
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
				si_out.write(f'Number of imaginary frequencies = {len(imaginary_freqs)}, v')
				si_out.write(r'_{i} = ')
				si_out.write(f'{', '.join(imaginary_freqs)} ')
				si_out.write(r'cm^{-1}} \\' +  '\n')
		if len(coords) > 0:
			si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
			si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
			si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
			si_out.write(r'\multicolumn{3}{c}{} & \multicolumn{5}{l}{} \\' + '\n')
			si_out.write(r'\hline & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} &  & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} \\ \cline{2-4} \cline{6-8} \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \multicolumn{1}{c}{\textit{\textbf{Z}}} & \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \textit{\textbf{Z}} \\ \hline' + '\n')

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
			si_out.write(r'\hline' + '\n')
		if jobtype == 'tddft':
			write_tddft = input('Write TD-DFT summary ([yes]/no)? ') or ('yes')
			if write_tddft == 'yes':
				print('Writing TD-DFT summary...')
				si_out.write(r'\hline' + '\n')
				si_out.write(r'\textbf{State} & \textbf{Orbital Contribution} & \textbf{Energy (eV)} & \textbf{Wavelength (nm)} & \textbf{$f_{osc}$} \\ \hline' + '\n')
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
		si_out.write(r'\end{tabular}' + '\n')
		si_out.write(r'\end{document}' + '\n')
		si_out.close()

	elif si_style == 8:
		print('under construction')
		print('Generating .tex file ...')

		si_out = open(f'{file.strip()[:-3]}tex', 'w')
		si_out.write(r'\documentclass{article}' + '\n')
		si_out.write(r'\usepackage[a4paper]{geometry}' + '\n')
		si_out.write(r'\usepackage{multirow}' + '\n')
		si_out.write('\\begin{document}' + '\n')
		si_out.write(r'\centering' + '\n')
		si_out.write(r'\begin{tabular}{ccclcccc}' + '\n')
		si_out.write(r'\hline' + '\n')
		si_out.write(r'\multicolumn{8}{c}{\textbf{out.log}} \\ \hline' + '\n')
		si_out.write(r'\multicolumn{3}{c}{\multirow{8}{*}{}} & \multicolumn{5}{l}{Basis set: ')
		si_out.write(f'{basis_set}')
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
		si_out.write(r'\hline & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} &  & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} \\ \cline{2-4} \cline{6-8} \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \multicolumn{1}{c}{\textit{\textbf{Z}}} & \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \textit{\textbf{Z}} \\ \hline' + '\n')

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
		si_out.write(r'\hline' + '\n')
		if jobtype == 'tddft':
			write_tddft = input('Write TD-DFT summary ([yes]/no)? ') or ('yes')
			if write_tddft == 'yes':
				print('Writing TD-DFT summary...')
				si_out.write(r'\hline' + '\n')
				si_out.write(r'\textbf{State} & \textbf{Orbital Contribution} & \textbf{Energy (eV)} & \textbf{Wavelength (nm)} & \textbf{$f_{osc}$} \\ \hline' + '\n')
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
		si_out.write(r'\end{tabular}' + '\n')
		si_out.write(r'\end{document}' + '\n')
		si_out.close()

	elif si_style == 9:
		print('Generating .tex file ...')

		si_out = open(f'{file.strip()[:-3]}tex', 'w')
		si_out.write(r'\documentclass{article}' + '\n')
		si_out.write(r'\usepackage[a4paper]{geometry}' + '\n')
		si_out.write(r'\usepackage{multirow}' + '\n')
		si_out.write('\\begin{document}' + '\n')
		si_out.write(r'\centering' + '\n')
		si_out.write(r'\begin{tabular}{cccc} \hline' + '\n')
		si_out.write(r'\multicolumn{4}{c}{\textbf{')
		si_out.write(f'{file}')
		si_out.write(r'}} \\ \hline' + '\n')
		si_out.write(r' & \multicolumn{3}{c}{\textbf{Cartesian Coordinates (\r{A})}} \\ \cline{2-4} \\ \textbf{Atoms} & \textit{\textbf{X}} & \textit{\textbf{Y}} & \textit{\textbf{Z}} \\ \hline' + '\n')

		for n in range(len(coords)):
			si_out.write(f'{coords[n].split()[0]} & ')
			si_out.write(f'{coords[n].split()[1]} & ')
			si_out.write(f'{coords[n].split()[2]} & ')
			si_out.write(f'{coords[n].split()[3]} ')
			si_out.write(r'\\' + '\n')
		
		si_out.write(r'\hline' + '\n')
		if jobtype == 'tddft':
			print('Under construction...')
			write_tddft = input('Write TD-DFT summary ([yes]/no)? ') or ('yes')
			if write_tddft == 'yes':
				print('Writing TD-DFT summary...')
				si_out.write(r'\hline' + '\n')
				si_out.write(r'\textbf{State} & \textbf{Orbital Contribution} & \textbf{Energy (eV)} & \textbf{Wavelength (nm)} & \textbf{$f_{osc}$} \\ \hline' + '\n')
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
		si_out.write(r'\end{tabular}' + '\n')
		si_out.write(r'\end{document}' + '\n')
		si_out.close()