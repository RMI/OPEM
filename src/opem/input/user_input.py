from dataclasses import InitVar, asdict, dataclass, field
from typing import Any, Dict, List
from opem.utils import build_dict_from_defaults, initialize_from_dataclass, initialize_from_list, read_input_structure


# hold validated user input


@dataclass
class UserInput:

    def __post_init__(self, user_input):

        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:

            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    # user inputs global model scope
    # Assay (Select Oil

    percent_ngl_c2_to_ethylene: float = 0

    product_name: str = None
    upstream_field_selection: str = None

    ngl_volume_source: int = 2
    gas_production_volume: int = 0
    oil_production_volume: int = 0
    ngl_c2_volume: int = 0
    ngl_c3_volume: int = 0
    ngl_c4_volume: int = 0
    ngl_c5plus_volume: int = 0
    opgee_coke_mass: int = 0

    # if ngl_volume_source==1 this must come from user input
    total_field_ngl_volume_user_input: int = None

    GWP: int = 100

   # input obj, bypasses default constructor (implicit __init__) and is passed to __post_init__
    user_input: InitVar[List] = []
   # table name passed into the build_dict_from_defaults function is
   # the same as the field name in the relevant object (because the table name
   # param will be compared with the input lookup csv table)
   # in the other objects this function takes a string corresponding to
   # the csv file name (slightly different from the corresponding attribute name)
   # I should change the csv names and attribute names to match.

    refinery_product_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults("refinery_product_combustion", read_defaults=read_input_structure))

    coke_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults("coke_combustion", read_defaults=read_input_structure))

    natural_gas_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults("natural_gas_combustion", read_defaults=read_input_structure))

    ngl_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults("ngl_combustion", read_defaults=read_input_structure))

    combustion_results: Dict = field(
        default_factory=lambda: build_dict_from_defaults("combustion_results", read_defaults=read_input_structure))

    product_combustion_emission_factors_petroleum: Dict = field(
        default_factory=lambda: build_dict_from_defaults("product_combustion_emission_factors_petroleum", read_defaults=read_input_structure))

    product_combustion_emission_factors_derived_solids: Dict = field(
        default_factory=lambda: build_dict_from_defaults("product_combustion_emission_factors_derived_solids", read_defaults=read_input_structure))

    energy_intensity_of_pipeline_transportation: Dict = field(
        default_factory=lambda: build_dict_from_defaults("energy_intensity_of_pipeline_transportation", read_defaults=read_input_structure))

    share_of_pipeline_technologies_used: Dict = field(
        default_factory=lambda: build_dict_from_defaults("share_of_pipeline_technologies_used", read_defaults=read_input_structure))

    energy_intensity_of_rail_transportation: Dict = field(
        default_factory=lambda: build_dict_from_defaults("energy_intensity_of_rail_transportation", read_defaults=read_input_structure))

    truck_fuel_economy_and_resultant_energy_consumption: Dict = field(
        default_factory=lambda: build_dict_from_defaults("truck_fuel_economy_and_resultant_energy_consumption", read_defaults=read_input_structure))
# should this move up?
#    select_biodiesel: Dict = field(
#         default_factory=lambda: build_dict_from_defaults(, read_defaults=read_input_structure))

    truck_emission_factors_of_fuel_combustion_origin_to_destination: Dict = field(
        default_factory=lambda: build_dict_from_defaults("truck_emission_factors_of_fuel_combustion_origin_to_destination", read_defaults=read_input_structure))

    truck_emission_factors_of_fuel_combustion_destination_to_origin: Dict = field(
        default_factory=lambda: build_dict_from_defaults("truck_emission_factors_of_fuel_combustion_destination_to_origin", read_defaults=read_input_structure))

    cargo_payload: Dict = field(
        default_factory=lambda: build_dict_from_defaults("cargo_payload", read_defaults=read_input_structure))

    tanker_barge_average_speed: Dict = field(
        default_factory=lambda: build_dict_from_defaults("tanker_barge_average_speed", read_defaults=read_input_structure))

    tanker_barge_energy_consumption_origin_to_destination: Dict = field(
        default_factory=lambda: build_dict_from_defaults("tanker_barge_energy_consumption_origin_to_destination", read_defaults=read_input_structure))

    tanker_barge_energy_consumption_destination_to_origin: Dict = field(
        default_factory=lambda: build_dict_from_defaults("tanker_barge_energy_consumption_destination_to_origin", read_defaults=read_input_structure))

    marine_fuel_properties_consumption: Dict = field(
        default_factory=lambda: build_dict_from_defaults("marine_fuel_properties_consumption", read_defaults=read_input_structure))

    fraction_of_fuel_type_for_transport_mode: Dict = field(
        default_factory=lambda: build_dict_from_defaults("fraction_of_fuel_type_for_transport_mode", read_defaults=read_input_structure))

    transport_distance: Dict = field(
        default_factory=lambda: build_dict_from_defaults("transport_distance", read_defaults=read_input_structure))

    emission_ratios_by_fuel_type_relative_to_baseline_fuel: Dict = field(
        default_factory=lambda: build_dict_from_defaults("emission_ratios_by_fuel_type_relative_to_baseline_fuel", read_defaults=read_input_structure))
