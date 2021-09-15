import codecs
import csv
import json

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from opem.input import input_lookup
from opem.products import product_slates

from opem.products.product_slate import ProductSlate
from opem.utils import isfloat


def initialize_model_inputs(get_input_func, validate_input_func):

    all_input = get_input_func(validate_input_func)

    # SHORTCUT--bypass user_input_dto and go straight to the
    # model objects. That means this returns the list
    # of lists we read from the csv

    # try:
    #     all_input_dto = UserInputDto(input_list=all_input)
    # except ValueError:
    #     print('Problem initializing user input. Please check your input parameters')
    #     raise
    return all_input

############################################

# we will take input as 2d csv, then turn into multi-d nested dict.
# dict should be dataclass with default values


def get_csv_input(validate_input_func):
    # find csv from path or on cwd
    # read csv
    # what datatype does this return?
    # try DictReader class, have one column for keys, one for values, then iterate
    input_lookup = create_lookup_table()

    all_user_input = []
    try:
        with open('opem_input.csv', newline='', encoding="utf-8-sig") as csvfile:

            reader = csv.reader(csvfile)

            for row in reader:
                try:
                    validate_input_func(row)
                except ValueError:
                    raise ValueError("input is invalid!")
                # lambda function here to get nesting of arbitrary depth
                # lambda: for each item in row if index(row[item]) exists
                # then all_user_input[row] = {}
                if row[0] != "":
                    try:
                        all_user_input.append(
                            input_lookup[create_key_from_csv(row[:4])] + [float(row[4]) if isfloat(row[4]) else row[4]])
                    except KeyError:
                        print(
                            f"Name {row[:4]} does not match expected user input.")
                        print("Ignoring this input and using defaults.")
    except FileNotFoundError:
        raise FileNotFoundError(
            "Please include opem_input.csv in your current working directory!")

    return all_user_input


def validate_input(row):
    # check if input params are valid
    pass


def create_key_from_csv(row):
    return "".join(row)


def create_lookup_table():
    input_keys = []
    indexing_paths = []
    ref = pkg_resources.files(
        input_lookup).joinpath("input_lookup.csv")
    # if only 'utf-8' is specified then BOM character '\ufeff' is included in output
    utf8_reader = codecs.getreader("utf-8-sig")
    with ref.open('rb') as csvfile:
        reader = csv.reader(utf8_reader(csvfile))
        for row in reader:
            if row[0] != '':
                split_array_index = row.index("`")
                input_keys.append(create_key_from_csv(row[:split_array_index]))
                indexing_paths.append(row[split_array_index+1:])
    lookup_table = dict(zip(input_keys, indexing_paths))
    return lookup_table


def get_product_slate_json(product_name: str):
    # read user selection from csv input and fetch respective slate
    # slate objects stored as dataclass with default values

    with pkg_resources.read_text(
            product_slates, f"{product_name}.json") as json_file:
        product_slate_json = json.load(json_file)
    try:
        # product slate has default vals in its dictionaries
        # so we don't unpack the json. Send it as an object
        # to be processed by __post__init function
        return ProductSlate(user_input=product_slate_json, product_name=product_slate_json["product_name"])
    except TypeError:
        print(
            'Problem initializing product slate. Please check your input parameters')
        raise


def get_product_slate_csv(product_name: str):
    # read user selection from csv input and fetch respective slate
    # slate objects stored as dataclass with default values

    ref = pkg_resources.files(
        product_slates).joinpath("all_product_slates.csv")
    # if only 'utf-8' is specified then BOM character '\ufeff' is included in output
    utf8_reader = codecs.getreader("utf-8-sig")
    with ref.open('rb') as csvfile:
        reader = csv.reader(utf8_reader(csvfile))
        all_product_slates = []
        for row in reader:
            all_product_slates.append(row)
        selected_index = all_product_slates[0].index(product_name)
        table_names = ["volume_flow_bbl", "energy_flow_MJ", "mass_flow_kg"]
        name_index = 0
        input_paths = []

    for row in all_product_slates[3:]:
        if row[0] in table_names and name_index < 2:
            name_index += 1
        else:
            input_paths.append([table_names[name_index], row[0],
                                "Flow", float(row[selected_index])])
    return ProductSlate(user_input=input_paths, product_name=product_name)
