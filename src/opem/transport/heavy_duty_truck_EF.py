from dataclasses import InitVar, dataclass, field
from typing import DefaultDict
from opem.constants import Constants

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells

# Define functions for filling calculated cells in the tables here


def emission_factors_calc(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None):
    # handle mapping the rows and columns of the target table to the rows and columns of other tables below
    # this example has only one other table and only maps columns
    # each table will need custom logic to handle rows/columns and however many other tables are passed in
    # we will probably not need to iterate over the other table refs, access via subscripts manually in the
    # custom logic below

    # there might be more keys: other_table_col_key1, other_table_col_key2, etc.
    other_table_col_key = col_key
    other_table_row_key = row_key
    if other_tables_keymap:
        other_table_col_key = (lambda col_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"][col_key] if col_key in
                               other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"].keys() else other_table_col_key)(col_key)

        other_table_row_key = (lambda row_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"][row_key] if row_key in
                               other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"].keys() else other_table_row_key)(row_key)
    return target_table_ref[row_key]["Diesel"] * \
        other_table_refs[0][other_table_row_key][other_table_col_key]


def emission_factors_calc2(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None):
    # handle mapping the rows and columns of the target table to the rows and columns of other tables below
    # this example has only one other table and only maps columns
    # each table will need custom logic to handle rows/columns and however many other tables are passed in
    # we will probably not need to iterate over the other table refs, access via subscripts manually in the
    # custom logic below

    # there might be more keys: other_table_col_key1, other_table_col_key2, etc.
    other_table_col_key = col_key
    other_table_row_key = row_key
    if other_tables_keymap:
        other_table_col_key = (lambda col_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"][col_key] if col_key in
                               other_tables_keymap[other_table_refs[0]["full_table_name"]]["col_keymap"].keys() else other_table_col_key)(col_key)

        other_table_row_key = (lambda row_key: other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"][row_key] if row_key in
                               other_tables_keymap[other_table_refs[0]["full_table_name"]]["row_keymap"].keys() else other_table_row_key)(row_key)

    print('test')

    print(target_table_ref[row_key]['Class 8B Diesel Truck Emission Factors (g/mi.)'] *
          other_table_refs[0][
        'Trip From Product Origin to Destination']['Fuel Economy (miles/diesel gallon)'])
    return target_table_ref[row_key]['Class 8B Diesel Truck Emission Factors (g/mi.)'] * \
        other_table_refs[0][
            'Trip From Product Origin to Destination']['Fuel Economy (miles/diesel gallon)']


@dataclass
class HeavyDutyTruckEF:

    def __post_init__(self, user_input):
        print(type(user_input))
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

        fill_calculated_cells(target_table_ref=self.emission_factors_of_fuel_combustion_origin_to_destination,
                              func_to_apply=emission_factors_calc2, included_cols=[
                                  'Diesel'],
                              other_table_refs=[self.fuel_economy_and_resultant_energy_consumption])

        fill_calculated_cells(target_table_ref=self.emission_factors_of_fuel_combustion_origin_to_destination,
                              func_to_apply=emission_factors_calc, excluded_rows=[
                                  'SOx', 'CO2'],
                              excluded_cols=[
                                  'Class 8B Diesel Truck Emission Factors (g/mi.)', 'Diesel'],
                              other_tables_keymap={f"{self.emission_ratios_by_fuel_type_relative_to_baseline_fuel['full_table_name']}": {
                                  "row_keymap": {}, "col_keymap": {'Ethanol': 'E90', 'Methanol': 'M90'}}},
                              other_table_refs=[self.emission_ratios_by_fuel_type_relative_to_baseline_fuel])

        print('finished post_init')
        print(self.emission_factors_of_fuel_combustion_origin_to_destination)

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
    # def calc(func_to_apply(other_table_refs=None, other_tables_keymap=None)-use lambda, included_rows = None, included_cols = None, excluded_rows = None, excluded_cols = None, other_tables_keymap = {table1: {col_keymap: {old_key: new_key}, row_keymap={old_key: new_key}}, other_table_refs[list of tables to referenc] = none, )

    def func_to_apply(row_key, col_key, other_table_refs=None, other_tables_keymap=None):
        pass

    def calculate_emission_factors_of_fuel_combustion_origin_to_destination(self):
        for row_key, row in self.emission_factors_of_fuel_combustion_origin_to_destination.items():

            if row_key != "row_index_name":
                # handle column that needs special treatment
                for col_key in row.keys():
                    if col_key == 'Diesel':
                        # get a reference to the Diesel cell in current row
                        # set value to be product of prev column in same row and a fixed cell of fuel economy table
                        row[col_key] = row['Class 8B Diesel Truck Emission Factors (g/mi.)'] * self.fuel_economy_and_resultant_energy_consumption[
                            'Trip From Product Origin to Destination']['Fuel Economy (miles/diesel gallon)']
                    # handle rest of columns
                    else:
                        # skip rows that need special treatment
                        if not (row_key in ['SOx', 'CO2']) and not (col_key in ['Class 8B Diesel Truck Emission Factors (g/mi.)']):

                            # deal with other table that needs different keys
                            # always pass in a key map when we reference another table
                            # pass this as a parameter
                            col_key_map = {'Ethanol': 'E90', 'Methanol': 'M90'}
                            # lambda switches table being written col key for table being read col key
                            other_table_col_key = (lambda col_key: col_key_map[col_key] if col_key in
                                                   col_key_map.keys() else col_key)(col_key)
                            print(col_key)
                            row[col_key] = row['Diesel'] * \
                                self.emission_ratios_by_fuel_type_relative_to_baseline_fuel[
                                    row_key][other_table_col_key]
        print(self.emission_factors_of_fuel_combustion_origin_to_destination)
        # if col_key != 'Class 8B Diesel Truck Emission Factors (g/mi.)'
        # print(self.emission_factors_of_fuel_combustion_origin_to_destination)
        # will this cause problems if I try to pass in a list?

    constants: Constants

    user_input: InitVar[DefaultDict] = {}

    # Heavy-Duty Truck EF sheet, table: Heavy-Duty Truck Emission Factors
    # all fuels for pipeline transport modes
    # CALCULATED
    heavy_duty_truck_emission_factors: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Heavy-Duty Truck Emission Factors'))

    # Heavy-Duty Truck EF sheet, table: Fuel Economy and Resultant Energy Consumption of Heavy-Duty Trucks
    # USER INPUT
    # CALCULATED
    truck_fuel_economy_and_resultant_energy_consumption: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Fuel Economy and Resultant Energy Consumption of Heavy-Duty Trucks'))

    # Heavy-Duty Truck EF sheet, cell Select Biodiesel for Simulating Oil-Based Renewable Diesel
    # USER INPUT
    # options: 1 --Renewable Diesel I (SuperCetane); 2 --Renewable Diesel II (UOP-HDO); 3 --Renewable Diesel III (PNNL-HTL)
    select_biodiesel: int = 2

    # Heavy-Duty Truck EF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation: Trip From Product Origin to Product Destination (grams per mmBtu of fuel burned)
    # USER INPUT
    # CALCULATED
    truck_emission_factors_of_fuel_combustion_origin_to_destination: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Origin to Product Destination (grams per mmBtu of fuel burned) -- Heavy-Duty Truck (full load)'))

    # Heavy-Duty Truck EF sheet, table: Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation: Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned)
    # USER INPUT
    # CALCULATED
    truck_emission_factors_of_fuel_combustion_destination_to_origin: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Emission Factors of Fuel Combustion for Feedstock and Fuel Transportation- Trip From Product Destination Back to Product Origin (grams per mmBtu of fuel burned) -- Heavy-Duty Truck (full load)'))

    # Heavy-Duty Truck EF sheet, table: Emission Ratios by Fuel Type Relative to Baseline Fuel
    # USER INPUT
    # STATIC
    emission_ratios_by_fuel_type_relative_to_baseline_fuel: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Emission Ratios by Fuel Type Relative to Baseline Fuel'))
