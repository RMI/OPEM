import collections
from dataclasses import asdict, dataclass
from typing import DefaultDict, List


def visit_dict(d, path=[]):
    for k, v in d.items():
        if not isinstance(v, dict):
            yield path + [k], v
        else:
            yield from visit_dict(v, path + [k])


def initialize_from_dataclass(target, source: DefaultDict):
    # this allows us to get input from a dict generated from another dataclass
    for key in source.keys():
        if key in asdict(target).keys():

            for path in visit_dict(source[key]):
                # print(user_input[key])

                if len(path[0]) == 1:
                    print('path length = 1')
                    print(source[key])
                    setattr(target, key, source[key][path[0]])
                else:

                    keys_length = len(path[0]) - 1
                # get a reference to the object the holds the key/value pair we want to mutate
                    ref = nested_access(
                        dict=getattr(target, key), keys=path[0][0:keys_length])

                    ref[path[0][-1]] = path[-1]


def nested_access(dict, keys):
    for key in keys:
        dict = dict[key]
    return dict


def initialize_from_list(target, source: List):
    # this allows us to get input from csv
    print('default values')
    print(target.product_name)
    print(target.transport_mode)
    print(target.transport_fuel_share)
    for row in source:
        if len(row) == 2:
            setattr(target, row[0], row[1])
        else:
            print('keys from input row')
            print(row[1:-2])
            # get a reference to the object the holds the key/value pair we want to mutate
            ref = nested_access(
                dict=getattr(target, row[0]), keys=row[1:-2])
            ref[row[-2]] = row[-1]



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
