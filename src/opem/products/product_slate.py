from dataclasses import InitVar, dataclass, field
from typing import Any, DefaultDict

from opem.utils import initialize_from_dataclass, initialize_from_list


@dataclass
class ProductSlate:
    def __post_init__(self, product_name, user_input):
        self.product_name = product_name

        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    product_name: InitVar[str]

    # We will us an initvar and custom function to fill
    # the fields from json so that we don't overwrite
    # any default values in the dictionary fields
    user_input: InitVar[DefaultDict] = {}
    volume_flow: DefaultDict = field(default_factory=lambda:
                                     {
                                         "full_table_name": 'Volume Flow',
                                         "Crude_bbl": Any,
                                         "Gasoline_bbl": Any,
                                         "Jet_Fuel_bbl": Any,
                                         "Diesel_bbl": Any,
                                         "Fuel_Oil_bbl": Any,
                                         "Coke_bbl": Any,
                                         "Residual_fuels_bbl": Any,
                                         "Surplus_Refinery_Fuel_Gas_RFG_bbl": Any,
                                         "Liquefied_Petroleum_Gases_LPG_bbl": Any,
                                         "Petrochemical_Feedstocks_bbl": Any,
                                         "Asphalt_bbl": Any})

    energy_flow: DefaultDict = field(default_factory=lambda:
                                     {"full_table_name": 'Energy Flow',
                                         "Gasoline_MJ": Any,
                                         "Jet_Fuel_MJ": Any,
                                         "Diesel_MJ": Any,
                                         "Fuel_Oil_MJ": Any,
                                         "Coke_MJ": Any,
                                         "Residual_fuels_MJ": Any,
                                         "Surplus_RFG_MJ": Any,
                                         "Surplus_NCR_H2_MJ": Any,
                                         "Liquefied_Petroleum_Gases_LPG_MJ": Any,
                                         "Petrochemical_Feedstocks_MJ": Any,
                                         "Asphalt_MJ": Any,
                                         "Gasoline_S_wt_MJ": Any,
                                         "Gasoline_H2_wt_MJ": Any
                                      })

    mass_flow: DefaultDict = field(default_factory=lambda:
                                   {   # keys "full_table_name" and "row_index_name" will be ignored during iteration
                                       "full_table_name": "Mass Flow",
                                       "Gasoline_kg": Any,
                                       "Jet_Fuel_kg": Any,
                                       "Diesel_kg": Any,
                                       "Fuel_Oil_kg": Any,
                                       "Coke_kg": Any,
                                       "Residual_fuels_kg": Any,
                                       "Sulphur_kg": Any,
                                       "Surplus_RFG_kg": Any,
                                       "Surplus_NCR_H2_kg": Any,
                                       "Liquefied_Petroleum_Gases_LPG_kg": Any,
                                       "Petrochemical_Feedstocks_kg": Any,
                                       "Asphalt_kg": Any,
                                       "Net_Upstream_Petcoke_kg": Any,

                                   }
                                   )
