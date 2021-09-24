import collections
import csv
from dataclasses import asdict, dataclass
from typing import Dict, List
import codecs
import math

import pkg_resources



"""
@param func_to_apply: function
     this is a user defined function that will return a value to be 
     written to the table cell that this function navigates to.
     it takes row_key and col_key as arguments 

@param other_tables_keymap: dict
     should be of the form 
     {
         other_table_1: {
             row_keymap: {"[target_table_key]": "[other_table_key]"}, 
             col_keymap: {"[target_table_key]": "[other_table_key]"}},

        other_table_1: {
             row_keymap: {"[target_table_key]": "[other_table_key]"}, 
             col_keymap: {"[target_table_key]": "[other_table_key]"}},
            
     }
     for other_table name use the "full_table_name" table attribute. 
      example: f"{self.product_slate.mass_flow_kg['full_table_name']}"

@param extra: dict
      used to pass extra config into function

"""


def fill_calculated_cells(target_table_ref, func_to_apply, other_table_refs=None,  included_rows=[], included_cols=[], excluded_rows=[], excluded_cols=[], other_tables_keymap={}, extra={}):
    if (included_rows and excluded_rows):
        raise ValueError(
            "Please only pass arguments for one of excluded_rows/included_rows, not both")
    if (included_cols and excluded_cols):
        raise ValueError(
            "Please only pass arguments for one of excluded_cols/included_cols, not both")

    temp_target_table_ref = target_table_ref
    # sometimes the target_table_ref is a ref to the table (in form of dict),
    # sometimes it is in the form of {"[table name]" : target_table_ref} --
    # the second form lets us access the table by its tablename in func_to_apply
    # so that it is easier to read. When we use the second form we also include
    # {"[table name]" : target_table_ref, "has_wrapper": True }
    # this lets us perform the check below to handle both forms in this function
    if target_table_ref.get("has_wrapper"):
        for key in target_table_ref:
            if key != "has_wrapper":
                temp_target_table_ref = target_table_ref[key]

    # handle included rows/ cols as well
    for row_key, row in temp_target_table_ref.items():
        # skip label for the row index and full table name and
        if row_key not in ["row_index_name", "full_table_name"] \
                and (not excluded_rows or (row_key not in excluded_rows)) and (not included_rows or (row_key in included_rows)):
            # handle column that needs special treatment
            for col_key in row.keys():

                if (not excluded_cols or (col_key not in excluded_cols)) and (not included_cols or (col_key in included_cols)):
                    # get a reference to current cell and write calculated value
                    row[col_key] = func_to_apply(
                        row_key, col_key, target_table_ref, other_table_refs, other_tables_keymap, extra)


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def read_input_structure(table_name):
    from opem.input.user_input import create_lookup_table
    lookup_table = create_lookup_table().values()
    
    inputs_table_format = [[""]]
    visited_rows = []
    for row in lookup_table:
        if row[0] == table_name:
            if not row[2] in inputs_table_format[0]:
               inputs_table_format[0].append(row[2])
            if not row[1] in visited_rows:
               inputs_table_format.append([row[1]])
               visited_rows.append(row[1])
    num_cols = len(inputs_table_format[0])-1
    for row in inputs_table_format[1:]:
        for _ in range(num_cols): 
            row.append("")
    return inputs_table_format


def read_model_table_defaults(table_name):
     rows_and_header = []
     csvfile = pkg_resources.resource_stream(
        "opem.defaults", f"{table_name}.csv")
    # if only 'utf-8' is specified then BOM character '\ufeff' is included in output
     utf8_reader = codecs.getreader("utf-8-sig")
     reader = csv.reader(utf8_reader(csvfile))
     for row in reader:
         rows_and_header.append(row)
     return rows_and_header


def build_dict_from_defaults(table_name, read_defaults=read_model_table_defaults):
    # we should be able to pass in a different read_model_table_defaults
    # function here. should implement a version that reads from memory instead
    # of disk for more speed.
      table_array = read_defaults(table_name)
     
      defaults = {}
      headers = table_array[0]
      defaults["full_table_name"] = table_name
      defaults['row_index_name'] = headers[0]
      for row in table_array[1:]:
        if row[0] != '':
            defaults[row[0]] = {k: float(v) if isfloat(v) else v for (k, v) in filter(
                lambda x: True if (x[0] != '' and x[1] != '') else False, zip(headers[1:], row[1:]))}    
      return defaults


    


def visit_dict(d, path=[]):

    for k, v in d.items():
        if not isinstance(v, dict):
            yield path + [k], v
        else:
            yield from visit_dict(v, path + [k])


def initialize_from_dataclass(target, source: Dict):
    # this allows us to get input from a dict generated from another dataclass
    target_keys = asdict(target).keys()
    for key in source.keys():
        if key in target_keys:
            if type(source[key]) != dict:
                if source[key] != '':
                   setattr(target, key, source[key])
            else:
                for path in visit_dict(source[key]):

                    # if len(path[0]) == 1:
                    #     print("lenth of path is 1")
                    #     setattr(target.key, [path[0][0]],
                    #             [path[0][1]])
                    #     # setattr(target, key, source[key][path[0][0]])
                    # else:

                    keys_length = len(path[0]) - 1
                    # get a reference to the object the holds the key/value pair we want to mutate
                    if path[-1] != '':
                       ref = nested_access(
                           dictionary=getattr(target, key), keys=path[0][0:keys_length])
                    #if not math.isnan(path[-1]):
                       ref[path[0][-1]] = path[-1]


def nested_access(dictionary, keys):

    for key in keys:
        try:
          dictionary = dictionary[key]
        except KeyError:
          print(dictionary) 
          print(f"Key {key} not recognized. There is probably an error in input_lookup.csv")
    return dictionary


def initialize_from_list(target, source: List):
    # this allows us to get input from csv

    target_keys = asdict(target).keys() 
    
    for row in source:
        if row[0] in target_keys:
            if row[0] == "product_name":
                print("found product!")
                print(row[0])
            # test if this is a path to a primitive datatype (as opposed to nested
            # dictionary)
            if row[1] == "" and row[-1] != "":
                setattr(target, row[0], row[-1])
            elif row[1] != "" and row[-1] != "":
                # get a reference to the object the holds the key/value pair we want to mutate

                ref = nested_access(
                    dictionary=getattr(target, row[0]), keys=row[1:-2])
                ref[row[-2]] = row[-1]


def write_csv_output(output, path="opem_output.csv"):

    with open(path, "w", newline='', encoding="utf-8-sig") as csvfile:

        writer = csv.writer(csvfile)

        for row in output:
            writer.writerow(row)


######################### NOT USED #######################


def isDict(d):
    return isinstance(d, collections.Mapping)


def isAtomOrFlat(d):
    return not isDict(d) or not any(isDict(v) for v in d.values())


def leafPaths(nestedDicts, noDeeper=isAtomOrFlat):
    """
        For each leaf in NESTEDDICTS, this yields a 
        dictionary consisting of only the entries between the root
        and the leaf.
    """
    for key, value in nestedDicts.items():
        if noDeeper(value):
            yield {key: value}
        else:
            for subpath in leafPaths(value):
                yield {key: subpath}
###########################################################
