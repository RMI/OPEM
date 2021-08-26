import csv
import json
from opem.input.user_input_dto import UserInputDto
from opem.products.product_slate import ProductSlate
import pkg_resources


from opem import input
# opem.input.user_input_dto
# we will have a script to prompt user and take input
# don't worry about that here. What functions will that script call?

# what is hardcoded now but will change in the future?
# --product slates
# --transportation


def initialize_model_inputs(get_input_func, validate_input_func):

    all_input = get_input_func(validate_input)
    try:
        all_input_dto = UserInputDto(input_list=all_input)
    except ValueError:
        print('Problem initializing user input. Please check your input parameters')
        raise
    return all_input_dto

############################################

# we will take input as 2d csv, then turn into multi-d nested dict.
# dict should be dataclass with default values


def get_csv_input(validate_input_func):
    # find csv from path or on cwd
    # read csv
    # what datatype does this return?
    # try DictReader class, have one column for keys, one for values, then iterate
    all_user_input = []
    with open('input.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                validate_input_func(row)
            except ValueError:
                ValueError("input is invalid!")
            # lambda function here to get nesting of arbitrary depth
            # lambda: for each item in row if index(row[item]) exists
            # then all_user_input[row] = {}
            all_user_input.append(row)
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

    # = initialize_combustion_dto(all_input)
    # transportation input =
    # return {comb: combustion_input, trans: transportation_input}


# def initialize_combustion_dto(all_input):
#     combustion_input = input.user_input_dto.CombustionInputDto(**all_input)
#     print('COMBUSTION INPUT')
#     print(combustion_input)
#     return combustion_input


def get_product_slate(product_name: str):
    # read user selection from csv input and fetch respective slate
    # slate objects stored as dataclass with default values

    with pkg_resources.resource_stream(
            "opem.products.product_slates", f"{product_name}.json") as json_file:
        product_slate_json = json.load(json_file)
    print(product_slate_json)
    try:
        return ProductSlate(**product_slate_json)
    except TypeError:
        print(
            'Problem initializing product slate. Please check your input parameters')
        raise
