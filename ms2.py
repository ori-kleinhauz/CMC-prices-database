from ms1 import load_class
import argparse
from Class_DB import DB

def main():
    """ uses the argparse module to read the user's mysql password and the database name from the command line. then,
    reads the dataframes dictionary created by ms1.py. updates the database if exists, otherwise creates and
    populates it """
    parser = argparse.ArgumentParser()
    parser.add_argument('password', help='mysql password', type=str)
    parser.add_argument('db_name', help='database name', type=str)
    args = parser.parse_args()
    dictionary = load_class()
    con, empty = dictionary.create_connection(args.db_name, args.password)
    if not empty:
        dictionary.update_rates(con)
    else:
        dictionary.create_tables(con)
        dictionary.insert_coins(con)
        dictionary.insert_rates(con)


if __name__ == '__main__':
    main()
