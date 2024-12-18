## To run test cases:

- Navigate to the directory containing the setup.py file for this package.

### To run all test cases:

```bash 
python setup.py pytest
```

### To run individual file:

```bash 
python setup.py pytest --addopts "<path_to_your_test_file>"

# example : python setup.py pytest --addopts "tests/test_basic.py"
```
