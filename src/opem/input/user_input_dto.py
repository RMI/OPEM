from dataclasses import InitVar, asdict, dataclass, field
from typing import Any, Dict, List
from opem.utils import build_dict_from_defaults, initialize_from_list, read_input_structure

# hold validated user input


@dataclass
class UserInputDto:
    # should have % combusted
    # should validate % combusted
    # # should have user transport fuel selections
    # should validate fuel selections

    # we can validate in the post init method

    # transport fuel-type options

    # transportation user inputs

    # Pipeline_Emissions_Transport_Fuel: Any
    # Pipeline_Emissions_Distance_Traveled_km: Any
    # Rail_Emissions_Transport_Fuel: Any
    # Rail_Emissions_Distance_Traveled_km: Any
    # Heavy_Duty_Truck_Emissions_Transport_Fuel: Any
    # Heavy_Duty_Truck_Emissions_Distance_Traveled_km: Any
    # Ocean_Tanker_Emissions_Transport_Fuel: Any
    # Ocean_Tanker_Emissions_Distance_Traveled_km: Any
    # Barge_Emissions_Transport_Fuel: Any
    # Barge_Emissions_Distance_Traveled_km: Any
    def __post_init__(self, input_list):
        # this allows us to get input from csv
        print(input_list)
        
        initialize_from_list(self, input_list)

    

    # user inputs global model scope
    # Assay (Select Oil)
    gas_production_volume: int = 0 # should be NA
    oil_production_volume: int = 0 # should be NA
    ngl_c2_volume: int = 0 
    ngl_c3_volume: int = 0 

    ngl_c4_volume: int = 0
    ngl_c5plus_volume: int = 0
    total_field_ngl_volume: int = 0
    opgee_coke_mass: int = 0
    percent_ngl_c2_to_ethylene: float = 0

    product_name: str = "Default Product"
    upstream_field_selection: str = "Defualt Upstream Field"
    
    ngl_volume_source: int = 2
    
    

   # input obj, bypasses default constructor (implicit __init__) and is passed to __post_init__
    input_list: InitVar[List] = []
   # table name passed into the build_dict_from_defaults function is 
   # the same as the field name in the relevant object (because the table name
   # param will be compared with the input lookup csv table)
   # in the other objects this function takes a string corresponding to 
   # the csv file name (slightly different from the corresponding attribute name)
   # I should change the csv names and attribute names to match.

    transport_results: Dict = field(
        default_factory=lambda: build_dict_from_defaults("transport_results", read_defaults=read_input_structure))

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

    tanker_barge_average_speed: Dict = field(
        default_factory=lambda: build_dict_from_defaults("tanker_barge_average_speed", read_defaults=read_input_structure))

    marine_fuel_properties_consumption: Dict = field(
        default_factory=lambda: build_dict_from_defaults("marine_fuel_properties_consumption", read_defaults=read_input_structure))

    fraction_of_fuel_type_for_transport_mode: Dict = field(
        default_factory=lambda: build_dict_from_defaults("fraction_of_fuel_type_for_transport_mode", read_defaults=read_input_structure))

    emission_ratios_by_fuel_type_relative_to_baseline_fuel: Dict = field(
        default_factory=lambda: build_dict_from_defaults("emission_ratios_by_fuel_type_relative_to_baseline_fuel", read_defaults=read_input_structure))

    
    refinery_product_transport_mode_of_transport: Dict = field(default_factory=lambda: {"Pipeline Emissions": {
                                        "Transport Fuel": "Natural Gas", "Distance Traveled (km)": 2414},
                                "Rail Emissions": {
                                        "Transport Fuel": "Diesel", "Distance Traveled (km)": 0},
                                "Heavy-Duty Truck Emissions": {
                                        "Transport Fuel": "Diesel", "Distance Traveled (km)": 380},
    "Ocean Tanker Emissions": {
                                        "Transport Fuel": "Bunker Fuel", "Distance Traveled (km)": 0},
    "Barge Emissions": {
                                        "Transport Fuel": "Residual Oil", "Distance Traveled (km)": 0}})

    # table: Field NGL transport
    field_ngl_transport_mode_of_transport: Dict = field(default_factory=lambda: {"Pipeline Emissions": {
                                        "Transport Fuel": "Natural Gas", "Distance Traveled (km)": 2414},
            "Rail Emissions": {
                                        "Transport Fuel": "Diesel", "Distance Traveled (km)": 0},
            "Heavy-Duty Truck Emissions": {
                                        "Transport Fuel": "Diesel", "Distance Traveled (km)": 380},
            "Ocean Tanker Emissions": {
                                        "Transport Fuel": "Bunker Fuel", "Distance Traveled (km)": 0},
            "Barge Emissions": {
                                        "Transport Fuel": "Residual Oil", "Distance Traveled (km)": 0}})
 
    # transport_fuel_share: Dict = field(default_factory=lambda: {"Pipeline": {
    #     "Natural Gas": 0.11}})
    transport_fuel_options: List[str] = field(default_factory=lambda: ["Natural Gas", "LNG Diesel", "Bunker Fuel Residual Oil",
                                                                       "LPG DME FTD Biodiesel", "Renewable Diesel", "Renewable Gasoline", "Hydrogen", "Ethanol", "Methanol"])
    # user inputs combustion model scope
    # table: Refinery product combustion + Product Slate
    refinery_product_combustion_product_slate: Dict = field(default_factory=lambda: {"Gasoline": {
                                        "% Combusted": 1.0},
                            "Jet Fuel": {
                                        "% Combusted": 1.0},
"Diesel": {
                                        "% Combusted": 1.0},
    "Fuel Oil": {
                                        "% Combusted": 1.0},
    "Coke": {
                                        "% Combusted": 1.0},
    "Residual Fuels": {
                                        "% Combusted": 1.0},
  "Liquefied Petroleum Gases (LPG)": {
                                        "% Combusted": 1.0}})
    
    # table: Field product combustion (combination of all Field * Combustion tables) + Product Slate
    field_product_combustion_product_slate: Dict = field(default_factory=lambda: {"Coke": {
                                        "% Combusted": 1.0},
    "Natural Gas": {
                                        "% Combusted": 1.0},
 "Ethane": {
                                        "% Combusted": 1.0},
    
"Propane": {
                                        "% Combusted": 1.0},
    
"Butane": {
                                        "% Combusted": 1.0},
    
"Pentanes Plus": {
                                        "% Combusted": 1.0}})

