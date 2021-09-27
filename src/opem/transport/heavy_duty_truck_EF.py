from dataclasses import InitVar, dataclass, field
from typing import Dict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


def co2_for_class8_diesel(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    return (other_table_refs[1]['U.S. conventional diesel']['Density, grams/gal']/other_table_refs[0][extra['trip_econ']]["Fuel Economy (miles/diesel gallon)"]*other_table_refs[1]['U.S. conventional diesel']['C ratio, (% by wt)']
            - (target_table_ref["VOC"]
               ["Class 8B Diesel Truck Emission Factors (g/mi.)"]*other_table_refs[2]["Carbon ratio of VOC"]["ratio"] +
               target_table_ref["CO"]["Class 8B Diesel Truck Emission Factors (g/mi.)"] *
               other_table_refs[2]["Carbon ratio of CO"]["ratio"] +
               target_table_ref["CH4"]["Class 8B Diesel Truck Emission Factors (g/mi.)"] *
               other_table_refs[2]["Carbon ratio of CH4"]["ratio"])) / other_table_refs[2]["Carbon ratio of CO2"]["ratio"]


def emission_factors_calc_fill_middle(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    other_table_col_key = col_key
    other_table_row_key = row_key
    if other_tables_keymap:
        if "col_keymap" in other_tables_keymap[other_table_refs[0]["full_table_name"]].keys():
            other_table_col_key = (lambda col_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"][col_key] if col_key in
                                   other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"].keys() else other_table_col_key)(col_key)
        if "row_keymap" in other_tables_keymap[other_table_refs[0]["full_table_name"]].keys():
            other_table_row_key = (lambda row_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"][row_key] if row_key in
                                   other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"].keys() else other_table_row_key)(row_key)
    return target_table_ref[row_key]['Diesel'] * other_table_refs[0][other_table_row_key][other_table_col_key]


def co2_for_renew_diesel_forward(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    hv = other_table_refs[1]["Renewable diesel II (UOP-HDO)"]["User Selection: LHV or HHV, Btu/gal"]
    density = other_table_refs[1]["Renewable diesel II (UOP-HDO)"]["Density, grams/gal"]
    c_ratio = other_table_refs[1]["Renewable diesel II (UOP-HDO)"]["C ratio, (% by wt)"]
    if other_table_refs[0] == 1:
        hv = other_table_refs[1]["Renewable diesel I (SuperCetane)"]["User Selection: LHV or HHV, Btu/gal"]
        density = other_table_refs[1]["Renewable diesel I (SuperCetane)"]["Density, grams/gal"]
        c_ratio = other_table_refs[1]["Renewable diesel I (SuperCetane)"]["C ratio, (% by wt)"]
    elif other_table_refs[0] == 3:
        hv = other_table_refs[1]["Renewable diesel III (PNNL-HTL)"]["User Selection: LHV or HHV, Btu/gal"]
        density = other_table_refs[1]["Renewable diesel III (PNNL-HTL)"]["Density, grams/gal"]

    # There might be a problem with this formula, originating from the workbook
    return (1000000/hv*density*c_ratio - (target_table_ref["VOC"]["Renewable Diesel"] *
                                          other_table_refs[2]["Carbon ratio of VOC"]["ratio"]+target_table_ref["CO"]["Renewable Diesel"] *
                                          other_table_refs[2]["Carbon ratio of CO"]["ratio"] +
                                          target_table_ref["N2O"]["Renewable Diesel"] *
                                          other_table_refs[2]["Carbon ratio of CH4"]["ratio"])) / other_table_refs[2]["Carbon ratio of CO2"]["ratio"]


def co2_for_renew_diesel_backward(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    hv = other_table_refs[1]["Renewable diesel II (UOP-HDO)"]["User Selection: LHV or HHV, Btu/gal"]
    density = other_table_refs[1]["Renewable diesel II (UOP-HDO)"]["Density, grams/gal"]
    c_ratio = other_table_refs[3]["Natural gas"]["C ratio, (% by wt)"]
    if other_table_refs[0] == 1:
        hv = other_table_refs[1]["Renewable diesel I (SuperCetane)"]["User Selection: LHV or HHV, Btu/gal"]
        density = other_table_refs[1]["Renewable diesel I (SuperCetane)"]["Density, grams/gal"]

    elif other_table_refs[0] == 3:
        hv = other_table_refs[1]["Renewable diesel III (PNNL-HTL)"]["User Selection: LHV or HHV, Btu/gal"]
        density = other_table_refs[1]["Renewable diesel III (PNNL-HTL)"]["Density, grams/gal"]

    # There might be a problem with this formula, originating from the workbook
    return (1000000/hv*density*c_ratio - (target_table_ref["VOC"]["Renewable Diesel"] *
                                          other_table_refs[2]["Carbon ratio of VOC"]["ratio"]+target_table_ref["CO"]["Renewable Diesel"] *
                                          other_table_refs[2]["Carbon ratio of CO"]["ratio"] +
                                          target_table_ref["N2O"]["Renewable Diesel"] *
                                          other_table_refs[2]["Carbon ratio of CH4"]["ratio"])) / other_table_refs[2]["Carbon ratio of CO2"]["ratio"]


def so2_for_renew_diesel_forward(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    hv = other_table_refs[1]["Renewable diesel II (UOP-HDO)"]["User Selection: LHV or HHV, Btu/gal"]
    density = other_table_refs[1]["Renewable diesel II (UOP-HDO)"]["Density, grams/gal"]
    s_ratio = other_table_refs[1]["Renewable diesel II (UOP-HDO)"]["S ratio, Actual ratio by wt"]
    if other_table_refs[0] == 1:
        hv = other_table_refs[1]["Renewable diesel I (SuperCetane)"]["User Selection: LHV or HHV, Btu/gal"]
        density = other_table_refs[1]["Renewable diesel I (SuperCetane)"]["Density, grams/gal"]
        s_ratio = other_table_refs[1]["Renewable diesel I (SuperCetane)"]["S ratio, Actual ratio by wt"]
    elif other_table_refs[0] == 3:
        hv = other_table_refs[1]["Renewable diesel III (PNNL-HTL)"]["User Selection: LHV or HHV, Btu/gal"]
        density = other_table_refs[1]["Renewable diesel III (PNNL-HTL)"]["Density, grams/gal"]

    return (1000000/hv*density*s_ratio / other_table_refs[2]["Sulfur ratio of SO2"]["ratio"])


def so2_for_renew_diesel_backward(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    hv = other_table_refs[1]["Renewable diesel II (UOP-HDO)"]["User Selection: LHV or HHV, Btu/gal"]
    density = other_table_refs[1]["Renewable diesel II (UOP-HDO)"]["Density, grams/gal"]
    s_ratio = other_table_refs[3]["Natural gas"]["S ratio, Actual ratio by wt"]
    if other_table_refs[0] == 1:
        hv = other_table_refs[1]["Renewable diesel I (SuperCetane)"]["User Selection: LHV or HHV, Btu/gal"]
        density = other_table_refs[1]["Renewable diesel I (SuperCetane)"]["Density, grams/gal"]
        # problem with cell reference H77 - it is in a table header
        s_ratio = other_table_refs[3]["Natural gas"]["S ratio, Actual ratio by wt"]

    elif other_table_refs[0] == 3:
        hv = other_table_refs[1]["Renewable diesel III (PNNL-HTL)"]["User Selection: LHV or HHV, Btu/gal"]
        density = other_table_refs[1]["Renewable diesel III (PNNL-HTL)"]["Density, grams/gal"]

    return (1000000/hv*density*s_ratio / other_table_refs[2]["Sulfur ratio of SO2"]["ratio"])


def co2_emissions_factors_most_fuels(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    # fuel columns are transposed in constants table
    other_table_col_key = row_key
    other_table_row_key = col_key

    if other_tables_keymap and other_table_refs[0]["full_table_name"] in other_tables_keymap.keys():
        if "col_keymap" in other_tables_keymap[other_table_refs[0]["full_table_name"]].keys():
            other_table_col_key = (lambda row_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"][row_key] if row_key in
                                   other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"].keys() else other_table_col_key)(row_key)
        if "row_keymap" in other_tables_keymap[other_table_refs[0]["full_table_name"]].keys():
            other_table_row_key = (lambda col_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"][col_key] if col_key in
                                   other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"].keys() else other_table_row_key)(col_key)

    hv = other_table_refs[0][other_table_row_key][
        "User Selection: LHV or HHV, Btu/gal"]
    density = other_table_refs[0][other_table_row_key]["Density, grams/gal"]
    c_ratio = other_table_refs[0][other_table_row_key]["C ratio, (% by wt)"]

    return (1000000/hv*density*c_ratio - (target_table_ref["VOC"][col_key] *
                                          other_table_refs[1]["Carbon ratio of VOC"]["ratio"]+target_table_ref["CO"][col_key] *
                                          other_table_refs[1]["Carbon ratio of CO"]["ratio"] +
                                          target_table_ref["N2O"][col_key] *
                                          other_table_refs[1]["Carbon ratio of CH4"]["ratio"])) / other_table_refs[1]["Carbon ratio of CO2"]["ratio"]


def so2_emissions_factors(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    # fuel columns are transposed in constants table
    other_table_col_key = row_key
    other_table_row_key = col_key

    if other_tables_keymap and other_table_refs[0]["full_table_name"] in other_tables_keymap.keys():
        if "col_keymap" in other_tables_keymap[other_table_refs[0]["full_table_name"]].keys():
            other_table_col_key = (lambda row_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"][row_key] if row_key in
                                   other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"].keys() else other_table_col_key)(row_key)
        if "row_keymap" in other_tables_keymap[other_table_refs[0]["full_table_name"]].keys():
            other_table_row_key = (lambda col_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"][col_key] if col_key in
                                   other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"].keys() else other_table_row_key)(col_key)

    hv = other_table_refs[0][other_table_row_key][
        "User Selection: LHV or HHV, Btu/gal"]
    density = other_table_refs[0][other_table_row_key]["Density, grams/gal"]
    s_ratio = other_table_refs[0][other_table_row_key]["S ratio, Actual ratio by wt"]

    return (1000000/hv*density*s_ratio/other_table_refs[1]["Sulfur ratio of SO2"]["ratio"])


def emission_factors_calc(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    # handle mapping the rows and columns of the target table to the rows and columns of other tables below
    # this example has only one other table and only maps columns
    # each table will need custom logic to handle rows/columns and however many other tables are passed in
    # we will probably not need to iterate over the other table refs, access via subscripts manually in the
    # custom logic below

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
    return target_table_ref[row_key]["Diesel"] * \
        other_table_refs[0][other_table_row_key][other_table_col_key]


def emission_factors_calc_diesel(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    # handle mapping the rows and columns of the target table to the rows and columns of other tables below
    # this example has only one other table and only maps columns
    # each table will need custom logic to handle rows/columns and however many other tables are passed in
    # we will probably not need to iterate over the other table refs, access via subscripts manually in the
    # custom logic below

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

    return (target_table_ref[row_key]["Class 8B Diesel Truck Emission Factors (g/mi.)"] *
            other_table_refs[0][
        extra['trip_econ']]['Fuel Economy (miles/diesel gallon)'] /
        other_table_refs[1]["U.S. conventional diesel"]["User Selection: LHV or HHV, Btu/gal"]*1000000)


def calc_truck_emission_factors_forward_backward(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    consump_per_payload = other_table_refs[0][extra["trip_details"]
                                              ]["Energy Consumption (Btu/km)"]/1000000/other_table_refs[0][extra["trip_details"]]["Cargo Payload (kg)"]
    fuel_sum = 0
    for key, row in other_table_refs[1].items():
        if key not in ["full_table_name", "row_index_name"]:
            fuel_sum += row["GWP"] * \
                other_table_refs[2][key][col_key]
            # if col_key == "Diesel":
            # print("from heavy duty Truck")
            # print("key", key)
            # print("row", row)
            # print("col_key", col_key)
            # print(row["GWP"])
            # print(other_table_refs[2][key][col_key])
            # print(row["GWP"]*other_table_refs[2][key][col_key])
    return consump_per_payload * fuel_sum


def calc_truck_emission_factors_total(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return target_table_ref["Heavy-Duty Truck Forward Journey (full load)"][col_key] + \
        target_table_ref["Heavy-Duty Truck Backhaul (full load)"][col_key]


@ dataclass
class HeavyDutyTruckEF:

    def __post_init__(self, user_input):
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")
        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_origin_to_destination,
                              func_to_apply=co2_for_class8_diesel,
                              included_cols=[
                                  "Class 8B Diesel Truck Emission Factors (g/mi.)"],
                              included_rows=['CO2'], other_table_refs=[self.truck_fuel_economy_and_resultant_energy_consumption,
                                                                       self.constants.table_3_fuel_specifications_liquid_fuels,
                                                                       self.constants.table_4_carbon_and_sulfer_ratios],
                              # hack the keymap to use same function for forward and backward trip
                              extra={"trip_econ": "Trip From Product Origin to Destination"})

        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_destination_to_origin,
                              func_to_apply=co2_for_class8_diesel,
                              included_cols=[
                                  "Class 8B Diesel Truck Emission Factors (g/mi.)"],
                              included_rows=['CO2'], other_table_refs=[self.truck_fuel_economy_and_resultant_energy_consumption,
                                                                       self.constants.table_3_fuel_specifications_liquid_fuels,
                                                                       self.constants.table_4_carbon_and_sulfer_ratios],
                              # hack the keymap to use same function for forward and backward trip
                              extra={"trip_econ": "Trip From Product Destination Back to Origin"})

        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_origin_to_destination,
                              func_to_apply=emission_factors_calc_diesel, included_cols=[
                                  "Diesel"],
                              other_table_refs=[
                                  self.truck_fuel_economy_and_resultant_energy_consumption,
                                  self.constants.table_3_fuel_specifications_liquid_fuels],
                              # hack the keymap to use same function for forward and backward trip
                              extra={"trip_econ": "Trip From Product Origin to Destination"})

        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_destination_to_origin,
                              func_to_apply=emission_factors_calc_diesel, included_cols=[
                                  'Diesel'],
                              other_table_refs=[
                                  self.truck_fuel_economy_and_resultant_energy_consumption,
                                  self.constants.table_3_fuel_specifications_liquid_fuels],
                              # hack the keymap to use same function for forward and backward trip
                              extra={"trip_econ": "Trip From Product Destination Back to Origin"})

        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_origin_to_destination,
                              func_to_apply=emission_factors_calc_fill_middle,
                              excluded_rows=["SOx", "CO2"],
                              excluded_cols=[
                                  "Class 8B Diesel Truck Emission Factors (g/mi.)", "Diesel"],
                              other_table_refs=[
                                  self.emission_ratios_by_fuel_type_relative_to_baseline_fuel, ],
                              other_tables_keymap={f"{self.emission_ratios_by_fuel_type_relative_to_baseline_fuel['full_table_name']}": {
                                  "row_keymap": {}, "col_keymap": {'Ethanol': 'E90', 'Methanol': 'M90'}}},
                              )
        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_destination_to_origin,
                              func_to_apply=emission_factors_calc_fill_middle,
                              excluded_rows=["SOx", "CO2"],
                              excluded_cols=[
                                  "Class 8B Diesel Truck Emission Factors (g/mi.)", "Diesel"],
                              other_table_refs=[
                                  self.emission_ratios_by_fuel_type_relative_to_baseline_fuel, ],
                              other_tables_keymap={f"{self.emission_ratios_by_fuel_type_relative_to_baseline_fuel['full_table_name']}": {
                                  "row_keymap": {}, "col_keymap": {'Ethanol': 'E90', 'Methanol': 'M90'}}},
                              )

        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_origin_to_destination,
                              func_to_apply=co2_for_renew_diesel_forward,
                              included_cols=[
                                  "Renewable Diesel"],
                              included_rows=['CO2'], other_table_refs=[self.select_biodiesel,
                                                                       self.constants.table_3_fuel_specifications_liquid_fuels,
                                                                       self.constants.table_4_carbon_and_sulfer_ratios,
                                                                       self.constants.table_3_fuel_specifications_gaseous_fuels])
        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_destination_to_origin,
                              func_to_apply=co2_for_renew_diesel_backward,
                              included_cols=[
                                  "Renewable Diesel"],
                              included_rows=['CO2'], other_table_refs=[self.select_biodiesel,
                                                                       self.constants.table_3_fuel_specifications_liquid_fuels,
                                                                       self.constants.table_4_carbon_and_sulfer_ratios,
                                                                       self.constants.table_3_fuel_specifications_gaseous_fuels])

        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_origin_to_destination,
                              func_to_apply=so2_for_renew_diesel_forward,
                              included_cols=[
                                  "Renewable Diesel"],
                              included_rows=['SOx'], other_table_refs=[self.select_biodiesel,
                                                                       self.constants.table_3_fuel_specifications_liquid_fuels,
                                                                       self.constants.table_4_carbon_and_sulfer_ratios,
                                                                       self.constants.table_3_fuel_specifications_gaseous_fuels])

        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_destination_to_origin,
                              func_to_apply=so2_for_renew_diesel_backward,
                              included_cols=[
                                  "Renewable Diesel"],
                              included_rows=['SOx'], other_table_refs=[self.select_biodiesel,
                                                                       self.constants.table_3_fuel_specifications_liquid_fuels,
                                                                       self.constants.table_4_carbon_and_sulfer_ratios,
                                                                       self.constants.table_3_fuel_specifications_gaseous_fuels])

        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_origin_to_destination,
                              func_to_apply=co2_emissions_factors_most_fuels,
                              included_cols=[
                                  "LNG",	"DME",	"FTD",	"Ethanol",	"Methanol",	"LPG",	"Biodiesel",	"Renewable Gasoline", "Hydrogen"],
                              included_rows=['CO2'], other_table_refs=[
                                  self.constants.table_3_fuel_specifications_liquid_fuels,
                                  self.constants.table_4_carbon_and_sulfer_ratios,
                              ],
                              other_tables_keymap={f"{self.constants.table_3_fuel_specifications_liquid_fuels['full_table_name']}": {
                                  "row_keymap": {"LNG": "Liquefied natural gas (LNG)", "DME": "Dimethyl ether (DME)", "FTD": "Dimethyl ether (DME)", "LPG": "Liquefied petroleum gas (LPG)", "Biodiesel": "Methyl ester (biodiesel, BD)", "Hydrogen": "Liquid hydrogen", "Renewable Gasoline": "Renewable gasoline"}, "col_keymap": {}}},)

        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_destination_to_origin,
                              func_to_apply=co2_emissions_factors_most_fuels,
                              included_cols=[
                                  "LNG",	"DME",	"FTD",	"Ethanol",	"Methanol",	"LPG",	"Biodiesel",	"Renewable Gasoline", "Hydrogen"],
                              included_rows=['CO2'], other_table_refs=[
                                  self.constants.table_3_fuel_specifications_liquid_fuels,
                                  self.constants.table_4_carbon_and_sulfer_ratios,
                              ],
                              other_tables_keymap={f"{self.constants.table_3_fuel_specifications_liquid_fuels['full_table_name']}": {
                                  "row_keymap": {"LNG": "Liquefied natural gas (LNG)", "DME": "Dimethyl ether (DME)", "FTD": "Dimethyl ether (DME)", "LPG": "Liquefied petroleum gas (LPG)", "Biodiesel": "Methyl ester (biodiesel, BD)", "Hydrogen": "Liquid hydrogen", "Renewable Gasoline": "Renewable gasoline"}, "col_keymap": {}}},)

        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_origin_to_destination,
                              func_to_apply=so2_emissions_factors,
                              included_cols=[
                                  "LNG",	"DME",	"FTD",	"Ethanol",	"Methanol",	"LPG",	"Biodiesel",	"Renewable Gasoline", "Hydrogen"],
                              included_rows=['SOx'], other_table_refs=[
                                  self.constants.table_3_fuel_specifications_liquid_fuels,
                                  self.constants.table_4_carbon_and_sulfer_ratios,
                              ],
                              other_tables_keymap={f"{self.constants.table_3_fuel_specifications_liquid_fuels['full_table_name']}": {
                                  "row_keymap": {"LNG": "Liquefied natural gas (LNG)", "DME": "Dimethyl ether (DME)", "FTD": "Dimethyl ether (DME)", "LPG": "Liquefied petroleum gas (LPG)", "Biodiesel": "Methyl ester (biodiesel, BD)", "Hydrogen": "Liquid hydrogen", "Renewable Gasoline": "Renewable gasoline"}, "col_keymap": {}}},)
        fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_destination_to_origin,
                              func_to_apply=so2_emissions_factors,
                              included_cols=[
                                  "LNG",	"DME",	"FTD",	"Ethanol",	"Methanol",	"LPG",	"Biodiesel",	"Renewable Gasoline", "Hydrogen"],
                              included_rows=['SOx'], other_table_refs=[
                                  self.constants.table_3_fuel_specifications_liquid_fuels,
                                  self.constants.table_4_carbon_and_sulfer_ratios,
                              ],
                              other_tables_keymap={f"{self.constants.table_3_fuel_specifications_liquid_fuels['full_table_name']}": {
                                  "row_keymap": {"LNG": "Liquefied natural gas (LNG)", "DME": "Dimethyl ether (DME)", "FTD": "Dimethyl ether (DME)", "LPG": "Liquefied petroleum gas (LPG)", "Biodiesel": "Methyl ester (biodiesel, BD)", "Hydrogen": "Liquid hydrogen", "Renewable Gasoline": "Renewable gasoline"}, "col_keymap": {}}},)
        fill_calculated_cells(target_table_ref=self.heavy_duty_truck_emission_factors,
                              func_to_apply=calc_truck_emission_factors_forward_backward,

                              included_rows=[
                                  "Heavy-Duty Truck Forward Journey (full load)"],
                              other_table_refs=[
                                  self.truck_fuel_economy_and_resultant_energy_consumption,
                                  self.constants.table_1_100year_gwp,
                                  self.truck_emission_factors_of_fuel_combustion_origin_to_destination
                              ], extra={"trip_details": "Trip From Product Origin to Destination"})

        fill_calculated_cells(target_table_ref=self.heavy_duty_truck_emission_factors,
                              func_to_apply=calc_truck_emission_factors_forward_backward,

                              included_rows=[
                                  "Heavy-Duty Truck Backhaul (full load)"],
                              other_table_refs=[
                                  self.truck_fuel_economy_and_resultant_energy_consumption,
                                  self.constants.table_1_100year_gwp,
                                  self.truck_emission_factors_of_fuel_combustion_destination_to_origin
                              ], extra={"trip_details": "Trip From Product Destination Back to Origin"})

        fill_calculated_cells(target_table_ref=self.heavy_duty_truck_emission_factors,
                              func_to_apply=calc_truck_emission_factors_total,
                              included_rows=[
                                  "Heavy-Duty Truck Emissions (full load)"])

        # fill_calculated_cells(target_table_ref=self.truck_emission_factors_of_fuel_combustion_origin_to_destination,
        #                       func_to_apply=emission_factors_calc, excluded_rows=[
        #                           'SOx', 'CO2'],
        #                       excluded_cols=[
        #                           'Class 8B Diesel Truck Emission Factors (g/mi.)', 'Diesel'],
        #                       other_tables_keymap={f"{self.emission_ratios_by_fuel_type_relative_to_baseline_fuel['full_table_name']}": {
        #                           "row_keymap": {}, "col_keymap": {'Ethanol': 'E90', 'Methanol': 'M90'}}},
        #                       other_table_refs=[self.emission_ratios_by_fuel_type_relative_to_baseline_fuel])

    # def calculate_heavy_duty_truck_ef(self

    #                                   ):
    #     print("in heavy_duty_truck")
    #     print(self.heavy_duty_truck_emission_factors)
    #     for row_key in self.heavy_duty_truck_emission_factors.keys():
    #         print(self.heavy_duty_truck_emission_factors[row_key])
    #         if row_key != "row_index_name":
    #             for col_key in self.heavy_duty_truck_emission_factors[row_key].keys():
    #                 print(
    #                     self.heavy_duty_truck_emission_factors[row_key][col_key])
    # Note, copying and pasting strings from excel will lose the space before parenthesis ' ()',
    # but the dictionary keys do include the space

    # I could have a function that takes a list of row keys and col keys to include, it will skip others
    # then I can call it multiple times to fill in table -- if some table cells reference other table cells
    # the order of function calls matters
    # we will only do one other table at a time? or two?
    # how to pass in a function to define the calc that will be called?
    # the function will have to be aware of the contents and order of the table list. But I think I can define an entire calculation
    # will have to do multiple passes to fill in rows/ columns with different calc functions . . .
    # remember, we always write by column.
    # def calc(func_to_apply(other_table_refs=None, other_tables_keymap=None, extra=None)-use lambda, included_rows = None, included_cols = None, excluded_rows = None, excluded_cols = None, other_tables_keymap = {table1: {col_keymap: {old_key: new_key}, row_keymap={old_key: new_key}}, other_table_refs[list of tables to referenc] = none, )

    def func_to_apply(row_key, col_key, other_table_refs=None, other_tables_keymap=None, extra=None):
        pass

    constants: Constants

    user_input: InitVar[Dict] = {}

    # Heavy-Duty Truck EF sheet, table: Heavy-Duty Truck Emission Factors
    # all fuels for pipeline transport modes
    # CALCULATED
    heavy_duty_truck_emission_factors: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Heavy_Duty_Truck_Emission_Factors', 'heavy_duty_truck'))
    # 'Heavy-Duty Truck Emission Factors'))

    # Heavy-Duty Truck EF sheet, table: Fuel Economy and Resultant Energy Consumption of Heavy-Duty Trucks
    # USER INPUT
    # CALCULATED
    truck_fuel_economy_and_resultant_energy_consumption: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Fuel_Economy_and_Resultant_Energy_Consumption_of_Heavy_Duty_Trucks', 'heavy_duty_truck'))
    #'Fuel Economy and Resultant Energy Consumption of Heavy-Duty Trucks'

    # Heavy-Duty Truck EF sheet, cell Select Biodiesel for Simulating Oil-Based Renewable Diesel
    # USER INPUT
    # options: 1 --Renewable Diesel I (SuperCetane); 2 --Renewable Diesel II (UOP-HDO); 3 --Renewable Diesel III (PNNL-HTL)
    select_biodiesel: int = 2

    # Heavy-Duty Truck EF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation: Trip From Product Origin to Product Destination (grams per mmBtu of fuel burned)
    # USER INPUT
    # CALCULATED
    truck_emission_factors_of_fuel_combustion_origin_to_destination: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
            'Emission_Factors_of_Fuel_Combustion_for_Feedstock_and_Fuel_Transportation_Trip_From_Product_Origin_to_Product_Destination_Heavy_Duty_Truck', 'heavy_duty_truck'))
    # 'Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Heavy-Duty Truck (full load)'))

    # Heavy-Duty Truck EF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation: Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned)
    # USER INPUT
    # CALCULATED
    truck_emission_factors_of_fuel_combustion_destination_to_origin: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
            'Emission_Factors_of_Fuel_Combustion_for_Feedstock_and_Fuel_Transportation_Trip_From_Product_Destination_Back_to_Product_Origin_Heavy_Duty_Truck', 'heavy_duty_truck'))

    # Heavy-Duty Truck EF sheet, table: Emission Ratios by Fuel Type Relative to Baseline Fuel
    # USER INPUT
    # STATIC
    emission_ratios_by_fuel_type_relative_to_baseline_fuel: Dict = field(
        default_factory=lambda: build_dict_from_defaults(
            'Emission_Ratios_by_Fuel_Type_Relative_to_Baseline_Fuel', 'heavy_duty_truck'))
