import os
import openpyxl
from openpyxl.styles import Border, Font, Alignment, Side
from openpyxl.utils import get_column_letter

linecolor = '000000'
font_style = 'Arial'
font_size = 10

mediumBorder = Side(border_style = 'medium', color = linecolor)
thinBorder = Side(border_style = 'thin', color = linecolor)
dashedBorder = Side(border_style = 'dashed', color = linecolor)

def sheet_title(SI_workbook, name, suffix = ''):
	#Excel allows at most 31 characters and no \ / ? * : [ ] in sheet names. Longer names are shortened, existing ones get a number.
	name = ''.join('_' if char in '\\/?*:[]' else char for char in name)
	title = name[:31 - len(suffix)] + suffix
	number = 1
	while title.lower() in [sheetname.lower() for sheetname in SI_workbook.sheetnames]:
		number += 1
		title = f'{name[:31 - len(suffix) - len(str(number)) - 1]}_{number}{suffix}'
	return title

def set_font(SI_worksheet, cell_range, **font):
	for row in SI_worksheet[cell_range]:
		for cell in row:
			cell.font = Font(name = font_style, size = font_size, **font)

def set_border(SI_worksheet, cell_range, **border):
	for row in SI_worksheet[cell_range]:
		for cell in row:
			cell.border = Border(**border)

def write_coordinate_header(SI_worksheet, row, first_column):
	#"Atoms" and "Cartesian Coordinates" with X, Y, Z below in four columns and two rows
	atoms, x, y, z = [get_column_letter(first_column + n) for n in range(4)]
	SI_worksheet.merge_cells(f'{atoms}{row}:{atoms}{row + 1}')
	SI_worksheet.merge_cells(f'{x}{row}:{z}{row}')

	SI_worksheet[f'{atoms}{row}'] = 'Atoms'
	SI_worksheet[f'{atoms}{row}'].font = Font(name = font_style, size = font_size, bold = True)
	SI_worksheet[f'{atoms}{row}'].alignment = Alignment(horizontal = 'center', vertical = 'bottom')
	SI_worksheet[f'{atoms}{row + 1}'].border = Border(bottom = thinBorder)

	SI_worksheet[f'{x}{row}'] = 'Cartesian Coordinates'
	SI_worksheet[f'{x}{row}'].font = Font(name = font_style, size = font_size, bold = True)
	SI_worksheet[f'{x}{row}'].alignment = Alignment(horizontal = 'center', vertical = 'center')

	for column, axis in zip((x, y, z), 'XYZ'):
		SI_worksheet[f'{column}{row + 1}'] = axis
		SI_worksheet[f'{column}{row + 1}'].font = Font(name = font_style, size = font_size, bold = True, italic = True)
		SI_worksheet[f'{column}{row + 1}'].alignment = Alignment(horizontal = 'center', vertical = 'center')
		SI_worksheet[f'{column}{row + 1}'].border = Border(top = dashedBorder, bottom = thinBorder)

def write_coordinate_rows(SI_worksheet, rows, last_column):
	#Append the coordinates below the header, the last row gets a medium line
	first_row = SI_worksheet.max_row + 1
	for row in rows:
		SI_worksheet.append(row)
	last_row = SI_worksheet.max_row
	for row in SI_worksheet[f'A{first_row}:{last_column}{last_row}']:
		for cell in row:
			cell.font = Font(name = font_style, size = font_size)
			cell.alignment = Alignment(horizontal = 'center', vertical = 'center')
	set_border(SI_worksheet, f'A{last_row}:{last_column}{last_row}', bottom = mediumBorder)
	return last_row

