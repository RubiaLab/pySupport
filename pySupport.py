#!/usr/bin/python
__author__ = 'RubiaLab'
__email__ = 'a.r.krappe@gmail.com'
__version__ = '1.0'

def main():

	import modules.txt_generator as txt
	import modules.xlsx_generator as xlsx
	import modules.tex_generator as tex
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
				'[9] Coordinates only (.tex)')

	si_style = int(input('Please enter a number for the SI style: '))

	#Generate Excel workbook
	if si_style in [4, 5, 6]:
		import openpyxl
		SI_workbook = openpyxl.Workbook()

	for filename in sys.argv[1:]:

		if not os.path.isfile(filename):
			print(f'Specified file {filename} does not exist. Moving to next file...')
			continue

		print(f'Loaded {filename} as input:')
		with open(filename) as output:
			calc_output = output.readlines()

		#Determine QC program
		calc_program = None
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
		print('Calculation program: ', calc_program)
		print('Program version: ', program_version)

		if not calc_program:
			print('Could not determine calculation program. Exiting the program.')
			sys.exit()

		#Calculation file analysis
		if program_type == 0:
			file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords = fa.analyzer(filename)
		if program_type == 1:
			file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords = fa.analyzer(filename)

		#SI file generation
		if si_style in [1, 2, 3]:
			txt.generate_txt(si_style, file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords)
			print(f'File "{filename.strip()[:-3]}txt" for Supporting Information saved in the same directory.')
		elif si_style in [4, 5, 6]:
			xlsx.generate_xlsx(si_style, SI_workbook, file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords)
			print(f'Files for Supporting Information saved as "SI_output.xlsx" in the same directory.')
		elif si_style in [7, 8, 9]:
			tex.generate_tex(si_style, file, basis_set, charge, multiplicity, total_energy, jobtype, imaginary_freqs, coords)
			print(f'File "{file.strip()[:-3]}tex" for Supporting Information saved in the same directory.')

	if si_style in [4, 5, 6]:
		#Remove first empty worksheet
		del SI_workbook['Sheet']
		# Save xlsx file
		SI_workbook.save('SI_output.xlsx')
	print('### Exiting pySupport ###')

if __name__ == '__main__':
	main()