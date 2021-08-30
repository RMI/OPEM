from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


@dataclass
class TankerBargeEF:
    def __post_init__(self, user_input):
        print(type(user_input))
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

    def calculate_tanker_barge_ef():
        pass

    constants: Constants

    # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {}

    # Tanker & Barge EF sheet, table: Tanker and Barge Emission Factors
    # CALCULATED
    tanker_barge_emission_factors: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Tanker and Barge Emission Factors'))

    # Tanker & Barge EF sheet, table: Cargo Payload by Transportation Mode and by Product Fuel Type (short tons)
    # User Input
    cargo_payload: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Cargo Payload by Transportation Mode and by Product Fuel Type (short tons)'))

    # Tanker & Barge EF sheet, table: Horsepower Requirements for Ocean Tanker and Barges: Calculated With Cargo Capacity (hp)
    # Calculated
    cargo_payload: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Horsepower Requirements for Ocean Tanker and Barges- Calculated With Cargo Capacity (hp)'))

    # Tanker & Barge EF sheet, table: Calculation of Energy Consumption for Ocean Tanker and Barge :: average speed
    # User Input
    tanker_barge_average_speed: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Average Speed (miles:hour)'))

    # Tanker & Barge EF sheet, table: Calculation of Energy Consumption for Ocean Tanker and Barge :: Energy Consumption -- Trip From Product Origin to Destination
    # User Input
    # Calculated
    tanker_barge_energy_consumption_origin_to_destination: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Energy Consumption -- Trip From Product Origin to Destination'))

    # Tanker & Barge EF sheet, table: Calculation of Energy Consumption for Ocean Tanker and Barge :: Energy Consumption -- Trip From Product Destination Back to Origin
    # User Input
    # Calculated
    tanker_barge_energy_consumption_destination_to_origin: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Energy Consumption -- Trip From Product Destination Back to Origin'))

    # Tanker & Barge EF sheet, table: Energy Intensity of Transport (Btu:kgkm)
    # Calculated
    tanker_barge_energy_intensity_transport: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Energy Intensity of Transport (Btu:kgkm)'))

    # Tanker & Barge EF sheet, table: Emission Factors of Fuel Combustion: Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Ocean Tanker
    # Static
    tanker_barge_emissions_factors_combustion_origin_destination_ocean_tanker: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Ocean Tanker'))

    # Tanker & Barge EF sheet, table: Emission Factors of Fuel Combustion: Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Barge
    # Static
    tanker_barge_emissions_factors_combustion_origin_destination_barge: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Emission Factors of Fuel Combustion- Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Barge'))

    # Tanker & Barge EF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned) -- Ocean Tanker
    # Static
    tanker_barge_emissions_factors_combustion_destination_origin_ocean_tanker: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned) -- Ocean Tanker'))

    # Tanker & Barge EF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned) -- Barge
    # Static
    tanker_barge_emissions_factors_combustion_destination_origin_barge: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned) -- Barge'))

    # Tanker & Barge EF sheet, table: Ocean Tanker Emissions From Transport (g CO2 eq.:kgkm) -- Ocean Tanker Forward Journey
    # Calculated
    tanker_barge_emissions_factors_transport_forward_journey_ocean_tanker: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Ocean Tanker Emissions From Transport (g CO2 eq.:kgkm) -- Ocean Tanker Forward Journey'))

    # Tanker & Barge EF sheet, table: Ocean Tanker Emissions From Transport (g CO2 eq.:kgkm) -- Ocean Tanker Backhaul
    # Calculated
    tanker_barge_emissions_factors_transport_backhaul_ocean_tanker: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Ocean Tanker Emissions From Transport (g CO2 eq.:kgkm) -- Ocean Tanker Backhaul'))

    # Tanker & Barge EF sheet, table: Barge Emissions From Transport (g CO2 eq.:kgkm) -- Barge Forward Journey
    # Calculated
    tanker_barge_emissions_factors_transport_forward_journey_barge: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Barge Emissions From Transport (g CO2 eq.:kgkm) -- Barge Forward Journey'))

    # Tanker & Barge EF sheet, table: Barge Emissions From Transport (g CO2 eq.:kgkm) -- Barge Backhaul
    # Calculated
    tanker_barge_emissions_factors_transport_backhaul_barge: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Barge Emissions From Transport (g CO2 eq.:kgkm) -- Barge Backhaul'))

    # Tanker & Barge EF sheet, table: Marine Fuel Properties and Consumption (Residual Oil)
    # Calculated
    # User Input
    marine_fuel_properties_consumption: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Marine Fuel Properties and Consumption (Residual Oil)'))
