import sys
import argparse
from config import PROGRAM_NAME, PROGRAM_DESCRIPTION
from lexer import lex_file_data

def create_arg_parser():
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description=PROGRAM_DESCRIPTION)

    parser.add_argument('filename')
    parser.add_argument('-v', '--verbose', action='store_true')
    
    return parser

def open_file(filename):
    try:
        with open(filename, "r") as file:
            data = file.read()
    except FileNotFoundError:
        print(f'Error: file "{filename}" not found.')
        sys.exit(1)
    except PermissionError:
        print(f'Error: Permission denied for "{filename}".')
        sys.exit(1)
    except OSError as e:
        print(f'Error opening file "{filename}": {e}')
        sys.exit(1)
    
    return data 

def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    file = {"name": args.filename, 
            "lines": open_file(args.filename).split("\n")}
    tokens = lex_file_data(file)
    print(tokens)

if __name__ == '__main__':
    main()
