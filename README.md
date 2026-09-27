# pySupport
pySupport is a python script for automatically generating computational details from an Orca or Gaussian output file for the Supporting Information (SI) of a scientific journal.

This script is based on the CSIgen repository from wongzit (https://github.com/wongzit/CSIgen.git) who developed a script for Gaussian output files.

## Usage
The script can be called directly from the command line using Python3 with the ORCA or Gaussian output file as argument. Both .log and .out files are supported.
```
python3 pySupport.py calculation.out
```

For the simultaneous processing of multiple files, they can be listed as arguments in a row:

```
python3 pySupport.py calc1.out calc2.log calc3.out
```

The build-in menu offers different options of formatting the SI output. You can choose between simple text ```txt```, Excel ```xlsx```, or LaTeX ```tex``` by entering a number between 1 and 11:

```
--- Supporting Information Styles ---
 [1] Full (.txt)
 [2] Simple (.txt)
 [3] Coordinates only (.txt)
 [4] Full (.xlsx)
 [5] Simple (.xlsx)
 [6] Coordinates only (.xlsx)
 [7] Full (.tex)
 [8] Simple (.tex)
 [9] Coordinates only (.tex)
 [10] XYZ file (ORCA style)
 [11] XYZ File (Gaussian style)
Please enter a number for the SI style:
```

> [!NOTE]
>
> In case of processing multiple files with Excel output, all files will be combined in a single Excel file named ```SI_output.xlsx``` with each calculation output on one separate sheet. Text and LaTeX files will be generated separately.
>
> All output files are saved next to the input file, ```SI_output.xlsx``` next to the first one.

### Supporting Information Styles

#### Full

The ```Full``` format style prints **file name**, **basis set**, **charge** and **multiplicity**, **electronic energy** as well as the **cartesian coordinates**. For a frequency calculation **imaginary frequencies** and the **thermochemistry** (zero-point, thermal, enthalpy and free energy) will be listed additionally.

#### Simple

The ```Simple``` format style prints **file name**, **basis set**, **charge** and **multiplicity**, **electronic energy** as well as the **cartesian coordinates**.

#### Coordinates only

The ```Coordinates only``` format style will only print **file name** and **cartesian coordinates**.

#### TD-DFT

For TD-DFT calculations every style can add a table of the excited states with **orbital contributions**, **HOMO/LUMO notation**, **energy**, **wavelength** and **oscillator strength**. As in ORCA, orbitals are counted from 0 and contributions are given as weights, also for Gaussian.

#### LaTeX

Tables continue over several pages (```longtable```). Compile two or three times or use ```latexmk```.

### XYZ File Generation

Modes [10] and [11] generate XYZ files from the loaded calculation files in ORCA or Gaussian style, respectively. The difference between those two types is that the ORCA files starts with the number of atoms in the first and a comment in the second line, while Gaussian only uses the atomic coordinates.

## Requirements

pySupport needs Python 3.12 or newer and was tested with Python 3.12 and 3.13. For the generation of Excel output files, the library openpyxl 3.1.5 is necessary. All requirements are listed in ```requirements.txt```.

## Tests

```
python3 -m unittest discover -s tests
```

## Contact

Alexander Krappe – rubialab@rubialab.de

Project link – [https://github.com/RubiaLab/pySupport](https://github.com/RubiaLab/pySupport)

## License

Distributed under the MIT License. See ```LICENSE``` for more information.