def generate_xlsx(si_style, SI_workbook, data):
	name = os.path.splitext(data.file)[0]
	atoms = data.atoms()

	if si_style == 4:
		print('Generating Full .xlsx file ...')
		SI_worksheet = SI_workbook.create_sheet(title=sheet_title(SI_workbook, name))
		for column, width in zip('ABCDEFGH', (7.25, 10.2, 10.2, 10.2, 7.25, 10.2, 10.2, 10.2)):
			SI_worksheet.column_dimensions[column].width = width

		set_border(SI_worksheet, 'A1:H1', bottom = mediumBorder)
		set_border(SI_worksheet, 'A9:H9', bottom = thinBorder)
		set_font(SI_worksheet, 'A2:H9')

		SI_worksheet.merge_cells('A1:H1')
		SI_worksheet['A1'] = data.file
		SI_worksheet['A1'].font = Font(name = font_style, size = 10.5, bold = True)
		SI_worksheet['A1'].alignment = Alignment(horizontal = 'center', vertical = 'center')

		SI_worksheet.merge_cells('A2:C9')
		SI_worksheet['A2'].font = Font(name = font_style, size = 10.5, color = '929292')
		SI_worksheet['A2'].alignment = Alignment(horizontal = 'center', vertical = 'center')
		SI_worksheet['A2'] = 'Insert molecular geometry here.'

		#Calculation details in D2 to D9
		details = [f'Basis set: {data.basis_set}', f'Charge = {data.charge}, Multiplicity = {data.multiplicity}', f'Electronic Energy = {data.total_energy} Hartree']
		if data.jobtype == 'opt+freq' or data.jobtype == 'freq':
			if len(data.imaginary_freqs) == 0:
				details.append('Number of imaginary frequencies = 0')
			else:
				details.append(f'Number of imaginary frequencies = {len(data.imaginary_freqs)}, v_i = {', '.join(data.imaginary_freqs)} cm-1')
			details += [f'{term} = {energy} Hartree' for term, energy in data.thermochemistry.items()]
		for row in range(2, 10):
			SI_worksheet.merge_cells(f'D{row}:H{row}')
		for row, detail in enumerate(details, 2):
			SI_worksheet[f'D{row}'] = detail
		SI_worksheet['D2'].font = Font(name = 'Courier', size = font_size)

		#Two atoms per row
		if len(atoms) > 0:
			write_coordinate_header(SI_worksheet, 10, 1)
			write_coordinate_header(SI_worksheet, 10, 5)
			rows = [atoms[r] + (atoms[r + 1] if r + 1 < len(atoms) else []) for r in range(0, len(atoms), 2)]
			last_row = write_coordinate_rows(SI_worksheet, rows, 'H')
			set_border(SI_worksheet, f'E10:E{last_row}', left = dashedBorder)
			SI_worksheet['E11'].border = Border(left = dashedBorder, bottom = thinBorder)
			SI_worksheet[f'E{last_row}'].border = Border(left = dashedBorder, bottom = mediumBorder)

	elif si_style == 5:
		print('Generating Simple .xlsx file ...')
		SI_worksheet = SI_workbook.create_sheet(title=sheet_title(SI_workbook, name))
		for column, width in zip('ABCD', (8.25, 12.25, 12.25, 12.25)):
			SI_worksheet.column_dimensions[column].width = width

		set_font(SI_worksheet, 'A2:D4')
		set_border(SI_worksheet, 'A1:D1', bottom = mediumBorder)
		set_border(SI_worksheet, 'A4:D4', bottom = thinBorder)

		SI_worksheet.merge_cells('A1:D1')
		SI_worksheet['A1'] = data.file
		SI_worksheet['A1'].font = Font(name = font_style, size = font_size, bold = True)
		SI_worksheet['A1'].alignment = Alignment(horizontal = 'center', vertical = 'center')

		SI_worksheet.merge_cells('A2:D2')
		SI_worksheet['A2'] = f'Basis set: {data.basis_set}'
		SI_worksheet['A2'].font = Font(name = 'Courier', size = font_size)

		SI_worksheet.merge_cells('A3:D3')
		SI_worksheet['A3'] = f'Charge = {data.charge}, Multiplicity = {data.multiplicity}'

		SI_worksheet.merge_cells('A4:D4')
		SI_worksheet['A4'] = f'Electronic Energy = {data.total_energy} Hartree'

		if len(atoms) > 0:
			write_coordinate_header(SI_worksheet, 5, 1)
			write_coordinate_rows(SI_worksheet, atoms, 'D')

	elif si_style == 6:
		if len(atoms) == 0:
			print('No coordinates found in output file. Moving to next file...')
			return

		print('Generating coordinates .xlsx file ...')
		SI_worksheet = SI_workbook.create_sheet(title=sheet_title(SI_workbook, name))
		for column, width in zip('ABCD', (7.25, 11.25, 11.25, 11.25)):
			SI_worksheet.column_dimensions[column].width = width

		set_border(SI_worksheet, 'A1:D1', bottom = mediumBorder)
		SI_worksheet.merge_cells('A1:D1')
		SI_worksheet['A1'] = data.file
		SI_worksheet['A1'].font = Font(name = font_style, size = font_size, bold = True)
		SI_worksheet['A1'].alignment = Alignment(horizontal = 'center', vertical = 'center')

		write_coordinate_header(SI_worksheet, 2, 1)
		write_coordinate_rows(SI_worksheet, atoms, 'D')

	for row in range(1, SI_worksheet.max_row + 1):
		SI_worksheet.row_dimensions[row].height = 16.0

	if data.jobtype == 'tddft':
		write_tddft = input('Write TD-DFT summary ([yes]/no)? ').strip().lower() or ('yes')
		if write_tddft == 'yes':
			print('Writing TD-DFT summary...')
			SI_worksheet = SI_workbook.create_sheet(title=sheet_title(SI_workbook, name, '_TD-DFT'))
			for column, width in zip('ABCDEF', (10, 21, 15, 15, 15, 15)):
				SI_worksheet.column_dimensions[column].width = width

			for column, header in zip('ABCDEF', ('State', 'Orbital Contribution', 'HOMO/LUMO', 'Energy (eV)', 'Wavelength (nm)', 'f_osc')):
				SI_worksheet[f'{column}1'] = header
				SI_worksheet[f'{column}1'].border = Border(bottom = thinBorder)
				SI_worksheet[f'{column}1'].font = Font(name = font_style, size = 10, bold = True)
				SI_worksheet[f'{column}1'].alignment = Alignment(horizontal = 'center', vertical = 'center')

			wrap_center = Alignment(wrap_text=True, vertical='top', horizontal='center')  # Stil für Orbital Contribution
			cell_alignment = Alignment(horizontal='center', vertical='top')
			cell_font = Font(name = font_style, size = font_size)

			#One row per orbital contribution, the cells of a state are merged
			row = 2
			for n in range(len(data.state_blocks)):
				start_row = row
				end_row = row + len(data.state_blocks[n]) - 1
				state = data.state_label(n)
				values = (int(state) if state.isdigit() else state,
					'\n'.join(f'{contribution[0]} → {contribution[1]} ({contribution[2]:.3f})' for contribution in data.state_blocks[n]),
					'\n'.join(data.homo_lumo(contribution, '→') for contribution in data.state_blocks[n]),
					f'{data.energies[n]:.2f}', f'{data.wavelengths[n]:.1f}', f'{data.f_osc[n]}')
				for column, value in zip('ABCDEF', values):
					if end_row > start_row:
						SI_worksheet.merge_cells(f'{column}{start_row}:{column}{end_row}')
					SI_worksheet[f'{column}{start_row}'] = value
					SI_worksheet[f'{column}{start_row}'].alignment = wrap_center if column in 'BC' else cell_alignment
					SI_worksheet[f'{column}{start_row}'].font = cell_font
					SI_worksheet[f'{column}{end_row}'].border = Border(bottom=thinBorder)
				row = end_row + 1
