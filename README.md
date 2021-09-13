Instructions:

There are two ways to install the OPEM package: 

1) download the source code and install in editable mode (best option for those who want to make changes to the code);
2) download the .whl or .tar.gz file from the latest release and install with pip


INSTRUCTIONS FOR OPTION 1:

Clone this repo to your local machine:

```
git clone https://github.com/zacharyschmidt/opem.git
``` 
or
```
git clone git@github.com:zacharyschmidt/opem.git
```

Once you have a local copy of the repo, navigate to the same directory as the setup.py file and create a virtual environment:

```
python -m venv venv
```

Activate the virtual environment:

```
source venv/bin/activate
```

Then run the command below to install the package in 'editable' mode (make sure you are in the same directory as the setup.py file). Any changes you make to the source code will automatically update the locally installed package.

```
pip install -e .
```


INSTRUCTIONS FOR OPTION 2:

Click on 'Releases', located in the rightmost section of the repository page (beneath 'About').

Find the latest release and open the 'Assets' dropdown. Then download either the .whl or .tar.gz file.

Set up and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate
```

Use pip to install OPEM from the downloaded file. For example, if you have a .whl file in your current working directory:

```
pip install opem-1.0.1a0-py3-none-any.whl
```


Once the installation is complete you can run opem from anywhere on your local machine with the terminal command 'opem' (make sure the virtual environment is activated).

opem will look for a file named 'opem_input.csv' in your current working directory. An example input file is included. You can make changes to the values in column E to provide user input (don't change any other columns). Blank cells in column E will be ignored.

If it can find 'opem_input.csv' the program will run and write results to a new file 'opem_output.csv', saved to your current working directory.

The input and output files are based on the 'OPEM Input Outputs' excel workbook created by Raghav (included in this repo). Please refer to this workbook to see how the names in the input/output csv filed map to parameters in the OPEM1.1 workbook.


