from dataclasses import InitVar, asdict, dataclass, field
from typing import Any, DefaultDict, List
from opem.utils import initialize_from_list, nested_access

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
        initialize_from_list(self, input_list)

    # input obj, bypasses default constructor (implicit __init__) and is passed to __post_init__
    input_list: InitVar[List] = []

    # user inputs global model scope
    # Assay (Select Oil)
    product_name: str = "Default Product"
    upstream_field_selection: str = "Defualt Upstream Field"
    ngl_volume_source: str = "1. GD NGL Volume"
    percent_ethane_volume_directly_sent_to_cracker_chem_plant_allocated_to_ethylene_conversion: float = 1.0

    # user inputs transport model scope
    # table: Refinery product transport + Mode of transport
    refinery_product_transport_mode_of_transport: DefaultDict = field(default_factory=lambda: {"Pipeline Emissions": {
                                        "Transport Fuel": "Natural Gas", "Distance Traveled (km)": 2414}})

    refinery_product_transport_mode_of_transport: DefaultDict = field(default_factory=lambda: {"Rail Emissions": {
                                        "Transport Fuel": "Diesel", "Distance Traveled (km)": 0}})

    refinery_product_transport_mode_of_transport: DefaultDict = field(default_factory=lambda: {"Heavy-Duty Truck Emissions": {
                                        "Transport Fuel": "Diesel", "Distance Traveled (km)": 380}})
    
    refinery_product_transport_mode_of_transport: DefaultDict = field(default_factory=lambda: {"Ocean Tanker Emissions": {
                                        "Transport Fuel": "Bunker Fuel", "Distance Traveled (km)": 0}})
    
    refinery_product_transport_mode_of_transport: DefaultDict = field(default_factory=lambda: {"Barge Emissions": {
                                        "Transport Fuel": "Residual Oil", "Distance Traveled (km)": 0}})

    # table: Field NGL transport
    field_ngl_transport_mode_of_transport: DefaultDict = field(default_factory=lambda: {"Pipeline Emissions": {
                                        "Transport Fuel": "Natural Gas", "Distance Traveled (km)": 2414}})

    field_ngl_transport_mode_of_transport: DefaultDict = field(default_factory=lambda: {"Rail Emissions": {
                                        "Transport Fuel": "Diesel", "Distance Traveled (km)": 0}})

    field_ngl_transport_mode_of_transport: DefaultDict = field(default_factory=lambda: {"Heavy-Duty Truck Emissions": {
                                        "Transport Fuel": "Diesel", "Distance Traveled (km)": 380}})
    
    field_ngl_transport_mode_of_transport: DefaultDict = field(default_factory=lambda: {"Ocean Tanker Emissions": {
                                        "Transport Fuel": "Bunker Fuel", "Distance Traveled (km)": 0}})
    
    field_ngl_transport_mode_of_transport: DefaultDict = field(default_factory=lambda: {"Barge Emissions": {
                                        "Transport Fuel": "Residual Oil", "Distance Traveled (km)": 0}})
 
    transport_fuel_share: DefaultDict = field(default_factory=lambda: {"Pipeline": {
        "Natural Gas": 0.11}})
    transport_fuel_options: List[str] = field(default_factory=lambda: ["Natural Gas", "LNG Diesel", "Bunker Fuel Residual Oil",
                                                                       "LPG DME FTD Biodiesel", "Renewable Diesel", "Renewable Gasoline", "Hydrogen", "Ethanol", "Methanol"])
    # user inputs combustion model scope
    # table: Refinery product combustion + Product Slate
    refinery_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Gasoline": {
                                        "% Combusted": 1.0}})

    refinery_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Jet Fuel": {
                                        "% Combusted": 1.0}})

    refinery_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Diesel": {
                                        "% Combusted": 1.0}})
    
    refinery_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Fuel Oil": {
                                        "% Combusted": 1.0}})
    
    refinery_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Coke": {
                                        "% Combusted": 1.0}})
    
    refinery_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Residual Fuels": {
                                        "% Combusted": 1.0}})
  
    refinery_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Liquefied Petroleum Gases (LPG)": {
                                        "% Combusted": 1.0}})
    
    # table: Field product combustion (combination of all Field * Combustion tables) + Product Slate
    field_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Coke": {
                                        "% Combusted": 1.0}})
    
    field_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Natural Gas": {
                                        "% Combusted": 1.0}})
 
    field_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Ethane": {
                                        "% Combusted": 1.0}})
    
    field_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Propane": {
                                        "% Combusted": 1.0}})
    
    field_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Butane": {
                                        "% Combusted": 1.0}})
    
    field_product_combustion_product_slate: DefaultDict = field(default_factory=lambda: {"Pentanes Plus": {
                                        "% Combusted": 1.0}})

