from dataclasses import InitVar, asdict, dataclass, field
from typing import Any, Dict, List
from opem.utils import build_dict_from_defaults, initialize_from_dataclass, initialize_from_list, read_input_structure

# hold validated user input


@dataclass
class OpgeeInput:

    def __post_init__(self, input_list):
        if type(input_list) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, input_list)
        elif type(input_list) == list:
            initialize_from_list(self, input_list)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")
	    

    # user inputs global model scope
    # Assay (Select Oil)
    gas_production_volume: int = 600000 
    oil_production_volume: int = 100000 
    ngl_c2_volume: int = 0 
    ngl_c3_volume: int = 0 

    ngl_c4_volume: int = 0
    ngl_c5plus_volume: int = 0
    total_field_ngl_volume: int = 0
    opgee_coke_mass: int = 0
   
    

    
    
    
    
    

   # input obj, bypasses default constructor (implicit __init__) and is passed to __post_init__
    input_list: InitVar[List] = []
   