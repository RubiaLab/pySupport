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

The build-in menu offers different options of formatting the SI output. You can choose between simple text ```txt```, Excel ```xlsx```, or LaTeX ```tex``` by entering a number between 1 and 9:

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
Please enter a number for the SI style:
```

> [!NOTE]
>
> In case of processing multiple files with Excel output, all files will be combined in a single Excel file named ```SI_output.xlsx``` with each calculation output on one separate sheet. Text and LaTeX files will be generated separately.

### Supporting Information Styles

#### Full

The ```Full``` format style prints **file name**, **basis set**, **charge** and **multiplicity**, **electronic energy** as well as the **cartesian coordinates**. For a frequency calculation **imaginary frequencies** will be listed additionally.

#### Simple

The ```Simple``` format style prints **file name**, **basis set**, **charge** and **multiplicity**, **electronic energy** as well as the **cartesian coordinates**.

#### Coordinates only

The ```Coordinates only``` format style will only print **file name** and **cartesian coordinates**.

## Requirements

The code was tested using Python 3.13.1. For the generation of Excel output files, the library openpyxl 3.1.5 is necessary. All requirements are listed in ```requirements.txt```.

## Contact

Alexander Krappe – rubialab@rubialab.de

Project link – [https://github.com/RubiaLab/pySupport](https://github.com/RubiaLab/pySupport)

## License

Distributed under the MIT License. See ```LICENSE.txt``` for more information.



