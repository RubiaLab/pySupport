#Regression tests for pySupport
#
#The files in tests/fixtures are small synthetic excerpts that mimic the layout of ORCA 6 and
#Gaussian 16 output files. They only contain the sections pySupport reads.
#
#Run from the repository root (Python >= 3.12):
#	python3 -m unittest discover -s tests -v

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import openpyxl
import pySupport
from modules import gaussian_analyzer, orca_analyzer, tex_generator

FIXTURES = os.path.join(REPO_ROOT, 'tests', 'fixtures')
FIELDS = ('file', 'basis_set', 'charge', 'multiplicity', 'total_energy', 'jobtype', 'imaginary_freqs', 'coords', 'state_blocks', 'energies', 'wavelengths', 'f_osc')
ELEMENTS = ('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr '
	'Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu '
	'Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr '
	'Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og').split()
WATER_ORCA = ['O      0.000000    0.000000    0.119262', 'H      0.000000    0.763239   -0.477047', 'H      0.000000   -0.763239   -0.477047']
WATER_GAUSSIAN = ['O 0.000000 0.000000 0.119262', 'H 0.000000 0.763239 -0.477047', 'H 0.000000 -0.763239 -0.477047']


def fixture(name):
	return os.path.join(FIXTURES, name)


def analyze(analyzer, path):
	#Run an analyzer without its console output and return the results by name
	with contextlib.redirect_stdout(io.StringIO()):
		result = analyzer(path)
	return None if result is None else dict(zip(FIELDS, result))


class TempDirTestCase(unittest.TestCase):
	#pySupport writes its output files into the current working directory

	def setUp(self):
		tmp = tempfile.TemporaryDirectory()
		self.addCleanup(tmp.cleanup)
		self.addCleanup(os.chdir, os.getcwd())
		os.chdir(tmp.name)

	def write(self, name, text):
		with open(name, 'w') as f:
			f.write(text)
		return os.path.abspath(name)

	def modified_fixture(self, fixture_name, new_name, old, new):
		with open(fixture(fixture_name)) as f:
			return self.write(new_name, f.read().replace(old, new))


class OrcaAnalyzerTest(unittest.TestCase):

	def test_opt_and_freq_in_one_keyword_line(self):
		data = analyze(orca_analyzer.analyzer, fixture('orca_opt_freq.out'))
		self.assertEqual(data['jobtype'], 'opt+freq')
		self.assertEqual(data['imaginary_freqs'], ['-150.00'])

	def test_optimization_uses_final_geometry(self):
		data = analyze(orca_analyzer.analyzer, fixture('orca_opt_freq.out'))
		self.assertEqual(data['coords'], WATER_ORCA)

	def test_file_names_and_comments_do_not_change_job_type(self):
		#water_opt.xyz and "optimized" in a comment must not turn a frequency job into an optimization
		data = analyze(orca_analyzer.analyzer, fixture('orca_freq.out'))
		self.assertEqual(data['jobtype'], 'freq')

	def test_frequency_job_has_coordinates(self):
		data = analyze(orca_analyzer.analyzer, fixture('orca_freq.out'))
		self.assertEqual(data['coords'], WATER_ORCA)

	def test_tddft_single_point_has_coordinates(self):
		data = analyze(orca_analyzer.analyzer, fixture('orca_tddft.out'))
		self.assertEqual(data['jobtype'], 'tddft')
		self.assertEqual(data['coords'], WATER_ORCA)
		self.assertEqual(data['energies'], [7.331939, 8.163398, 9.140216])

	def test_tddft_states_stay_aligned_with_their_energies(self):
		#State 2 has no contribution > 0.05 and keeps its largest one, the last line of state 3 must not be cut off
		data = analyze(orca_analyzer.analyzer, fixture('orca_tddft.out'))
		self.assertEqual(data['state_blocks'], [[[4, 5, 0.99438]], [[2, 5, 0.04]], [[3, 5, 0.88], [4, 6, 0.1]]])
		self.assertEqual(len(data['state_blocks']), len(data['energies']))


class GaussianAnalyzerTest(TempDirTestCase):

	def test_nosymm_uses_last_input_orientation(self):
		data = analyze(gaussian_analyzer.analyzer, fixture('gaussian_opt_nosymm.out'))
		self.assertEqual(data['coords'], WATER_GAUSSIAN)

	def test_standard_orientation_is_preferred(self):
		data = analyze(gaussian_analyzer.analyzer, fixture('gaussian_genecp.out'))
		self.assertEqual(data['coords'][0], 'Hf 0.000000 0.000000 0.000000')

	def test_general_basis_set(self):
		data = analyze(gaussian_analyzer.analyzer, fixture('gaussian_genecp.out'))
		self.assertEqual(data['basis_set'], 'genecp')
		gen = self.modified_fixture('gaussian_genecp.out', 'gen.out', 'b3lyp/genecp', 'b3lyp/gen')
		self.assertEqual(analyze(gaussian_analyzer.analyzer, gen)['basis_set'], 'gen')

	def test_element_symbols(self):
		rule = ' ' + '-' * 69
		lines = [
			' Entering Gaussian System, Link 0=g16',
			' #p b3lyp/6-31g(d)',
			' Charge =  0 Multiplicity = 1',
			'                         Standard orientation:',
			rule,
			' Center     Atomic      Atomic             Coordinates (Angstroms)',
			' Number     Number       Type             X           Y           Z',
			rule,
			*[f'{z:7d}{z:11d}{0:12d}{0:16.6f}{0:12.6f}{z:12.6f}' for z in range(1, 119)],
			rule,
			' Standard basis: 6-31G(d) (6D, 7F)',
			' SCF Done:  E(RB3LYP) =  -100.000000000     A.U. after   10 cycles',
			' Normal termination of Gaussian 16',
		]
		data = analyze(gaussian_analyzer.analyzer, self.write('elements.out', '\n'.join(lines) + '\n'))
		self.assertEqual([atom.split()[0] for atom in data['coords']], ELEMENTS)


