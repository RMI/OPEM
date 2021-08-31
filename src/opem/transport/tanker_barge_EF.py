from dataclasses import InitVar, dataclass, field
from typing import Any, DefaultDict
from opem.constants import Constants
from opem.products.product_slate import ProductSlate

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


def calc_product_total_mass_flow(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None):
    return sum(
        (float(value) for key, value in other_table_refs[0].mass_flow.items() if key != "full_table_name" and key not in other_tables_keymap["excluded_keys"] and value != "null"))


def calc_marine_heating_val(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None):
    print("MARINE")
    MJ_to_BTU = 947.817

    return other_table_refs[0]["Bunker fuel for ocean tanker"]["User Selection: LHV or HHV, Btu/gal"] / MJ_to_BTU / other_table_refs[0]["Bunker fuel for ocean tanker"]["Density, grams/gal"] * 1000


def calc_marine_energy_consumption(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None):
    MJ_to_BTU = 947.817
    print("from inside marine energy consumption")
    return target_table_ref["Heating Value"]["properties"] * target_table_ref["Brake Specific Fuel Consumption (BSFC, g/kWh operation)"]["properties"] * MJ_to_BTU / 1000


def calc_product_share(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None):

    # there might be more keys: other_table_col_key1, other_table_col_key2, etc.
    other_table_col_key = col_key
    other_table_row_key = row_key
    if other_tables_keymap and other_table_refs[0]["full_table_name"] in other_tables_keymap.keys():
        if "col_keymap" in other_tables_keymap[other_table_refs[0]["full_table_name"]].keys():
            other_table_col_key = (lambda col_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"][col_key] if col_key in
                                   other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"].keys() else other_table_col_key)(col_key)
        if "row_keymap" in other_tables_keymap[other_table_refs[0]["full_table_name"]].keys():
            other_table_row_key = (lambda row_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"][row_key] if row_key in
                                   other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"].keys() else other_table_row_key)(row_key)

    if row_key == "Residual Oil":
        return (other_table_refs[0]["Fuel_Oil_kg"] + other_table_refs[0]["Residual_fuels_kg"]/target_table_ref["mass_flow_sum"]["total"])
    else:
        return other_table_refs[0][other_table_row_key]/target_table_ref["mass_flow_sum"]["total"]


def calc_barge_tanker_emissions(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None):
    print(target_table_ref['full_table_name'])
    result = 0
    for key, row in other_table_refs[0].items():
        if key not in ['full_table_name', 'row_index_name']:
            print(key)
            print(col_key)
            print(other_tables_keymap)

            result += row[col_key] * \
                other_table_refs[1][key]['GWP']
    result = (result * other_table_refs[2]
              [other_tables_keymap["trip_details"]][row_key])/100000
    return result


def calc_energy_intensity_transport(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None):
    other_table_refs[0]["Energy Consumption (Btu/hphr)"][other_tables_keymap["trip_details"]] * \
        other_table_refs[0]["Load Factor"][other_tables_keymap["trip_details"]
                                           ] * other_table_refs[2][other_tables_keymap["trip_details"]][col_key] / \
        other_table_refs[1]["Average Speed (miles/hour)"][other_tables_keymap["trip_details"]] / \
        other_table_refs[3][other_tables_keymap["trip_details"]][col_key] / \
        other_table_refs[4]["kg per short ton"]["Conversion Factor"] / \
        other_table_refs[4]["km per mile"]["Conversion Factor"]


@dataclass
class TankerBargeEF:
    def __post_init__(self, user_input):
        print("Tanker barge")
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

        fill_calculated_cells(target_table_ref=self.share_of_petroleum_products,
                              func_to_apply=calc_product_total_mass_flow, included_rows=[
                                  "mass_flow_sum"],
                              included_cols=["total"],
                              other_table_refs=[
                                  self.product_slate, ],
                              # hack the keymap to pass excluded column when we iterate over other_table keys
                              other_tables_keymap={"excluded_keys": ["Net_Upstream_Petcoke_kg"]})

        fill_calculated_cells(target_table_ref=self.share_of_petroleum_products, other_table_refs=[
            self.product_slate.mass_flow, ],
            func_to_apply=calc_product_share, excluded_rows=[
            "mass_flow_sum", "row_index_name"],
            other_tables_keymap={f"{self.product_slate.mass_flow['full_table_name']}": {
                "row_keymap": {"Gasoline": "Gasoline_kg",
                               "Jet Fuel": "Jet_Fuel_kg",
                               "Diesel": "Diesel_kg",
                               "Petcoke": "Coke_kg"}}})

        fill_calculated_cells(target_table_ref=self.marine_fuel_properties_consumption,
                              included_rows=["Heating Value"], included_cols=["properties"],
                              func_to_apply=calc_marine_heating_val,
                              other_table_refs=[self.constants.table_3_fuel_specifications_liquid_fuels])

        fill_calculated_cells(target_table_ref=self.marine_fuel_properties_consumption,
                              included_rows=["Energy Consumption (Btu/kWh operation)"], included_cols=["properties"],
                              func_to_apply=calc_marine_energy_consumption,
                              other_table_refs=[self.constants.table_3_fuel_specifications_liquid_fuels])
        # calculate horsepower
        fill_calculated_cells(target_table_ref=self.marine_fuel_properties_consumption,
                              included_rows=["Energy Consumption (Btu/kWh operation)"], included_cols=["properties"],
                              func_to_apply=calc_horsepower,
                              other_table_refs=[self.constants.table_3_fuel_specifications_liquid_fuels])

        fill_calculated_cells(target_table_ref=self.tanker_barge_emissions_factors_transport_forward_journey_barge,
                              func_to_apply=calc_barge_tanker_emissions,
                              other_tables_keymap={
                                  "trip_details": "Barge Forward Journey"},
                              other_table_refs=[self.tanker_barge_emissions_factors_combustion_origin_destination_barge,
                                                self.constants.table_1_100year_gwp,
                                                self.tanker_barge_energy_intensity_transport])

        fill_calculated_cells(target_table_ref=self.tanker_barge_emissions_factors_transport_backhaul_barge,
                              func_to_apply=calc_barge_tanker_emissions,
                              other_tables_keymap={
                                  "trip_details": "Barge Backhaul"},
                              other_table_refs=[self.tanker_barge_emissions_factors_combustion_destination_origin_barge,
                                                self.constants.table_1_100year_gwp,
                                                self.tanker_barge_energy_intensity_transport])

        fill_calculated_cells(target_table_ref=self.tanker_barge_emissions_factors_transport_forward_journey_ocean_tanker,
                              func_to_apply=calc_barge_tanker_emissions,
                              other_tables_keymap={
                                  "trip_details": "Ocean Tanker Forward Journey"},
                              other_table_refs=[self.tanker_barge_emissions_factors_combustion_origin_destination_ocean_tanker,
                                                self.constants.table_1_100year_gwp,
                                                self.tanker_barge_energy_intensity_transport])

        fill_calculated_cells(target_table_ref=self.tanker_barge_emissions_factors_transport_backhaul_ocean_tanker,
                              func_to_apply=calc_barge_tanker_emissions,
                              other_tables_keymap={
                                  "trip_details": "Ocean Tanker Backhaul"},
                              other_table_refs=[self.tanker_barge_emissions_factors_combustion_destination_origin_ocean_tanker,
                                                self.constants.table_1_100year_gwp,
                                                self.tanker_barge_energy_intensity_transport])

        fill_calculated_cells(target_table_ref=self.tanker_barge_energy_intensity_transport,
                              func_to_apply=calc_energy_intensity_transport,
                              included_rows=["Ocean Tanker Forward Journey"],
                              other_tables_keymap={
                                  "trip_details": "Ocean Tanker"},
                              other_table_refs=[self.tanker_barge_energy_consumption_origin_to_destination,
                                                self.tanker_barge_average_speed,
                                                self.horsepower_requirements,
                                                self.cargo_payload,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.tanker_barge_energy_intensity_transport,
                              func_to_apply=calc_energy_intensity_transport,
                              included_rows=["Ocean Tanker Backhaul"],
                              other_tables_keymap={
                                  "trip_details": "Ocean Tanker"},
                              other_table_refs=[self.tanker_barge_energy_consumption_destination_to_origin,
                                                self.tanker_barge_average_speed,
                                                self.horsepower_requirements,
                                                self.cargo_payload,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.tanker_barge_energy_intensity_transport,
                              func_to_apply=calc_energy_intensity_transport,
                              included_rows=["Barge Forward Journey"],
                              other_tables_keymap={
                                  "trip_details": "Barge"},
                              other_table_refs=[self.tanker_barge_energy_consumption_origin_to_destination,
                                                self.tanker_barge_average_speed,
                                                self.horsepower_requirements,
                                                self.cargo_payload,
                                                self.constants.table_2_conversion_factors])

        fill_calculated_cells(target_table_ref=self.tanker_barge_energy_intensity_transport,
                              func_to_apply=calc_energy_intensity_transport,
                              included_rows=["Barge Backhaul"],
                              other_tables_keymap={
                                  "trip_details": "Barge"},
                              other_table_refs=[self.tanker_barge_energy_consumption_destination_to_origin,
                                                self.tanker_barge_average_speed,
                                                self.horsepower_requirements,
                                                self.cargo_payload,
                                                self.constants.table_2_conversion_factors])
        print(self.tanker_barge_energy_intensity_transport)
    constants: Constants

    product_slate: ProductSlate

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
    horsepower_requirements: DefaultDict = field(
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

    # Tanker & Barge EF sheet, table: Share of Petroleum Products
    # Calculated
    # calculated from ProductSlate
    share_of_petroleum_products: DefaultDict = field(
        default_factory=lambda: {"row_index_name": "Product Transported",
                                 "mass_flow_sum": {"total": float},
                                 "Gasoline": {"share": float},
                                 "Diesel":  {"share": float},
                                 "Jet Fuel":  {"share": float},
                                 "Residual Oil":  {"share": float},
                                 "Petcoke":  {"share": float}})
