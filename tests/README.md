## Running the Script with Arguments
To run the entire test_quote.py file:

```sh
python3 run_tests.py tests.common.test_data_explorer
```
To run a specific test case within test_quote.py:

```sh
python3 run_tests.py tests.common.test_data_explorer.TestVnstock.test_vnstock_init_invalid_source
```
This custom script provides flexibility to run specific tests efficiently without modifying the script each time.

## Real examples

- Fmarket fund testing: `python3.10 -m unittest tests.explorer.fmarket.test_fund`