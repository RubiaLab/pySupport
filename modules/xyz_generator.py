def generate_xyz(si_style, data):
	print('Generating .xyz file ...')
	si_out = open(f'{data.output_base}.xyz', 'w')
	if len(data.coords) > 0:
		if si_style == 10:
			si_out.write(str(len(data.coords)))
			si_out.write(f'\nCoordinate file generated from {data.file} with pySupport\n')
		for atom in data.atoms():
			si_out.write(' '.join(atom) + '\n')
	si_out.close()
