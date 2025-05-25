def generate_xyz(si_style, file, coords):
	print('Generating .xyz file ...')
	si_out = open(f'{file.strip()[:-3]}xyz', 'w')
	if len(coords) > 0:
		if si_style == 10:		
			si_out.write(str(len(coords)))
			si_out.write(f'\nCoordinate file generated from {file} with pySupport\n')
		for n in range(len(coords)):
			si_out.write(f'{coords[n].split()[0]}')
			if coords[n].split()[1][0] == '-':
				si_out.write(f' {coords[n].split()[1]}')
			else:
				si_out.write(f' {coords[n].split()[1]}')
			if coords[n].split()[2][0] == '-':
				si_out.write(f' {coords[n].split()[2]}')
			else:
				si_out.write(f' {coords[n].split()[2]}')
			if coords[n].split()[3][0] == '-':
				si_out.write(f' {coords[n].split()[3]}\n')
			else:
				si_out.write(f' {coords[n].split()[3]}\n')
	si_out.close()