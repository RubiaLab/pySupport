#!/usr/bin/python
__author__ = 'RubiaLab'
__email__ = 'rubialab@rubialab.de'
__version__ = '1.2'

def main():

	import modules.txt_generator as txt
	import modules.xlsx_generator as xlsx
	import modules.tex_generator as tex
	import modules.xyz_generator as xyz
	import sys
	import os

	print('### Starting pySupport ###')

	# Data Input
	if len(sys.argv) < 2:
		print('Please provide at least one filename as an argument.')
		sys.exit()

	print('--- Supporting Information Styles ---\n',
				'[1] Full (.txt)\n',
				'[2] Simple (.txt)\n',
				'[3] Coordinates only (.txt)\n',
				'[4] Full (.xlsx)\n',
				'[5] Simple (.xlsx)\n',
				'[6] Coordinates only (.xlsx)\n',
				'[7] Full (.tex)\n',
				'[8] Simple (.tex)\n',
				'[9] Coordinates only (.tex)\n',
				'[10] XYZ file (ORCA style)\n',
				'[11] XYZ file (Gaussian style)')

	si_style = int(input('Please enter a number for the SI style: '))

	#Generate Excel workbook, it is saved next to the first input file
	if si_style in [4, 5, 6]:
		import openpyxl
		SI_workbook = openpyxl.Workbook()
		xlsx_file = None

	for filename in sys.argv[1:]:

		if not os.path.isfile(filename):
			print(f'Specified file {filename} does not exist. Moving to next file...')
			continue

		print(f'Loaded {filename} as input:')
		with open(filename) as output:
			calc_output = output.readlines()

		#Determine QC program
		calc_program = None
		program_type = None
		program_version = 'unknown'
		previous_line = None
		for line in calc_output:
			if '* O   R   C   A *' in line:
				calc_program = 'ORCA'
				program_type = 0
				import modules.orca_analyzer as fa
			elif 'Entering Gaussian System' in line:
				calc_program = 'Gaussian'
				program_type = 1
				import modules.gaussian_analyzer as fa
			if 'Program Version' in line:
				program_version = line.split()[2]
				break
			elif previous_line and 'Cite this work as:' in previous_line and program_type == 1:
				program_version = line.strip()[:-1]
				break
			previous_line = line

		if not calc_program:
			print(f'Could not determine calculation program of {filename}. Moving to next file...')
			continue
		print('Calculation program: ', calc_program)
		print('Program version: ', program_version)

		#Calculation file analysis (None if the calculation did not terminate normally)
		data = fa.analyzer(filename)
		if data is None:
			continue

		#SI file generation next to the input file
		if si_style in [1, 2, 3]:
			txt.generate_txt(si_style, data)
			print(f'File "{data.output_base}.txt" for Supporting Information saved.')
		elif si_style in [4, 5, 6]:
			xlsx.generate_xlsx(si_style, SI_workbook, data)
			xlsx_file = xlsx_file or os.path.join(os.path.dirname(data.filename), 'SI_output.xlsx')
		elif si_style in [7, 8, 9]:
			tex.generate_tex(si_style, data)
			print(f'File "{data.output_base}.tex" for Supporting Information saved.')
		elif si_style in [10, 11]:
			xyz.generate_xyz(si_style, data)
			print(f'File "{data.output_base}.xyz" saved.')

	if si_style in [4, 5, 6]:
		#Remove first empty worksheet
		del SI_workbook['Sheet']
		# Save xlsx file (only if at least one worksheet was generated)
		if SI_workbook.sheetnames:
			SI_workbook.save(xlsx_file)
			print(f'Files for Supporting Information saved as "{xlsx_file}".')
		else:
			print('No worksheets were generated, "SI_output.xlsx" was not written.')
	print('### Exiting pySupport ###')

if __name__ == '__main__':
	main()
