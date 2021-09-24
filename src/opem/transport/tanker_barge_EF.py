from dataclasses import InitVar, dataclass, field
from typing import Any, Dict
from opem.constants import Constants
from opem.products.product_slate import ProductSlate

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

from statistics import mean
# Define functions for filling calculated cells in the tables here


def calc_product_total_mass_flow(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return sum(
        (float(value["Flow"]) for key, value in other_table_refs[0].items() if key not in ["full_table_name", "row_index_name"] and key not in extra["excluded_keys"] and value != None))


def calc_marine_heating_val(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    MJ_to_BTU = 947.817

    return other_table_refs[0]["Bunker fuel for ocean tanker"]["User Selection: LHV or HHV, Btu/gal"] / MJ_to_BTU / other_table_refs[0]["Bunker fuel for ocean tanker"]["Density, grams/gal"] * 1000


def calc_horsepower(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Ocean Tanker":
        return 9070+0.101*other_table_refs[0][row_key][col_key]
    elif row_key == "Barge":
        return 5600/22500*other_table_refs[0][row_key][col_key]


def calc_tanker_barge_energy_consumption(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if col_key == "Ocean Tanker":
        return other_table_refs[0]["Energy Consumption (Btu/kWh operation)"]["properties"]/1.3410220888
    elif col_key == "Barge":
        return (14.42/target_table_ref["Load Factor"]["Barge"]+350)*0.735*other_table_refs[1]["Residual oil"]["User Selection: LHV or HHV, Btu/gal"]/other_table_refs[1]["Residual oil"]["Density, grams/gal"]


def calc_marine_energy_consumption(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    MJ_to_BTU = 947.817

    return (target_table_ref["Heating Value"]["properties"] *
            float(target_table_ref["Brake Specific Fuel Consumption (BSFC, g/kWh operation)"]["properties"]) *
            MJ_to_BTU / 1000)


def calc_product_share(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

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
        return (other_table_refs[0]["Fuel Oil"]["Flow"] + other_table_refs[0]["Residual fuels"]["Flow"]/target_table_ref["mass_flow_sum"]["total"])
    else:

        return other_table_refs[0][other_table_row_key]["Flow"]/target_table_ref["mass_flow_sum"]["total"]


def calc_barge_tanker_emissions(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    result = 0
    for key, row in other_table_refs[0].items():
        if key not in ['full_table_name', 'row_index_name']:
            result += row[col_key] * \
                other_table_refs[1][key]['GWP']
    result = (result * other_table_refs[2]
              [extra["trip_details"]][row_key])/1000000
    return result


def calc_energy_intensity_transport(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs[0]["Energy Consumption (Btu/hphr)"][extra["trip_details"]] * \
        other_table_refs[0]["Load Factor"][extra["trip_details"]
                                           ] * other_table_refs[2][extra["trip_details"]][col_key] / \
        other_table_refs[1]["Average Speed (miles/hour)"][extra["trip_details"]] / \
        other_table_refs[3][extra["trip_details"]][col_key] / \
        other_table_refs[4]["kg per short ton"]["Conversion Factor"] / \
        other_table_refs[4]["km per mile"]["Conversion Factor"]


def calc_emission_factors_ocean_tanker_forward_backward(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    total = 0
    for row in other_table_refs[0].keys():
        if row != "full_table_name" and row != "row_index_name":
            total += other_table_refs[0][row][col_key] * \
                other_table_refs[1][row]["share"]
    return total


def calc_emission_factors_ocean_tanker_total(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    return target_table_ref["Ocean Tanker Forward Journey"][col_key] + target_table_ref["Ocean Tanker Backhaul"][col_key]


def calc_emission_factors_barge_forward_backward(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Barge Forward Journey":
        return mean(other_table_refs[0][row][col_key] for row in other_table_refs[0].keys() if row != "full_table_name" and row != "row_index_name")
    elif row_key == "Barge Backhaul":
        return mean(other_table_refs[1][row][col_key] for row in other_table_refs[0].keys() if row != "full_table_name" and row != "row_index_name")


def calc_emission_factors_barge_total(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return target_table_ref["Barge Forward Journey"][col_key] + target_table_ref["Barge Backhaul"][col_key]


@dataclass
class TankerBargeEF:
    def __post_init__(self, user_input):

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
                                  self.product_slate.mass_flow_kg, ],
                              # hack the keymap to pass excluded column when we iterate over other_table keys
                              extra={"excluded_keys": ["Net Upstream Petcoke", ]})

        fill_calculated_cells(target_table_ref=self.share_of_petroleum_products, other_table_refs=[
            self.product_slate.mass_flow_kg, ],
            func_to_apply=calc_product_share, excluded_rows=[
            "mass_flow_sum", "row_index_name"],
            other_tables_keymap={f"{self.product_slate.mass_flow_kg['full_table_name']}": {
                "row_keymap": {"Petcoke": "Coke"}}})

        fill_calculated_cells(target_table_ref=self.marine_fuel_properties_consumption,
                              included_rows=["Heating Value"], included_cols=["properties"],
                              func_to_apply=calc_marine_heating_val,
                              other_table_refs=[self.constants.table_3_fuel_specifications_liquid_fuels])

        fill_calculated_cells(target_table_ref=self.marine_fuel_properties_consumption,
                              included_rows=["Energy Consumption (Btu/kWh operation)"], included_cols=["properties"],
                              func_to_apply=calc_marine_energy_consumption,
                              other_table_refs=[self.constants.table_3_fuel_specifications_liquid_fuels])
        # calculate horsepower
        fill_calculated_cells(target_table_ref=self.horsepower_requirements,
                              func_to_apply=calc_horsepower,
                              other_table_refs=[self.cargo_payload])
        # calculate tanker/barge energy consumption forward
        fill_calculated_cells(target_table_ref=self.tanker_barge_energy_consumption_origin_to_destination,
                              func_to_apply=calc_tanker_barge_energy_consumption,
                              included_rows=["Energy Consumption (Btu/hphr)"],
                              other_table_refs=[self.marine_fuel_properties_consumption, self.constants.table_3_fuel_specifications_liquid_fuels])

        # calculate tanker/barge energy consumption backward
        fill_calculated_cells(target_table_ref=self.tanker_barge_energy_consumption_destination_to_origin,
                              func_to_apply=calc_tanker_barge_energy_consumption,
                              included_rows=["Energy Consumption (Btu/hphr)"],
                              other_table_refs=[self.marine_fuel_properties_consumption, self.constants.table_3_fuel_specifications_liquid_fuels])

        # calculate energy intensity
        fill_calculated_cells(target_table_ref=self.tanker_barge_energy_intensity_transport,
                              func_to_apply=calc_energy_intensity_transport,
                              included_rows=["Ocean Tanker Forward Journey"],
                              extra={
                                  "trip_details": "Ocean Tanker"},
                              other_table_refs=[self.tanker_barge_energy_consumption_origin_to_destination,
                                                self.tanker_barge_average_speed,
                                                self.horsepower_requirements,
                                                self.cargo_payload,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.tanker_barge_energy_intensity_transport,
                              func_to_apply=calc_energy_intensity_transport,
                              included_rows=["Ocean Tanker Backhaul"],
                              extra={
                                  "trip_details": "Ocean Tanker"},
                              other_table_refs=[self.tanker_barge_energy_consumption_destination_to_origin,
                                                self.tanker_barge_average_speed,
                                                self.horsepower_requirements,
                                                self.cargo_payload,
                                                self.constants.table_2_conversion_factors])
        fill_calculated_cells(target_table_ref=self.tanker_barge_energy_intensity_transport,
                              func_to_apply=calc_energy_intensity_transport,
                              included_rows=["Barge Forward Journey"],
                              extra={
                                  "trip_details": "Barge"},
                              other_table_refs=[self.tanker_barge_energy_consumption_origin_to_destination,
                                                self.tanker_barge_average_speed,
                                                self.horsepower_requirements,
                                                self.cargo_payload,
                                                self.constants.table_2_conversion_factors])

        fill_calculated_cells(target_table_ref=self.tanker_barge_energy_intensity_transport,
                              func_to_apply=calc_energy_intensity_transport,
                              included_rows=["Barge Backhaul"],
                              extra={
                                  "trip_details": "Barge"},
                              other_table_refs=[self.tanker_barge_energy_consumption_destination_to_origin,
                                                self.tanker_barge_average_speed,
                                                self.horsepower_requirements,
                                                self.cargo_payload,
                                                self.constants.table_2_conversion_factors])

        # calculate emissions factors from transport
        fill_calculated_cells(target_table_ref=self.tanker_barge_emissions_factors_transport_forward_journey_barge,
                              func_to_apply=calc_barge_tanker_emissions,
                              extra={
                                  "trip_details": "Barge Forward Journey"},
                              other_table_refs=[self.tanker_barge_emissions_factors_combustion_origin_destination_barge,
                                                self.constants.table_1_100year_gwp,
                                                self.tanker_barge_energy_intensity_transport])

        fill_calculated_cells(target_table_ref=self.tanker_barge_emissions_factors_transport_backhaul_barge,
                              func_to_apply=calc_barge_tanker_emissions,
                              extra={
                                  "trip_details": "Barge Backhaul"},
                              other_table_refs=[self.tanker_barge_emissions_factors_combustion_destination_origin_barge,
                                                self.constants.table_1_100year_gwp,
                                                self.tanker_barge_energy_intensity_transport])

        fill_calculated_cells(target_table_ref=self.tanker_barge_emissions_factors_transport_forward_journey_ocean_tanker,
                              func_to_apply=calc_barge_tanker_emissions,
                              extra={
                                  "trip_details": "Ocean Tanker Forward Journey"},
                              other_table_refs=[self.tanker_barge_emissions_factors_combustion_origin_destination_ocean_tanker,
                                                self.constants.table_1_100year_gwp,
                                                self.tanker_barge_energy_intensity_transport])

        fill_calculated_cells(target_table_ref=self.tanker_barge_emissions_factors_transport_backhaul_ocean_tanker,
                              func_to_apply=calc_barge_tanker_emissions,
                              extra={
                                  "trip_details": "Ocean Tanker Backhaul"},
                              other_table_refs=[self.tanker_barge_emissions_factors_combustion_destination_origin_ocean_tanker,
                                                self.constants.table_1_100year_gwp,
                                                self.tanker_barge_energy_intensity_transport])
        # calculate emission factors for ocean tanker, forward and backward
        fill_calculated_cells(target_table_ref=self.tanker_barge_emission_factors,
                              func_to_apply=calc_emission_factors_ocean_tanker_forward_backward,
                              included_rows=[
                                  "Ocean Tanker Forward Journey", "Ocean Tanker Backhaul"],
                              excluded_cols=["Residual Oil", "Biodiesel",
                                             "Renewable Diesel", "Renewable Gasoline"],
                              other_table_refs=[self.tanker_barge_emissions_factors_transport_forward_journey_ocean_tanker,
                                                self.share_of_petroleum_products])
        fill_calculated_cells(target_table_ref=self.tanker_barge_emission_factors,
                              func_to_apply=calc_emission_factors_ocean_tanker_total,
                              included_rows=[
                                  "Ocean Tanker Emissions"],
                              excluded_cols=["Residual Oil", "Biodiesel",
                                             "Renewable Diesel", "Renewable Gasoline"],
                              )

        fill_calculated_cells(target_table_ref=self.tanker_barge_emission_factors,
                              func_to_apply=calc_emission_factors_barge_forward_backward,
                              included_rows=[
                                  "Barge Forward Journey", "Barge Backhaul"],
                              excluded_cols=["Bunker Fuel", ],
                              other_table_refs=[self.tanker_barge_emissions_factors_transport_forward_journey_barge,
                                                self.tanker_barge_emissions_factors_transport_backhaul_barge])

        fill_calculated_cells(target_table_ref=self.tanker_barge_emission_factors,
                              func_to_apply=calc_emission_factors_barge_total,
                              included_rows=[
                                  "Barge Emissions"],
                              excluded_cols=["Bunker Fuel"])

    constants: Constants

    product_slate: ProductSlate

    # will this cause problems if I try to pass in a list?
    user_input: InitVar[Dict] = {}

    # Tanker & Barge EF sheet, table: Tanker and Barge Emission Factors
    # CALCULATED
    tanker_barge_emission_factors: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Tanker_and_Barge_Emission_Factors'))

    # Tanker & Barge EF sheet, table: Cargo Payload by Transportation Mode and by Product Fuel Type (short tons)
    # User Input
    cargo_payload: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
       'Cargo_Payload_by_Transportation_Mode_and_by_Product_Fuel_Type'))

    # Tanker & Barge EF sheet, table: Horsepower Requirements for Ocean Tanker and Barges: Calculated With Cargo Capacity (hp)
    # Calculated
    horsepower_requirements: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
       'Horsepower_Requirements_for_Ocean_Tanker_and_Barges_Calculated_With_Cargo_Capacity'))

    # Tanker & Barge EF sheet, table: Calculation of Energy Consumption for Ocean Tanker and Barge :: average speed
    # User Input
    tanker_barge_average_speed: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Average_Speed'))

    # Tanker & Barge EF sheet, table: Calculation of Energy Consumption for Ocean Tanker and Barge :: Energy Consumption -- Trip From Product Origin to Destination
    # User Input
    # Calculated
    tanker_barge_energy_consumption_origin_to_destination: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
            'Energy_Consumption_Trip_From_Product_Origin_to_Destination'))

    # Tanker & Barge EF sheet, table: Calculation of Energy Consumption for Ocean Tanker and Barge :: Energy Consumption -- Trip From Product Destination Back to Origin
    # User Input
    # Calculated
    tanker_barge_energy_consumption_destination_to_origin: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
            'Energy_Consumption_Trip_From_Product_Destination_Back_to_Origin'))

    # Tanker & Barge EF sheet, table: Energy Intensity of Transport (Btu:kgkm)
    # Calculated
    tanker_barge_energy_intensity_transport: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Energy_Intensity_of_Transport'))

    # Tanker & Barge EF sheet, table: Emission Factors of Fuel Combustion: Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Ocean Tanker
    # Static
    tanker_barge_emissions_factors_combustion_origin_destination_ocean_tanker: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Emission_Factors_of_Fuel_Combustion_Feedstock_and_Fuel_Transportation_From_Product_Origin_to_Product_Destination_Ocean_Tanker'))

    # Tanker & Barge EF sheet, table: Emission Factors of Fuel Combustion: Feedstock and Fuel Transportation From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Barge
    # Static
    tanker_barge_emissions_factors_combustion_origin_destination_barge: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
      'Emission_Factors_of_Fuel_Combustion_Feedstock_and_Fuel_Transportation_From_Product_Origin_to_Product_Destination_Barge'))

    # Tanker & Barge EF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned) -- Ocean Tanker
    # Static
    tanker_barge_emissions_factors_combustion_destination_origin_ocean_tanker: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
        'Emission_Factors_of_Fuel_Combustion_for_Feedstock_and_Fuel_Transportation_Trip_From_Product_Destination_Back_to_Product_Origin_Ocean_Tanker'))

    # Tanker & Barge EF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned) -- Barge
    # Static
    tanker_barge_emissions_factors_combustion_destination_origin_barge: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
       'Emission_Factors_of_Fuel_Combustion_for_Feedstock_and_Fuel_Transportation_Trip_From_Product_Destination_Back_to_Product_Origin_Barge'))

    # Tanker & Barge EF sheet, table: Ocean Tanker Emissions From Transport (g CO2 eq.:kgkm) -- Ocean Tanker Forward Journey
    # Calculated
    tanker_barge_emissions_factors_transport_forward_journey_ocean_tanker: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
        'Ocean_Tanker_Emissions_From_Transport_Ocean_Tanker_Forward_Journey'))

    # Tanker & Barge EF sheet, table: Ocean Tanker Emissions From Transport (g CO2 eq.:kgkm) -- Ocean Tanker Backhaul
    # Calculated
    tanker_barge_emissions_factors_transport_backhaul_ocean_tanker: Dict = field(
        default_factory=lambda: build_dict_from_defaults( 
            'Ocean_Tanker_Emissions_From_Transport_Ocean_Tanker_Backhaul'))

    # Tanker & Barge EF sheet, table: Barge Emissions From Transport (g CO2 eq.:kgkm) -- Barge Forward Journey
    # Calculated
    tanker_barge_emissions_factors_transport_forward_journey_barge: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
       'Barge_Emissions_From_Transport_Barge_Forward_Journey'))

    # Tanker & Barge EF sheet, table: Barge Emissions From Transport (g CO2 eq.:kgkm) -- Barge Backhaul
    # Calculated
    tanker_barge_emissions_factors_transport_backhaul_barge: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
       'Barge_Emissions_From_Transport_Barge_Backhaul'))

    # Tanker & Barge EF sheet, table: Marine Fuel Properties and Consumption (Residual Oil)
    # Calculated
    # User Input
    marine_fuel_properties_consumption: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Marine_Fuel_Properties_and_Consumption_Residual_Oil'))

    # Tanker & Barge EF sheet, table: Share of Petroleum Products
    # Calculated
    # calculated from ProductSlate
    share_of_petroleum_products: Dict = field(
        default_factory=lambda: {"row_index_name": "Product Transported",
                                 "mass_flow_sum": {"total": float},
                                 "Gasoline": {"share": float},
                                 "Diesel":  {"share": float},
                                 "Jet Fuel":  {"share": float},
                                 "Residual Oil":  {"share": float},
                                 "Petcoke":  {"share": float}})
