import csv
from opem import input
# opem.input.user_input_dto
# we will have a script to prompt user and take input
# don't worry about that here. What functions will that script call?

# what is hardcoded now but will change in the future?
# --product slates
# --transportation


def initialize_model_inputs(get_input_func, validate_input_func):

    all_input = get_input_func(validate_input)
    all_input_dtos = initialize_params(all_input)
    #product_slate = fetch_product_slate()
    # return all_input_dtos, product_slate

############################################

# we will take input as 2d csv, then turn into multi-d nested dict.
# dict should be dataclass with default values


def get_csv_input(validate_input_func):
    # find csv from path or on cwd
    # read csv
    # what datatype does this return?
    # try DictReader class, have one column for keys, one for values, then iterate
    all_user_input = {}
    with open('input.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                validate_input_func(row)
            except ValueError:
                ValueError("input is invalid!")
            all_user_input[row[0]] = row[1]
        print(all_user_input)
    return all_user_input


def validate_input(row):
    # check if input params are valid
    print('validating row')
    print(row)


def initialize_params(all_input):
    # fill in parameter object with user defined or default params
    print("input dict")
    print(all_input)
    combustion_input = initialize_combustion_dto(all_input)
    # transportation input =
    # return {comb: combustion_input, trans: transportation_input}


def initialize_combustion_dto(all_input):
    combustion_input = input.user_input_dto.CombustionInputDto(**all_input)
    print('COMBUSTION INPUT')
    print(combustion_input)
    return combustion_input


def initialize_transport_dto():
    pass


def initialize_product_slate_dto():
    pass


def fetch_product_slate():
    # read user selection from csv input and fetch respective slate
    # slate objects stored as dataclass with default values
    pass
    #####################################################
