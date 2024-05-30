import os

def create_directory_structure(base_path, structure):
    for entry, sub_structure in structure.items():
        entry_path = os.path.join(base_path, entry)
        if sub_structure is None:
            # It's a file, create an empty file
            open(entry_path, 'a').close()
        else:
            # It's a directory, create it and its substructure
            os.makedirs(entry_path, exist_ok=True)
            init_file = os.path.join(entry_path, '__init__.py')
            open(init_file, 'a').close()  # Create an empty __init__.py file
            create_directory_structure(entry_path, sub_structure)

# Define the directory structure
directory_structure = {
    'tests': {
        'core': {
            'test_converter.py': None,
            'test_config.py': None,
            'test_utils.py': None,
        },
        'explorer': {
            'misc': {
                'test_gold_price.py': None,
                'test_exchange_rate.py': None,
            },
            'msn': {
                'test_models.py': None,
                'test_quote.py': None,
            },
            'vci': {
                'test_company.py': None,
                'test_analysis.py': None,
                'test_models.py': None,
                'test_quote.py': None,
            },
            'tcbs': {
                'test_company.py': None,
                'test_analysis.py': None,
                'test_models.py': None,
                'test_quote.py': None,
            },
        },
        'common': {
            'test_data_explorer.py': None,
        },
    }
}

# Define the base path for the project
base_path = '/Users/mrthinh/Library/CloudStorage/OneDrive-Personal/Github/vnstock'

# Create the directory structure
create_directory_structure(base_path, directory_structure)

print("Directory structure created successfully.")
