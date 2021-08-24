
# we will have a script to prompt user and take input
# don't worry about that here. What functions will that script call?

# what is hardcoded now but will change in the future?
# --product slates
# --transportation


def initialize_model_inputs():
    get_csv_input()
    validate_input()
    initialize_params()
    fetch_product_slate()

############################################

# we will take input as 2d csv, then turn into multi-d nested dict.
# dict should be dataclass with default values


def get_csv_input():
    # find csv from path or on cwd
    # read csv
    # what datatype does this return?
    # try DictReader class, have one column for keys, one for values, then iterate


def validate_input():
    # check if input params are valid


def initialize_params():
    # fill in parameter object with user defined or default params


def fetch_product_slate():
    # read user selection from csv input and fetch respective slate
    # slate objects stored as dataclass with default values

    #####################################################