class PySupportTest(TempDirTestCase):

	def run_pysupport(self, si_style, *files):
		#Answer the style menu with si_style and return the console output
		with mock.patch.object(sys, 'argv', ['pySupport.py', *files]), mock.patch('builtins.input', return_value=str(si_style)), contextlib.redirect_stdout(io.StringIO()) as output:
			pySupport.main()
		return output.getvalue()

	def test_unknown_and_missing_files_are_skipped(self):
		unknown = self.write('notes.out', 'not an ORCA or Gaussian output\n')
		output = self.run_pysupport(1, unknown, 'missing.out', fixture('orca_opt_freq.out'))
		self.assertIn('Could not determine calculation program', output)
		self.assertTrue(os.path.isfile('orca_opt_freq.txt'))

	def test_abnormal_termination_skips_only_this_file(self):
		aborted = self.modified_fixture('orca_opt_freq.out', 'aborted.out', '****ORCA TERMINATED NORMALLY****', '')
		self.run_pysupport(1, aborted, fixture('orca_freq.out'))
		self.assertFalse(os.path.exists('aborted.txt'))
		self.assertTrue(os.path.isfile('orca_freq.txt'))

	def test_excel_without_worksheets_is_not_written(self):
		self.run_pysupport(4, 'missing.out')
		self.assertFalse(os.path.exists('SI_output.xlsx'))

	def test_excel_coordinates_only_skips_files_without_coordinates(self):
		no_coords = self.modified_fixture('gaussian_genecp.out', 'no_coords.out', 'orientation:', 'orientation removed')
		self.run_pysupport(6, no_coords, fixture('orca_freq.out'))
		self.assertEqual(openpyxl.load_workbook('SI_output.xlsx').sheetnames, ['orca_freq'])


class TexGeneratorTest(TempDirTestCase):

	def generate(self, si_style, name):
		#Write the .tex file for an ORCA fixture (TD-DFT summary: yes) and return its content
		data = analyze(orca_analyzer.analyzer, fixture(name))
		with mock.patch('builtins.input', return_value='yes'), contextlib.redirect_stdout(io.StringIO()):
			tex_generator.generate_tex(si_style, **data)
		with open(f'{name[:-3]}tex') as f:
			return f.read()

	def test_title_is_the_escaped_file_name(self):
		for si_style in (7, 8, 9):
			with self.subTest(si_style=si_style):
				tex = self.generate(si_style, 'orca_opt_freq.out')
				self.assertIn(r'\textbf{orca\_opt\_freq.out}', tex)
				self.assertNotIn('out.log', tex)

	def test_imaginary_frequencies_in_math_mode(self):
		tex = self.generate(7, 'orca_opt_freq.out')
		self.assertIn(r'$\nu_{i}$ = -150.00 cm$^{-1}$', tex)

	def test_tddft_summary_has_own_table(self):
		for si_style in (7, 8, 9):
			with self.subTest(si_style=si_style):
				coordinates, tddft = self.generate(si_style, 'orca_tddft.out').split(r'\begin{longtable}{ccccc}')
				self.assertIn('Cartesian Coordinates', coordinates)
				self.assertNotIn(r'\textbf{State}', coordinates)
				self.assertIn(r'\textbf{State}', tddft)

	@unittest.skipUnless(shutil.which('pdflatex'), 'pdflatex is not installed')
	def test_long_tables_break_across_pages(self):
		#150 atoms and 60 excited states do not fit on one page, nothing may be cut off at the bottom of a page
		coords = [f'C {n:.6f} 0.000000 0.000000' for n in range(150)]
		state_blocks = [[[10, 11, 0.9], [9, 12, 0.08]] for n in range(60)]
		energies = [2.0 + n / 10 for n in range(60)]
		wavelengths = [1239.84 / energy for energy in energies]
		f_osc = ['0.10'] * 60
		for si_style in (7, 8, 9):
			with self.subTest(si_style=si_style):
				with mock.patch('builtins.input', return_value='yes'), contextlib.redirect_stdout(io.StringIO()):
					tex_generator.generate_tex(si_style, 'large.out', 'def2-SVP', '0', '1', '-1000.0', 'tddft', [], coords, state_blocks, energies, wavelengths, f_osc)
				result = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'large.tex'], capture_output=True, text=True, errors='replace', timeout=120)
				self.assertEqual(result.returncode, 0, result.stdout[-1500:])
				with open('large.log', errors='replace') as f:
					self.assertNotIn(r'Overfull \vbox', f.read())

	@unittest.skipUnless(shutil.which('pdflatex'), 'pdflatex is not installed')
	def test_tex_files_compile(self):
		for name in ('orca_opt_freq.out', 'orca_tddft.out'):
			for si_style in (7, 8, 9):
				with self.subTest(file=name, si_style=si_style):
					self.generate(si_style, name)
					result = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', f'{name[:-3]}tex'], capture_output=True, text=True, errors='replace', timeout=120)
					self.assertEqual(result.returncode, 0, result.stdout[-1500:])


if __name__ == '__main__':
	unittest.main()
