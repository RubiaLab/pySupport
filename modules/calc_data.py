import os
from dataclasses import dataclass, field

@dataclass
class CalcData:
	#Results of an ORCA or Gaussian output file for the Supporting Information
	filename: str
	basis_set: str = 'unknown'
	charge: str = ''
	multiplicity: str = ''
	total_energy: str = ''
	jobtype: str = 'other'
	imaginary_freqs: list = field(default_factory=list)
	thermochemistry: dict = field(default_factory=dict)
	coords: list = field(default_factory=list)
	homo: dict = field(default_factory=dict)
	state_blocks: list = field(default_factory=list)
	spins: list = field(default_factory=list)
	energies: list = field(default_factory=list)
	wavelengths: list = field(default_factory=list)
	f_osc: list = field(default_factory=list)

	@property
	def file(self):
		#Name of the output file, used as title in the Supporting Information
		return os.path.basename(self.filename)

	@property
	def output_base(self):
		#Path of the output file without extension, the Supporting Information is written next to it
		return os.path.splitext(self.filename)[0]

	def atoms(self):
		#Element symbol and cartesian coordinates of every atom, e.g. ['C', '0.000000', '1.342425', '0.000000']
		return [line.split()[:4] for line in self.coords]

	def state_label(self, n):
		#Label of the n-th excited state (counted from 0): S1, S2, ... and T1, T2, ... if singlets and triplets were calculated, otherwise 1, 2, ...
		if {'S', 'T'} <= set(self.spins):
			return f'{self.spins[n]}{self.spins[:n + 1].count(self.spins[n])}'
		return str(n + 1)

	def homo_lumo(self, contribution, arrow):
		#HOMO/LUMO notation of an orbital contribution relative to the HOMO of its spin, e.g. ['242', '244', 0.88] -> 'H-1 -> L'
		names = []
		for orbital in contribution[:2]:
			spin = orbital[-1] if orbital[-1] in 'ab' else ''
			if spin not in self.homo:
				return ''
			offset = int(orbital.removesuffix(spin)) - self.homo[spin]
			if offset <= 0:
				names.append('H' if offset == 0 else f'H{offset}')
			else:
				names.append('L' if offset == 1 else f'L+{offset - 1}')
		return f' {arrow} '.join(names)
