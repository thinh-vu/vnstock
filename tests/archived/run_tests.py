import unittest
import logging
import os
import sys
from datetime import datetime

# Create results directory inside tests if it does not exist
results_dir = os.path.join('tests', 'results')
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# Define a custom test runner to log results
class LoggingTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwargs):
        self.log_filename = kwargs.pop('log_filename', None)
        super().__init__(*args, **kwargs)

    def run(self, test):
        result = super().run(test)
        if self.log_filename:
            with open(self.log_filename, 'a') as log_file:
                for test, err in result.errors:
                    log_file.write(f"ERROR: {test}\n{err}\n")
                for test, err in result.failures:
                    log_file.write(f"FAIL: {test}\n{err}\n")
        return result

def main():
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
    else:
        print("Please provide the test file or test case to run. For example:")
        print("python run_tests.py tests.test_ema")
        print("python run_tests.py tests.test_ema.TestEMA.test_ema_normal_index")
        return

    # Configure logging
    test_file_name = test_name.split('.')[1] if '.' in test_name else test_name
    log_filename = os.path.join(
        results_dir, 
        f'{test_file_name}_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    )
    logging.basicConfig(
        filename=log_filename,
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    logging.info(f"Starting test suite {test_name}")
    
    # Run the specified test
    suite = unittest.defaultTestLoader.loadTestsFromName(test_name)
    runner = LoggingTestRunner(verbosity=2, log_filename=log_filename)
    runner.run(suite)
    
    logging.info(f"Test suite {test_name} finished")

if __name__ == '__main__':
    main()
