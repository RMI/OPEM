from opem.input.input import standardize_input
from opem.input.user_input import UserInput
from opem.transport.pipeline_EF import PipelineEF
from opem.transport.rail_EF import RailEF
from opem.transport.tanker_barge_EF import TankerBargeEF

from opem.transport import HeavyDutyTruckEF
from dataclasses import InitVar, dataclass, field, asdict
from typing import Dict
from math import isnan
from opem.combustion.combustion_EF import CombustionEF
from opem.constants import Constants
from opem.input import get_product_slate_csv
from opem.input.opgee_input import OpgeeInput
from opem.products.product_slate import ProductSlate
from opem.transport.petrochem_EF import PetroChemEF

from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells, count_list
from opem.transport.transport_EF import TransportEF


def verify_user_fuel_shares(user_shares):
    for key, row in user_shares.items():
        if key not in ["full_table_name", "row_index_name"]:
            share_sum = sum(share for share in row.values()
                            if not isnan(share))
            if share_sum != 1:
                raise(ValueError(
                    f'Shares of fuel types for {key} do not add to 1. Sum is {share_sum}'))
    print("fuel shares valid")
# Define functions for filling calculated cells in the tables here


def calc_gas_production_volume(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs["gas_prod_volume"] / other_table_refs["table_6"]["Natural Gas (MCF/BOE)"]["conversion factor"]


def calc_oil_volume_ratio(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs["oil_volume"] / other_table_refs["product_slate"]["Barrels of Crude per Day"]["Flow"]


def calc_total_field_ngl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    if other_table_refs["ngl_volume_source"] == 1:
        if other_table_refs["user_input_field_volume"] is None:
            print(
                "Expected user input for Total field NGL volume (BOED) but none was given.")
            print("Using default value of 1000.")
            return 1000
        return other_table_refs["user_input_field_volume"]
    elif other_table_refs["ngl_volume_source"] == 2:
        return other_table_refs["c2"] + other_table_refs["c3"] + other_table_refs["c4"] + other_table_refs["c5"]


def calc_opgee_coke_mass(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return (other_table_refs["coke_mass"] *
            other_table_refs["table_5"]["Petroleum Coke Density, average bbl/ton"]["density"] /
            other_table_refs["table_2"]["kg per short ton"]["Conversion Factor"])


def calc_total_boe(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return (other_table_refs["gas_vol"]["row"]["col"] +
            other_table_refs["oil_vol"] +
            other_table_refs["ngl_vol"]["row"]["col"] +
            other_table_refs["coke_mass"]["row"]["col"])


def calc_product_slate(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if target_table_ref["full_table_name"] == "Refinery_Product_Transport":
        if row_key == "Coke":
            return other_table_refs["opgee_coke_mass"] + other_table_refs["product_slate_mass"][row_key]["Flow"] * other_table_refs["oil_vol_ratio"]["row"]["col"]
        return other_table_refs["product_slate_mass"][row_key]["Flow"] * other_table_refs["oil_vol_ratio"]["row"]["col"]
    if target_table_ref["full_table_name"] == "refinery_product_combustion":
        if row_key == "Coke":
            return other_table_refs["product_slate_mass"][row_key]["Flow"] * other_table_refs["oil_vol_ratio"]["row"]["col"]
        return other_table_refs["product_slate_vol"][row_key]["Flow"] * other_table_refs["oil_vol_ratio"]["row"]["col"]


def calc_sum(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    sum = 0
    # don't use name wrapper for target table, makes reuse difficult.
    for row in target_table_ref.items():
        if row[0] not in ["full_table_name", "row_index_name", "Sum", "NGLs"]:
            sum += row[1][col_key]
    return sum


def lookup_emission_factors_transport(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs["transport_em_factors_by_mass"][col_key][row_key]


def calc_total_em(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    # print("")
    return target_table_ref[row_key]["Kilograms of Product per Day"] * target_table_ref[row_key][other_tables_keymap[col_key]] / 1000


def calc_em_intensity(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    return target_table_ref[row_key][other_tables_keymap[col_key]] / other_table_refs["row"]["col"]

# NGL transport


def calc_ngl_product_slate(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return (other_tables_keymap["opgee"][row_key] *
            other_table_refs[0][other_tables_keymap["constants"]
                                [row_key]]["Density, grams/gal"] *
            42/1000)

# coke combustion


def fetch_upstream_coke(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs["opgee_coke_mass"]

# natural gas combustion


def fetch_upstream_gas(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs["gas_prod_vol"]

# NGL combustion


def fetch_upstream_ngl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Ethane":
        return other_table_refs["ngl_c2_vol"] * (1 - other_table_refs["ngl_c2_percent"])
    return other_table_refs[row_key]

# combustion


def lookup_emission_factors_combustion(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Coke":
        return other_table_refs["CombustionEF::ProductEmFactorsSolid"][extra["fuel_lookup"][row_key]]["Total GHGs (kg CO2eq. per kg petcoke)"]
    else:
        return other_table_refs["CombustionEF::ProductEmFactorsPet"][extra["fuel_lookup"][row_key]]["Total GHGs (kg CO2eq. per bbl)"]


def lookup_emission_factors_nat_gas(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs["CombustionEF::ProductEmFactorsNaturalGas"][extra["fuel_lookup"][row_key]]["Total GHGs (kg CO2eq. per scf)"] * 1000


def lookup_emission_factors_ngl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Sum":
        return other_table_refs[1]["Natural Gas Liquid Average Estimate"]["Total GHGs (kg CO2eq. per bbl)"]
    return other_table_refs[0][row_key]["Total GHGs (kg CO2eq. per bbl)"]


def calc_total_em_combust(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if col_key == "Total Combustion Emissions (kg CO2eq/day)":
        return (target_table_ref[row_key]["Volume or Mass of Product per Day"] *
                target_table_ref[row_key]["Combustion Emission Factors"] *
                target_table_ref[row_key]["% Combusted"])
    if row_key == "Coke":
        emissions = (other_table_refs[1][extra["fuel_lookup"][row_key]]
                     [extra["coke_col_lookup"][col_key]] *
                     target_table_ref[row_key]["Volume or Mass of Product per Day"] *
                     target_table_ref[row_key]["% Combusted"] /
                     other_table_refs[2]["kg per short ton"]["Conversion Factor"])
        if col_key == "Total Combustion CO2 Emissions (kg CO2 /day)":
            return emissions
        return emissions / 1000
    result = (other_table_refs[0][extra["fuel_lookup"][row_key]]
              [extra["col_lookup"][col_key]] *
              target_table_ref[row_key]["Volume or Mass of Product per Day"] *
              target_table_ref[row_key]["% Combusted"] * 42)
    if col_key == "Total Combustion CO2 Emissions (kg CO2 /day)":
        return result
    return result / 1000


def calc_total_em_nat_gas(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if col_key == "Total Combustion Emissions (kg CO2eq/day)":
        return (target_table_ref[row_key]["Volume or Mass of Product per Day"] *
                target_table_ref[row_key]["Combustion Emission Factors"] *
                target_table_ref[row_key]["% Combusted"])
    result = (other_table_refs[0][extra["fuel_lookup"][row_key]]
              [extra["col_lookup"][col_key]] *
              target_table_ref[row_key]["Volume or Mass of Product per Day"]
              )
    if col_key == "Total Combustion CO2 Emissions (kg CO2 /day)":
        return result * 1000
    return result


def calc_total_em_sum_ngl(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if other_table_refs[0] == 1:
        if col_key == "Total Combustion Emissions (kg CO2eq/day)":
            return (target_table_ref[row_key]["Volume or Mass of Product per Day"] *
                    target_table_ref[row_key]["Combustion Emission Factors"] *
                    target_table_ref[row_key]["% Combusted"])
        return (other_table_refs[1]["Natural Gas Liquid Average Estimate"][extra[col_key]])
    else:
        em_sum = 0
        for row, col in target_table_ref.items():
            if row not in ["Sum", "full_table_name", "row_index_name"]:
                em_sum += col[col_key]
        return em_sum
# Total Combustion Emissions Table


def sum_all_combust(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return (other_table_refs[0]["Sum"][col_key] +
            other_table_refs[1]["Coke"][col_key] +
            other_table_refs[2]["Natural Gas"][col_key] +
            other_table_refs[3]["Sum"][col_key]
            )
# non-combusted product emissions


def calc_product_slate_non_combust(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Ethane":
        return other_table_refs["ngl_c2"] * other_table_refs["%_allocated_ethylene"]
    return other_table_refs["product_slate"][row_key]["Flow"] * other_table_refs["oil_vol_ratio"]["row"]["col"]

# fetch emissions factors


def fetch_emission_factors_non_combusted(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return other_table_refs


def calc_total_em_non_combust(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if col_key == "Total Process Emissions (kg CO2eq.)":
        return target_table_ref[row_key]["Volume or Mass of Product per Day"] * target_table_ref[row_key]["Emission Factors"]
    petrochem_em = (target_table_ref[row_key]["Volume or Mass of Product per Day"] *
                    other_table_refs[0][extra[col_key]]["mass"] / other_table_refs[1]["Natural Gas Liquids"]["bbl (HHV)"])
    if col_key == "Total Process CO2 Emissions (kg CO2)":
        return petrochem_em
    if col_key == "Total Process CH4 Emissions (kg CH4)":

        return petrochem_em/1000
    if col_key == "Total Process N2O Emissions (kg N2O)":
        return petrochem_em/1000000


@dataclass
class OPEM:

    def __post_init__(self, user_input):
        if type(user_input) == dict:
            # this allows us to get input from a dict generated from another dataclass
            initialize_from_dataclass(self, user_input)
        elif type(user_input) == list:
            initialize_from_list(self, user_input)
        else:
            raise ValueError("Please pass a list or dictionary to initialize")

        # fill_calculated_cells(target_table_ref=self.transport_results,
        #                       func_to_apply=calc_product_slate_combustion_sum,
        #                       included_cols=["Transport Emissions (kg CO2eq. / bbl of crude)"],
        #                       other_table_refs=[self.transport_ef.tanker_barge_ef.share_of_petroleum_products])

        # fill calc fields related to OPGEE input
        # calc_gas_production_volume
        fill_calculated_cells(target_table_ref=self.gas_production_volume_boed,
                              func_to_apply=calc_gas_production_volume,
                              other_table_refs={"gas_prod_volume": self.opgee_input.gas_production_volume,
                                                "table_6": self.constants.table_6_boe_conversions})

        # calc_oil_volume_ratio
        fill_calculated_cells(target_table_ref=self.oil_volume_ratio_to_prelim,
                              func_to_apply=calc_oil_volume_ratio,
                              other_table_refs={"oil_volume": self.opgee_input.oil_production_volume,
                                                "product_slate": self.product_slate.volume_flow_bbl})

        # calc_total_field_ngl

        fill_calculated_cells(target_table_ref=self.total_field_ngl_volume,
                              func_to_apply=calc_total_field_ngl,
                              other_table_refs={"ngl_volume_source": self.ngl_volume_source,
                                                "user_input_field_volume": self.total_field_ngl_volume_user_input,
                                                "c2": self.opgee_input.ngl_c2_volume,
                                                "c3": self.opgee_input.ngl_c3_volume,
                                                "c4": self.opgee_input.ngl_c4_volume,
                                                "c5": self.opgee_input.ngl_c5plus_volume})

        # calc_opgee_coke_mass
        fill_calculated_cells(target_table_ref=self.opgee_coke_mass_boed,
                              func_to_apply=calc_opgee_coke_mass,
                              other_table_refs={"coke_mass": self.opgee_input.opgee_coke_mass,
                                                "table_5": self.constants.table_5_solid_fuel_densities,
                                                "table_2": self.constants.table_2_conversion_factors})
        # calc_total_boe
        fill_calculated_cells(target_table_ref=self.total_boe_produced,
                              func_to_apply=calc_total_boe,
                              other_table_refs={"gas_vol": self.gas_production_volume_boed,
                                                "oil_vol": self.opgee_input.oil_production_volume,
                                                "ngl_vol": self.total_field_ngl_volume,
                                                "coke_mass": self.opgee_coke_mass_boed})

        # Refinery Transport Table
        # calc_product_slate
        fill_calculated_cells(target_table_ref=self.refinery_product_transport,
                              func_to_apply=calc_product_slate,
                              included_cols=["Kilograms of Product per Day"],
                              excluded_rows=["Sum"],
                              other_table_refs={"product_slate_mass": self.product_slate.mass_flow_kg,
                                                "oil_vol_ratio": self.oil_volume_ratio_to_prelim,
                                                "opgee_coke_mass": self.opgee_input.opgee_coke_mass})

        # lookup refinery transport emissions factors
        fill_calculated_cells(target_table_ref={"refinery_prod_trans": self.refinery_product_transport, "has_wrapper": True},
                              func_to_apply=lookup_emission_factors_transport,
                              included_cols=["Emissions Factor (g CO2eq/kg product)",
                                             "CO2 Emissions Factor (g CO2/kg product)",
                                             "CH4 Emissions Factor (g CH4/kg product)",
                                             "N2O Emissions Factor (g N2O/kg product)",
                                             ],
                              excluded_rows=["Sum"],
                              other_table_refs={"transport_em_factors_by_mass": self.transport_ef.transport_emissions_by_prod_mass})

        # calc total refinery transport emissions for all gasses
        fill_calculated_cells(target_table_ref=self.refinery_product_transport,
                              func_to_apply=calc_total_em,
                              included_cols=["Total Transport Emissions (kg CO2eq/ day)",
                                             "Total Transport CO2 Emissions (kg CO2/ day)",
                                             "Total Transport CH4 Emissions (kg CH4/ day)",
                                             "Total Transport N2O Emissions (kg N2O/ day)"],
                              other_tables_keymap={"Total Transport Emissions (kg CO2eq/ day)": "Emissions Factor (g CO2eq/kg product)",
                                                   "Total Transport CO2 Emissions (kg CO2/ day)":  "CO2 Emissions Factor (g CO2/kg product)",
                                                   "Total Transport CH4 Emissions (kg CH4/ day)": "CH4 Emissions Factor (g CH4/kg product)",
                                                   "Total Transport N2O Emissions (kg N2O/ day)": "N2O Emissions Factor (g N2O/kg product)"},
                              excluded_rows=["Sum"],
                              )

        # calc refinery product emissions intensity for all gasses
        fill_calculated_cells(target_table_ref=self.refinery_product_transport,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Transport Emissions Intensity (kg CO2eq. /BOE)",
                                             "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Transport N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Transport Emissions Intensity (kg CO2eq. /BOE)": "Total Transport Emissions (kg CO2eq/ day)",
                                                   "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)": "Total Transport CO2 Emissions (kg CO2/ day)",
                                                   "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)": "Total Transport CH4 Emissions (kg CH4/ day)",
                                                   "Total Transport N2O Emissions Intensity (kg N2O / BOE)": "Total Transport N2O Emissions (kg N2O/ day)"},
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)

        # Refinery transport Sums
        fill_calculated_cells(target_table_ref=self.refinery_product_transport,
                              func_to_apply=calc_sum,
                              included_cols=["Kilograms of Product per Day",
                                             "Total Transport Emissions (kg CO2eq/ day)",
                                             "Transport Emissions Intensity (kg CO2eq. /BOE)",
                                             "Total Transport CO2 Emissions (kg CO2/ day)",
                                             "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Transport CH4 Emissions (kg CH4/ day)",
                                             "Total Transport N2O Emissions (kg N2O/ day)",
                                             "Total Transport N2O Emissions Intensity (kg N2O / BOE)"
                                             ],
                              included_rows=["Sum"])

        # NGL Transport Table

        # calc_product_slate_ngl
        fill_calculated_cells(target_table_ref=self.ngl_transport,
                              func_to_apply=calc_ngl_product_slate,
                              included_cols=["Kilograms of Product per Day"],
                              # excluded_rows=["Sum"],
                              other_table_refs=[
                                  self.constants.table_3_fuel_specifications_liquid_fuels],
                              other_tables_keymap={"opgee": {"Ethane": self.opgee_input.ngl_c2_volume,
                                                             "Propane": self.opgee_input.ngl_c3_volume,
                                                             "Butane": self.opgee_input.ngl_c4_volume,
                                                             "Pentanes Plus": self.opgee_input.ngl_c5plus_volume,
                                                             "NGLs": self.total_field_ngl_volume["row"]["col"]},
                                                   "constants": {"Ethane": "Propane",
                                                                 "Propane": "Propane",
                                                                 "Butane": "Butane",
                                                                 "Pentanes Plus": "n-Hexane",
                                                                 "NGLs": "Natural gas liquids"
                                                                 }})

        # lookup ngl transport emissions factors
        fill_calculated_cells(target_table_ref=self.ngl_transport,
                              func_to_apply=lookup_emission_factors_transport,
                              included_cols=["Emissions Factor (g CO2eq/kg product)",
                                             "CO2 Emissions Factor (g CO2/kg product)",
                                             "CH4 Emissions Factor (g CH4/kg product)",
                                             "N2O Emissions Factor (g N2O/kg product)",
                                             ],

                              other_table_refs={"transport_em_factors_by_mass": self.transport_ef.transport_emissions_by_prod_mass})

        # calc total ngl transport emissions for all gasses
        fill_calculated_cells(target_table_ref=self.ngl_transport,
                              func_to_apply=calc_total_em,
                              included_cols=["Total Transport Emissions (kg CO2eq/ day)",
                                             "Total Transport CO2 Emissions (kg CO2/ day)",
                                             "Total Transport CH4 Emissions (kg CH4/ day)",
                                             "Total Transport N2O Emissions (kg N2O/ day)"],
                              other_tables_keymap={"Total Transport Emissions (kg CO2eq/ day)": "Emissions Factor (g CO2eq/kg product)",
                                                   "Total Transport CO2 Emissions (kg CO2/ day)":  "CO2 Emissions Factor (g CO2/kg product)",
                                                   "Total Transport CH4 Emissions (kg CH4/ day)": "CH4 Emissions Factor (g CH4/kg product)",
                                                   "Total Transport N2O Emissions (kg N2O/ day)": "N2O Emissions Factor (g N2O/kg product)"},

                              )

        # calc ngl emissions intensity for all gasses
        fill_calculated_cells(target_table_ref=self.ngl_transport,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Transport Emissions Intensity (kg CO2eq. /BOE)",
                                             "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Transport N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Transport Emissions Intensity (kg CO2eq. /BOE)": "Total Transport Emissions (kg CO2eq/ day)",
                                                   "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)": "Total Transport CO2 Emissions (kg CO2/ day)",
                                                   "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)": "Total Transport CH4 Emissions (kg CH4/ day)",
                                                   "Total Transport N2O Emissions Intensity (kg N2O / BOE)": "Total Transport N2O Emissions (kg N2O/ day)"},

                              other_table_refs=self.total_boe_produced)

        # special case for CO2 emissions intensity
        fill_calculated_cells(target_table_ref=self.ngl_transport,
                              func_to_apply=calc_em_intensity,
                              included_cols=[
                                  "Transport Emissions Intensity (kg CO2eq. /BOE)"],
                              included_rows=["NGLS"],
                              other_tables_keymap={"Transport Emissions Intensity (kg CO2eq. /BOE)": "Total Transport Emissions (kg CO2eq/ day)",
                                                   "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)": "Total Transport CO2 Emissions (kg CO2/ day)",
                                                   "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)": "Total Transport CH4 Emissions (kg CH4/ day)",
                                                   "Total Transport N2O Emissions Intensity (kg N2O / BOE)": "Total Transport N2O Emissions (kg N2O/ day)"},

                              other_table_refs=self.total_field_ngl_volume)

        # NGL transport Sums
        if self.ngl_volume_source == 2:
            fill_calculated_cells(target_table_ref=self.ngl_transport,
                                  func_to_apply=calc_sum,
                                  included_cols=[
                                      "Kilograms of Product per Day",
                                      "Total Transport Emissions (kg CO2eq/ day)",
                                      "Transport Emissions Intensity (kg CO2eq. /BOE)",
                                      "Total Transport CO2 Emissions (kg CO2/ day)",
                                      "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)",
                                      "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)",
                                      "Total Transport CH4 Emissions (kg CH4/ day)",
                                      "Total Transport N2O Emissions (kg N2O/ day)",
                                      "Total Transport N2O Emissions Intensity (kg N2O / BOE)"
                                  ],
                                  included_rows=["NGLs"])

        # refinery product combustion
        # calc_product_slate refinery combustion
        fill_calculated_cells(target_table_ref=self.refinery_product_combustion,
                              func_to_apply=calc_product_slate,
                              included_cols=[
                                  "Volume or Mass of Product per Day"],
                              excluded_rows=["Sum"],
                              other_table_refs={"product_slate_mass": self.product_slate.mass_flow_kg,
                                                "product_slate_vol": self.product_slate.volume_flow_bbl,
                                                "oil_vol_ratio": self.oil_volume_ratio_to_prelim,
                                                "opgee_coke_mass": self.opgee_input.opgee_coke_mass})

        # look up combustion factors
        fill_calculated_cells(target_table_ref={"Combustion Results": self.refinery_product_combustion, "has_wrapper": True},
                              func_to_apply=lookup_emission_factors_combustion,
                              included_cols=["Combustion Emission Factors"],
                              excluded_rows=[
                                  "Sum"],
                              other_table_refs={"CombustionEF::ProductEmFactorsPet": self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                "CombustionEF::ProductEmFactorsSolid": self.combustion_ef.product_combustion_emission_factors_derived_solids},
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)"
                                                     }})
        # calc combustion emissions
        fill_calculated_cells(target_table_ref=self.refinery_product_combustion,
                              func_to_apply=calc_total_em_combust,
                              included_cols=["Total Combustion Emissions (kg CO2eq/day)",
                                             "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions (kg N2O/ day)"],
                              excluded_rows=[
                                  "Sum"],
                              other_table_refs=[self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                self.combustion_ef.product_combustion_emission_factors_derived_solids,
                                                self.constants.table_2_conversion_factors],
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)"
                                                     },
                                     "coke_col_lookup": {"Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per ton",
                                                         "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per ton",
                                                         "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per ton"},
                                     "col_lookup": {
                                  "Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per gallon",
                                  "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per gallon",
                                  "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per gallon"
                              }})

        # calc refinery product combustion emissions intensity for all gasses
        fill_calculated_cells(target_table_ref=self.refinery_product_combustion,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Total Combustion Emissions Intensity (kg CO2eq. / BOE)": "Total Combustion Emissions (kg CO2eq/day)",
                                                   "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)": "Total Combustion CO2 Emissions (kg CO2 /day)",
                                                   "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)": "Total Combustion CH4 Emissions (kg CH4/ day)",
                                                   "Total Combustion N2O Emissions Intensity (kg N2O / BOE)": "Total Combustion N2O Emissions (kg N2O/ day)"},
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)

        # Refinery combustion Sums
        fill_calculated_cells(target_table_ref=self.refinery_product_combustion,
                              func_to_apply=calc_sum,
                              included_cols=["Volume or Mass of Product per Day",
                                             "Total Combustion Emissions (kg CO2eq/day)",
                                             "Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions (kg N2O/ day)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"
                                             ],
                              included_rows=["Sum"])

        # coke combustion
        fill_calculated_cells(target_table_ref=self.coke_combustion,
                              func_to_apply=fetch_upstream_coke,
                              included_cols=[
                                  "Volume or Mass of Product per Day"],
                              # excluded_rows=["Sum"],
                              other_table_refs={"product_slate": self.product_slate.mass_flow_kg,
                                                "opgee_coke_mass": self.opgee_input.opgee_coke_mass})

        # look up combustion factors
        fill_calculated_cells(target_table_ref={"Combustion Results": self.coke_combustion, "has_wrapper": True},
                              func_to_apply=lookup_emission_factors_combustion,
                              included_cols=["Combustion Emission Factors"],

                              other_table_refs={"CombustionEF::ProductEmFactorsPet": self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                "CombustionEF::ProductEmFactorsSolid": self.combustion_ef.product_combustion_emission_factors_derived_solids},
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)"
                                                     }})

        # calc combustion emissions coke
        fill_calculated_cells(target_table_ref=self.coke_combustion,
                              func_to_apply=calc_total_em_combust,
                              included_cols=["Total Combustion Emissions (kg CO2eq/day)",
                                             "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions (kg N2O/ day)"],
                              excluded_rows=[
                                  "Sum"],
                              other_table_refs=[self.combustion_ef.product_combustion_emission_factors_natural_gas,
                                                self.combustion_ef.product_combustion_emission_factors_derived_solids,
                                                self.constants.table_2_conversion_factors],
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)"
                                                     },
                                     "coke_col_lookup": {"Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per ton",
                                                         "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per ton",
                                                         "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per ton"},
                                     "col_lookup": {
                                  "Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per scf",
                                  "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per scf",
                                  "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per scf"
                              }})

        # calc coke combustion emissions intensity for all gasses
        fill_calculated_cells(target_table_ref=self.coke_combustion,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Total Combustion Emissions Intensity (kg CO2eq. / BOE)": "Total Combustion Emissions (kg CO2eq/day)",
                                                   "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)": "Total Combustion CO2 Emissions (kg CO2 /day)",
                                                   "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)": "Total Combustion CH4 Emissions (kg CH4/ day)",
                                                   "Total Combustion N2O Emissions Intensity (kg N2O / BOE)": "Total Combustion N2O Emissions (kg N2O/ day)"},
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)

        # Natural Gas
        # Lookup volume flow
        fill_calculated_cells(target_table_ref=self.natural_gas_combustion,
                              func_to_apply=fetch_upstream_gas,
                              included_cols=[
                                  "Volume or Mass of Product per Day"],
                              # excluded_rows=["Sum"],
                              other_table_refs={"gas_prod_vol": self.gas_production_volume_boed["row"]["col"]})

        # look up combustion factors
        fill_calculated_cells(target_table_ref={"Combustion Results": self.natural_gas_combustion, "has_wrapper": True},
                              func_to_apply=lookup_emission_factors_nat_gas,
                              included_cols=["Combustion Emission Factors"],

                              other_table_refs={
                                  "CombustionEF::ProductEmFactorsNaturalGas": self.combustion_ef.product_combustion_emission_factors_natural_gas},
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)",
                                                     "Natural Gas": "Natural Gas"
                                                     }})

        # calc combustion emissions natural gas
        fill_calculated_cells(target_table_ref=self.natural_gas_combustion,
                              func_to_apply=calc_total_em_nat_gas,
                              included_cols=["Total Combustion Emissions (kg CO2eq/day)",
                                             "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions (kg N2O/ day)"],
                              other_table_refs=[self.combustion_ef.product_combustion_emission_factors_natural_gas,
                                                self.combustion_ef.product_combustion_emission_factors_derived_solids,
                                                self.constants.table_2_conversion_factors],
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke",
                                                     "Fuel Oil": "Distillate Fuel Oil No. 4",
                                                     "Residual fuels": "Residual Fuel Oil No. 6",
                                                     "Liquefied Petroleum Gases (LPG)": "Liquefied Petroleum Gases (LPG)",
                                                     "Natural Gas": "Natural Gas"
                                                     },
                                     "coke_col_lookup": {"Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per ton",
                                                         "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per ton",
                                                         "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per ton"},
                                     "col_lookup": {
                                  "Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per scf",
                                  "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per scf",
                                  "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per scf"
                              }})

        # emissions intensity Natural Gas
        fill_calculated_cells(target_table_ref=self.natural_gas_combustion,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Total Combustion Emissions Intensity (kg CO2eq. / BOE)": "Total Combustion Emissions (kg CO2eq/day)",
                                                   "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)": "Total Combustion CO2 Emissions (kg CO2 /day)",
                                                   "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)": "Total Combustion CH4 Emissions (kg CH4/ day)",
                                                   "Total Combustion N2O Emissions Intensity (kg N2O / BOE)": "Total Combustion N2O Emissions (kg N2O/ day)"},
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)

        # NGL Combustion
        # Lookup volume flow
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=fetch_upstream_ngl,
                              included_cols=[
                                  "Volume or Mass of Product per Day"],
                              other_table_refs={"ngl_c2_vol": self.opgee_input.ngl_c2_volume,
                                                "ngl_c2_percent": self.percent_ngl_c2_to_ethylene,
                                                "Propane": self.opgee_input.ngl_c3_volume,
                                                "Butane": self.opgee_input.ngl_c4_volume,
                                                "Pentanes Plus": self.opgee_input.ngl_c5plus_volume,
                                                "Sum": self.total_field_ngl_volume["row"]["col"]})
        # lookup emissions factors
        # look up combustion factors
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=lookup_emission_factors_ngl,
                              included_cols=["Combustion Emission Factors"],

                              other_table_refs=[self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                self.combustion_ef.ngl_estimate])

        # calc combustion emissions ngl
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=calc_total_em_combust,
                              excluded_rows=["Sum"],
                              included_cols=["Total Combustion Emissions (kg CO2eq/day)",
                                             "Total Combustion CO2 Emissions (kg CO2 /day)",
                                             "Total Combustion CH4 Emissions (kg CH4/ day)",
                                             "Total Combustion N2O Emissions (kg N2O/ day)"],
                              other_table_refs=[self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                self.combustion_ef.product_combustion_emission_factors_derived_solids,
                                                self.constants.table_2_conversion_factors],
                              extra={"fuel_lookup": {"Ethane": "Ethane",
                                                     "Propane": "Propane",
                                                     "Butane": "Butane",
                                                     "Pentanes Plus": "Pentanes Plus"
                                                     },
                                     "coke_col_lookup": {"Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per ton",
                                                         "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per ton",
                                                         "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per ton"},
                                     "col_lookup": {
                                  "Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per gallon",
                                  "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per gallon",
                                  "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per gallon"
                              }})

        # emissions intensity NGL
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Total Combustion Emissions Intensity (kg CO2eq. / BOE)": "Total Combustion Emissions (kg CO2eq/day)",
                                                   "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)": "Total Combustion CO2 Emissions (kg CO2 /day)",
                                                   "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)": "Total Combustion CH4 Emissions (kg CH4/ day)",
                                                   "Total Combustion N2O Emissions Intensity (kg N2O / BOE)": "Total Combustion N2O Emissions (kg N2O/ day)"},
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)

        # sum ngl
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=calc_total_em_sum_ngl,
                              included_cols=[
                                  "Total Combustion Emissions (kg CO2eq/day)",
                                  "Total Combustion CO2 Emissions (kg CO2 /day)",
                                  "Total Combustion CH4 Emissions (kg CH4/ day)",
                                  "Total Combustion N2O Emissions (kg N2O/ day)",
                              ],
                              included_rows=["Sum"],
                              other_table_refs=[
                                  self.ngl_volume_source, self.combustion_ef.ngl_estimate],
                              extra={

                                  "Total Combustion CO2 Emissions (kg CO2 /day)": "kg CO2 per gallon",
                                  "Total Combustion CH4 Emissions (kg CH4/ day)": "g CH4 per gallon",
                                  "Total Combustion N2O Emissions (kg N2O/ day)": "g N2O per gallon"
                              }
                              )
        # emissions intensity NGL SUM
        fill_calculated_cells(target_table_ref=self.ngl_combustion,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Combustion Emissions Intensity (kg CO2eq. / BOE)",
                                             "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)",
                                             "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)",
                                             "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],
                              other_tables_keymap={"Total Combustion Emissions Intensity (kg CO2eq. / BOE)": "Total Combustion Emissions (kg CO2eq/day)",
                                                   "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)": "Total Combustion CO2 Emissions (kg CO2 /day)",
                                                   "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)": "Total Combustion CH4 Emissions (kg CH4/ day)",
                                                   "Total Combustion N2O Emissions Intensity (kg N2O / BOE)": "Total Combustion N2O Emissions (kg N2O/ day)"},
                              included_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)

        # Total Combustion Emissions
        fill_calculated_cells(target_table_ref=self.total_combustion_emissions,
                              func_to_apply=sum_all_combust,
                              other_table_refs=[self.refinery_product_combustion,
                                                self.coke_combustion,
                                                self.natural_gas_combustion,
                                                self.ngl_combustion],)

        # Non-combusted Product emissions
        # calc_product_slate
        fill_calculated_cells(target_table_ref=self.non_combusted_product_emissions,
                              func_to_apply=calc_product_slate_non_combust,
                              included_cols=[
                                  "Volume or Mass of Product per Day"],
                              excluded_rows=["Sum"],
                              other_table_refs={"product_slate": self.product_slate.volume_flow_bbl,
                                                "oil_vol_ratio": self.oil_volume_ratio_to_prelim,
                                                "opgee_coke_mass": self.opgee_input.opgee_coke_mass,
                                                "ngl_c2": self.opgee_input.ngl_c2_volume,
                                                "%_allocated_ethylene": self.percent_ngl_c2_to_ethylene})

        # lookup emission factors non-combusted products
        fill_calculated_cells(target_table_ref=self.non_combusted_product_emissions,
                              func_to_apply=fetch_emission_factors_non_combusted,
                              included_cols=["Emission Factors"],
                              excluded_rows=["Sum"],
                              other_table_refs=self.petrochem_ef.ethylene_conversion_100yr_gwp["Sum"]["kg CO2e/bbl Natural Gas Liquids (HHV)"])

        fill_calculated_cells(target_table_ref=self.non_combusted_product_emissions,
                              func_to_apply=calc_total_em_non_combust,
                              included_cols=["Total Process Emissions (kg CO2eq.)",
                                             "Total Process CO2 Emissions (kg CO2)",
                                             "Total Process CH4 Emissions (kg CH4)",
                                             "Total Process N2O Emissions (kg N2O)"],
                              excluded_rows=["Sum"],
                              extra={"Total Process CO2 Emissions (kg CO2)": "CO2",
                                     "Total Process CH4 Emissions (kg CH4)": "CH4",
                                     "Total Process N2O Emissions (kg N2O)": "N2O"},
                              other_table_refs=[self.petrochem_ef.ethylene_conversion_kg_co2e,
                                                self.petrochem_ef.onsite_energy_inputs])

        # emissions intensity non-combusted
        fill_calculated_cells(target_table_ref=self.non_combusted_product_emissions,
                              func_to_apply=calc_em_intensity,
                              included_cols=["Total Process Emissions Intensity (kg CO2eq./boe total)",
                                             "Total Process CO2 Emissions Intensity (kg CO2/boe total)",
                                             "Total ProcessCH4  Emissions Intensity (kg CH4/boe total)",
                                             "Total Process N2O Emissions Intensity (kg N2O./boe total)"],
                              other_tables_keymap={"Total Process Emissions Intensity (kg CO2eq./boe total)": "Total Process Emissions (kg CO2eq.)",
                                                   "Total Process CO2 Emissions Intensity (kg CO2/boe total)": "Total Process CO2 Emissions (kg CO2)",
                                                   "Total ProcessCH4  Emissions Intensity (kg CH4/boe total)": "Total Process CH4 Emissions (kg CH4)",
                                                   "Total Process N2O Emissions Intensity (kg N2O./boe total)": "Total Process N2O Emissions (kg N2O)"},
                              excluded_rows=["Sum"],
                              other_table_refs=self.total_boe_produced)
        # non-combusted sum
        fill_calculated_cells(target_table_ref=self.non_combusted_product_emissions,
                              func_to_apply=calc_sum,
                              included_cols=[
                                  "Volume or Mass of Product per Day",
                                  "Total Process Emissions Intensity (kg CO2eq./boe total)",
                                  "Total Process CO2 Emissions Intensity (kg CO2/boe total)",
                                  "Total ProcessCH4  Emissions Intensity (kg CH4/boe total)",
                                  "Total Process N2O Emissions Intensity (kg N2O./boe total)",
                                  "Total Process Emissions (kg CO2eq.)",
                                  "Total Process CO2 Emissions (kg CO2)",
                                  "Total Process CH4 Emissions (kg CH4)",
                                  "Total Process N2O Emissions (kg N2O)"
                              ],
                              included_rows=["Sum"])

    def results(self, return_dict=True):

        if return_dict:
            # keys should be tuples based on input output sheet
            return {("Selected Oil"): self.product_slate.product_name,
                    ("Total BOE Produced"): self.total_boe_produced["row"]["col"],
                    ("OPEM Transport", "Refinery Product Transport", "Sum: Kilograms of Product per Day"):
                    self.refinery_product_transport["Sum"]["Kilograms of Product per Day"],
                    ("OPEM Transport", "Refinery Product Transport", "Transport Emissions Intensity (kg CO2eq. /BOE)"): self.refinery_product_transport["Sum"]["Transport Emissions Intensity (kg CO2eq. /BOE)"],
                    ("OPEM Transport", "Refinery Product Transport", "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)"): self.refinery_product_transport["Sum"]["Total Transport CO2 Emissions Intensity (kg CO2 / BOE)"],
                    ("OPEM Transport", "Refinery Product Transport", "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)"): self.refinery_product_transport["Sum"]["Total Transport CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Transport", "Refinery Product Transport", "Total Transport N2O Emissions Intensity (kg N2O / BOE)"): self.refinery_product_transport["Sum"]["Total Transport N2O Emissions Intensity (kg N2O / BOE)"],
                    ("OPEM Transport", "NGL Product Transport", "Sum: Kilograms of Product per Day"):
                    self.ngl_transport["NGLs"]["Kilograms of Product per Day"],
                    ("OPEM Transport", "NGL Product Transport", "Total Transport CO2 Emissions Intensity (kg CO2 / BOE)"): self.ngl_transport["NGLs"]["Transport Emissions Intensity (kg CO2eq. /BOE)"],
                    ("OPEM Transport", "NGL Product Transport", "Total Transport CH4 Emissions Intensity (kg CH4. / BOE)"): self.ngl_transport["NGLs"]["Total Transport CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Transport", "NGL Product Transport", "Total Transport N2O Emissions Intensity (kg N2O / BOE)"): self.ngl_transport["NGLs"]["Total Transport N2O Emissions Intensity (kg N2O / BOE)"],

                    ("OPEM Combustion", "Refinery Product Combustion", "Gasoline Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.refinery_product_combustion["Gasoline"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Jet Fuel Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.refinery_product_combustion["Jet Fuel"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Diesel Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.refinery_product_combustion["Diesel"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Fuel Oil Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.refinery_product_combustion["Fuel Oil"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Coke Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.refinery_product_combustion["Coke"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Residual fuels Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.refinery_product_combustion["Residual fuels"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Liquefied Petroleum Gases (LPG) Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.refinery_product_combustion["Liquefied Petroleum Gases (LPG)"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Total Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.refinery_product_combustion["Sum"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],

                    ("OPEM Combustion", "Refinery Product Combustion", "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"): self.refinery_product_combustion["Sum"]["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"],

                    ("OPEM Combustion", "Refinery Product Combustion", "Gasoline Combustion Emissions Intensity (kg CH4. / BOE)"): self.refinery_product_combustion["Gasoline"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Jet Fuel Combustion Emissions Intensity (kg CH4. / BOE)"): self.refinery_product_combustion["Jet Fuel"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Diesel Combustion Emissions Intensity (kg CH4. / BOE)"): self.refinery_product_combustion["Diesel"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Fuel Oil Combustion Emissions Intensity (kg CH4. / BOE)"): self.refinery_product_combustion["Fuel Oil"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Coke Combustion Emissions Intensity (kg CH4. / BOE)"): self.refinery_product_combustion["Coke"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Residual fuels Combustion Emissions Intensity (kg CH4. / BOE)"): self.refinery_product_combustion["Residual fuels"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Liquefied Petroleum Gases (LPG) Combustion Emissions Intensity (kg CH4. / BOE)"): self.refinery_product_combustion["Liquefied Petroleum Gases (LPG)"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "Refinery Product Combustion", "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"): self.refinery_product_combustion["Sum"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],

                    ("OPEM Combustion", "Refinery Product Combustion", "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"): self.refinery_product_combustion["Sum"]["Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],

                    ("OPEM Combustion", "Coke Combustion (direct offtake and transport from upstream field)", "Coke Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.coke_combustion["Coke"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "Coke Combustion (direct offtake and transport from upstream field)", "Coke Combustion CO2 Emissions Intensity (kg CO2 / BOE)"): self.coke_combustion["Coke"]["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"],
                    ("OPEM Combustion", "Coke Combustion (direct offtake and transport from upstream field)", "Coke Combustion CH4 Emissions Intensity (kg CH4. / BOE)"): self.coke_combustion["Coke"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "Coke Combustion (direct offtake and transport from upstream field)", "Coke Combustion N2O Emissions Intensity (kg N2O / BOE)"): self.coke_combustion["Coke"]["Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],

                    ("OPEM Combustion", "Natural Gas Combustion (direct offtake and transport from upstream field)", "Natural Gas Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.natural_gas_combustion["Natural Gas"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "Natural Gas Combustion (direct offtake and transport from upstream field)", "Natural Gas Combustion CO2 Emissions Intensity (kg CO2 / BOE)"): self.natural_gas_combustion["Natural Gas"]["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"],
                    ("OPEM Combustion", "Natural Gas Combustion (direct offtake and transport from upstream field)", "Natural Gas Combustion CH4 Emissions Intensity (kg CH4. / BOE)"): self.natural_gas_combustion["Natural Gas"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "Natural Gas Combustion (direct offtake and transport from upstream field)", "Natural Gas Combustion N2O Emissions Intensity (kg N2O / BOE)"): self.natural_gas_combustion["Natural Gas"]["Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],

                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Ethane Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.ngl_combustion["Ethane"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Propane Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.ngl_combustion["Propane"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Butane Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.ngl_combustion["Butane"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Pentanes Plus Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.ngl_combustion["Pentanes Plus"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Total NGL Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.ngl_combustion["Sum"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],

                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Total NGL Combustion CO2 Emissions Intensity (kg CO2 / BOE)"): self.ngl_combustion["Sum"]["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"],

                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Ethane Combustion Emissions Intensity (kg CH4. / BOE)"): self.ngl_combustion["Ethane"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Propane Combustion Emissions Intensity (kg CH4. / BOE)"): self.ngl_combustion["Propane"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Butane Combustion Emissions Intensity (kg CH4. / BOE)"): self.ngl_combustion["Butane"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Pentanes Plus Combustion Emissions Intensity (kg CH4. / BOE)"): self.ngl_combustion["Pentanes Plus"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Total NGL Combustion CH4 Emissions Intensity (kg CH4. / BOE)"): self.ngl_combustion["Sum"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],

                    ("OPEM Combustion", "NGL Combustion (direct offtake and transport from upstream field)", "Total NGL Combustion N2O Emissions Intensity (kg N2O / BOE)"): self.ngl_combustion["Sum"]["Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],

                    ("OPEM Combustion", "Total Combustion emissions", "Total Combustion Emissions Intensity (kg CO2eq. / BOE)"): self.total_combustion_emissions["Sum"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"],
                    ("OPEM Combustion", "Total Combustion emissions", "Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"): self.total_combustion_emissions["Sum"]["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"],
                    ("OPEM Combustion", "Total Combustion emissions", "Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"): self.total_combustion_emissions["Sum"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"],
                    ("OPEM Combustion", "Total Combustion emissions", "Total Combustion N2O Emissions Intensity (kg N2O / BOE)"): self.total_combustion_emissions["Sum"]["Total Combustion N2O Emissions Intensity (kg N2O / BOE)"],

                    ("OPEM Combustion", "Non-combusted product emissions", "Sum: BOED"): self.non_combusted_product_emissions["Sum"]["Volume or Mass of Product per Day"],
                    ("OPEM Combustion", "Non-combusted product emissions", "Total Process Emissions Intensity (kg CO2eq./boe total)"): self.non_combusted_product_emissions["Sum"]["Total Process Emissions Intensity (kg CO2eq./boe total)"],
                    ("OPEM Combustion", "Non-combusted product emissions", "Total Process CO2 Emissions Intensity (kg CO2/boe total)"): self.non_combusted_product_emissions["Sum"]["Total Process CO2 Emissions Intensity (kg CO2/boe total)"],
                    ("OPEM Combustion", "Non-combusted product emissions", "Total ProcessCH4  Emissions Intensity (kg CH4/boe total)"): self.non_combusted_product_emissions["Sum"]["Total ProcessCH4  Emissions Intensity (kg CH4/boe total)"],
                    ("OPEM Combustion", "Non-combusted product emissions", "Total Process N2O Emissions Intensity (kg N2O./boe total)"): self.non_combusted_product_emissions["Sum"]["Total Process N2O Emissions Intensity (kg N2O./boe total)"]
                    }
        return [["Output Name", "RESULTS"],
                ["Selected Oil", self.product_slate.product_name],
                ["Total BOE Produced", self.total_boe_produced["row"]["col"]],
                ["*-OPEM Transport-*", ""],
                ["*--Refinery Product Transport", ""],
                ["Sum: Kilograms of Product per Day",
                    self.refinery_product_transport["Sum"]["Kilograms of Product per Day"]],
                ["Transport Emissions Intensity (kg CO2eq. /BOE)", self.refinery_product_transport["Sum"]
                 ["Transport Emissions Intensity (kg CO2eq. /BOE)"]],
                ["Total Transport CO2 Emissions Intensity (kg CO2 / BOE)", self.refinery_product_transport["Sum"]
                 ["Total Transport CO2 Emissions Intensity (kg CO2 / BOE)"]],
                ["Total Transport CH4 Emissions Intensity (kg CH4. / BOE)", self.refinery_product_transport["Sum"]
                 ["Total Transport CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Total Transport N2O Emissions Intensity (kg N2O / BOE)", self.refinery_product_transport["Sum"]
                 ["Total Transport N2O Emissions Intensity (kg N2O / BOE)"]],
                ["*--NGL Product Transport", ""],
                ["Sum: Kilograms of Product per Day",
                    self.ngl_transport["NGLs"]["Kilograms of Product per Day"]],
                ["Transport Emissions Intensity (kg CO2eq. /BOE)", self.ngl_transport["NGLs"]
                 ["Transport Emissions Intensity (kg CO2eq. /BOE)"]],
                ["Total Transport CO2 Emissions Intensity (kg CO2 / BOE)", self.ngl_transport["NGLs"]
                 ["Total Transport CO2 Emissions Intensity (kg CO2 / BOE)"]],
                ["Total Transport CH4 Emissions Intensity (kg CH4. / BOE)", self.ngl_transport["NGLs"]
                 ["Total Transport CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Total Transport N2O Emissions Intensity (kg N2O / BOE)", self.ngl_transport["NGLs"]
                 ["Total Transport N2O Emissions Intensity (kg N2O / BOE)"]],

                ["*-OPEM Combustion-*", ""],
                ["*--Refinery Product Combustion", ""],
                ["*---CO2eq.", ""],
                ["Gasoline Combustion Emissions Intensity (kg CO2eq. / BOE)", self.refinery_product_combustion["Gasoline"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Jet Fuel Combustion Emissions Intensity (kg CO2eq. / BOE)", self.refinery_product_combustion["Jet Fuel"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Diesel Combustion Emissions Intensity (kg CO2eq. / BOE)", self.refinery_product_combustion["Diesel"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Fuel Oil Combustion Emissions Intensity (kg CO2eq. / BOE)", self.refinery_product_combustion["Fuel Oil"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Coke Combustion Emissions Intensity (kg CO2eq. / BOE)", self.refinery_product_combustion["Coke"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Residual fuels Combustion Emissions Intensity (kg CO2eq. / BOE)", self.refinery_product_combustion["Residual fuels"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Liquefied Petroleum Gases (LPG) Combustion Emissions Intensity (kg CO2eq. / BOE)",
                 self.refinery_product_combustion["Liquefied Petroleum Gases (LPG)"]["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)", self.refinery_product_combustion["Sum"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["*---CO2", ""],
                ["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)", self.refinery_product_combustion["Sum"]
                 ["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"]],
                ["*---CH4", ""],
                ["Gasoline Combustion Emissions Intensity (kg CH4. / BOE)", self.refinery_product_combustion["Gasoline"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Jet Fuel Combustion Emissions Intensity (kg CH4. / BOE)", self.refinery_product_combustion["Jet Fuel"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Diesel Combustion Emissions Intensity (kg CH4. / BOE)", self.refinery_product_combustion["Diesel"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Fuel Oil Combustion Emissions Intensity (kg CH4. / BOE)", self.refinery_product_combustion["Fuel Oil"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Coke Combustion Emissions Intensity (kg CH4. / BOE)", self.refinery_product_combustion["Coke"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Residual fuels Combustion Emissions Intensity (kg CH4. / BOE)", self.refinery_product_combustion["Residual fuels"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Liquefied Petroleum Gases (LPG) Combustion Emissions Intensity (kg CH4. / BOE)",
                 self.refinery_product_combustion["Liquefied Petroleum Gases (LPG)"]["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)", self.refinery_product_combustion["Sum"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["*---N2O", ""],
                ["Total Combustion N2O Emissions Intensity (kg N2O / BOE)", self.refinery_product_combustion["Sum"]
                 ["Total Combustion N2O Emissions Intensity (kg N2O / BOE)"]],

                ["*--Coke Combustion (direct offtake and transport from upstream field)", ""],
                ["Coke Combustion Emissions Intensity (kg CO2eq. / BOE)", self.coke_combustion["Coke"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Coke Combustion CO2 Emissions Intensity (kg CO2 / BOE)", self.coke_combustion["Coke"]
                 ["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"]],
                ["Coke Combustion CH4 Emissions Intensity (kg CH4. / BOE)", self.coke_combustion["Coke"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Coke Combustion N2O Emissions Intensity (kg N2O / BOE)", self.coke_combustion["Coke"]
                 ["Total Combustion N2O Emissions Intensity (kg N2O / BOE)"]],

                ["*--Natural Gas Combustion (direct offtake and transport from upstream field)", ""],
                ["Natural Gas Combustion Emissions Intensity (kg CO2eq. / BOE)", self.natural_gas_combustion["Natural Gas"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Natural Gas Combustion CO2 Emissions Intensity (kg CO2 / BOE)", self.natural_gas_combustion["Natural Gas"]
                 ["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"]],
                ["Natural Gas Combustion CH4 Emissions Intensity (kg CH4. / BOE)", self.natural_gas_combustion["Natural Gas"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Natural Gas Combustion N2O Emissions Intensity (kg N2O / BOE)", self.natural_gas_combustion["Natural Gas"]
                 ["Total Combustion N2O Emissions Intensity (kg N2O / BOE)"]],

                ["*--NGL Combustion (direct offtake and transport from upstream field)", ""],
                ["*---CO2eq.", ""],
                ["Ethane Combustion Emissions Intensity (kg CO2eq. / BOE)", self.ngl_combustion["Ethane"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Propane Combustion Emissions Intensity (kg CO2eq. / BOE)", self.ngl_combustion["Propane"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Butane Combustion Emissions Intensity (kg CO2eq. / BOE)", self.ngl_combustion["Butane"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Pentanes Plus Combustion Emissions Intensity (kg CO2eq. / BOE)", self.ngl_combustion["Pentanes Plus"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Total NGL Combustion Emissions Intensity (kg CO2eq. / BOE)", self.ngl_combustion["Sum"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["*---CO2", ""],
                ["Total NGL Combustion CO2 Emissions Intensity (kg CO2 / BOE)", self.ngl_combustion["Sum"]
                 ["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"]],
                ["*---CH4", ""],
                ["Ethane Combustion Emissions Intensity (kg CH4. / BOE)", self.ngl_combustion["Ethane"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Propane Combustion Emissions Intensity (kg CH4. / BOE)", self.ngl_combustion["Propane"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Butane Combustion Emissions Intensity (kg CH4. / BOE)", self.ngl_combustion["Butane"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Pentanes Plus Combustion Emissions Intensity (kg CH4. / BOE)", self.ngl_combustion["Pentanes Plus"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Total NGL Combustion CH4 Emissions Intensity (kg CH4. / BOE)", self.ngl_combustion["Sum"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["*---CH4", ""],
                ["Total NGL Combustion N2O Emissions Intensity (kg N2O / BOE)", self.ngl_combustion["Sum"]
                 ["Total Combustion N2O Emissions Intensity (kg N2O / BOE)"]],

                ["*--Total Combustion emissions", ""],
                ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)", self.total_combustion_emissions["Sum"]
                 ["Total Combustion Emissions Intensity (kg CO2eq. / BOE)"]],
                ["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)", self.total_combustion_emissions["Sum"]
                 ["Total Combustion CO2 Emissions Intensity (kg CO2 / BOE)"]],
                ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)", self.total_combustion_emissions["Sum"]
                 ["Total Combustion CH4 Emissions Intensity (kg CH4. / BOE)"]],
                ["Total Combustion N2O Emissions Intensity (kg N2O / BOE)", self.total_combustion_emissions["Sum"]
                 ["Total Combustion N2O Emissions Intensity (kg N2O / BOE)"]],

                ["*-Non-combusted product emissions-*", ""],
                ["Sum: BOED", self.non_combusted_product_emissions["Sum"]
                    ["Volume or Mass of Product per Day"]],
                ["Total Process Emissions Intensity (kg CO2eq./boe total)", self.non_combusted_product_emissions["Sum"]
                 ["Total Process Emissions Intensity (kg CO2eq./boe total)"]],
                ["Total Process CO2 Emissions Intensity (kg CO2/boe total)", self.non_combusted_product_emissions["Sum"]
                 ["Total Process CO2 Emissions Intensity (kg CO2/boe total)"]],
                ["Total ProcessCH4  Emissions Intensity (kg CH4/boe total)", self.non_combusted_product_emissions["Sum"]
                 ["Total ProcessCH4  Emissions Intensity (kg CH4/boe total)"]],
                ["Total Process N2O Emissions Intensity (kg N2O./boe total)", self.non_combusted_product_emissions["Sum"]["Total Process N2O Emissions Intensity (kg N2O./boe total)"]]]
    constants: Constants
    transport_ef: TransportEF
    petrochem_ef: PetroChemEF
    combustion_ef: CombustionEF
    product_slate: ProductSlate
    opgee_input: OpgeeInput

    # calculate these in post_init
    gas_production_volume_boed: Dict = field(
        default_factory=lambda: {"row": {"col": None}})
    oil_volume_ratio_to_prelim: Dict = field(
        default_factory=lambda: {"row": {"col": None}})
    total_field_ngl_volume: Dict = field(
        default_factory=lambda: {"row": {"col": None}})
    opgee_coke_mass_boed: Dict = field(
        default_factory=lambda: {"row": {"col": None}})
    total_boe_produced: Dict = field(
        default_factory=lambda: {"row": {"col": None}})

    # fill from user_input_dto
    ngl_volume_source: int = None
    percent_ngl_c2_to_ethylene: int = None
    # carries value from user input
    # total_field_ngl_volume will copy this
    # if volume source==1
    total_field_ngl_volume_user_input: int = None

    # will this cause problems if I try to pass in a list?
    user_input: InitVar[Dict] = {}

    # User Inputs & Results sheet, table: OPEM Transport
    # USER INPUT
    # CALCULATED
    refinery_product_transport: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Refinery_Product_Transport', 'results'))

    # User Inputs & Results sheet, table: OPEM Transport
    # CALCULATED
    ngl_transport: Dict = field(
        default_factory=lambda: build_dict_from_defaults('NGL_Transport', 'results'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # USER INPUT
    # CALCULATED
    refinery_product_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Refinery_Product_Combustion', 'results'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # USER INPUT
    # CALCULATED
    coke_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Coke_Combustion', 'results'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # USER INPUT
    # CALCULATED
    natural_gas_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Natural_Gas_Combustion', 'results'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # USER INPUT
    # CALCULATED
    ngl_combustion: Dict = field(
        default_factory=lambda: build_dict_from_defaults('NGL_Combustion', 'results'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # CALCULATED
    total_combustion_emissions: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Total_Combustion_Emissions', 'results'))

    # User Inputs & Results sheet, table: Non-combusted Product Emissions
    # CALCULATED
    non_combusted_product_emissions: Dict = field(
        default_factory=lambda: build_dict_from_defaults('Non_Combusted_Product_Emissions', 'results'))


def run_model(input, return_dict=True):
    """This function orchestrates one or more runs of the OPEM model.


    Example:

    example input #1 (dictionary holding lists of lists): 
                { "user_input": 
                      [["User Inputs & Results", 
                        "Global:", "Assay (Select Oil)", "-",
                        "Field Name B"]],
                  "opgee_input": 
                      [["User Inputs & Results", "Global:", "Gas Production Volume (MCFD)", "-", 600000],
                       ["User Inputs & Results", "Global:", "Oil Production Volume (BOED)", "-", 100000]]
                  "product_slate": 
                      [["volume_flow_bbl", "Barrels of Crude per Day", "Flow", 84851.48652], 
                       ["volume_flow_bbl", "Gasoline", "Flow", 14386.84259], 
                       ["volume_flow_bbl", "Jet Fuel", "Flow", 30485.5812], 
                       ["volume_flow_bbl", "Diesel", "Flow", 19011.05842]],
                        ... }

        example input #2 (dictionary holding dictionaries): 
                {"user_input": {("User Inputs & Results", "Global:", "Assay (Select Oil)", "-"): "Field Name B"},
                 "opgee_input": {("User Inputs & Results", "Global:", "Gas Production Volume (MCFD)", "-"): 600000,
                        ("User Inputs & Results", "Global:", "Oil Production Volume (BOED)", "-"): 100000,
                 "product_slate": {("volume_flow_bbl", "Barrels of Crude per Day", "Flow"): 84851.48652, 
                        ("volume_flow_bbl", "Gasoline", "Flow"): 14386.84259, 
                        ("volume_flow_bbl", "Jet Fuel", "Flow"): 30485.5812, 
                        ("volume_flow_bbl", "Diesel", "Flow"): 19011.05842,
                        ... }

    Args:
        input (list/dict): Either a single dictionary of input parameters, or a list of 
                           dictionaries, each one of which holds input parameters for one 
                           run of the model. The input dictionaries must contain a key "user_input"
                           and may also contain keys "opgee_input" and "product_slate". The value for
                           each key may be either a dictionary or a list of lists. If it is a dictionary,
                           the keys must be tuples of strings which name the input parameter (refer to opem_input.csv and product_slate_input.csv 
                           to find the sequence of strings for each parmeter). 
                           If the value is a list of lists, each list represents one row of input; the first elements 
                           of the list must be the string names and the last element is the value of the input parameter.

                           OPGEE input parameters may be included with "user_input" values. In this case 
                           the "opgee_input" should be omitted.

                           The "product_slate" key should provide complete product slate information for a single product (see product_slate_input.csv).
                           If the "product_slate" key is omitted the program will use the value of the "Assay (Select Oil)" key under "user_input" to 
                           look up the product slate in an internal csv file. If both are provided the value of "Assay (Select Oil)" will be ignored. 
                           Omitting both "product_slate" and "Assay (Select Oil)" will result in an error. 

        return_dict (bool): If true, the function will return model results in the form of a dictionary. Otherwise model results will be returned as a list of lists.

    Returns:
        list/dict: If a single param dictionary is passed as input,
                   the function will return either a dictionary or list of lists (controlled
                   by the return_dict argument) containing results. If a list of 
                   param dictionaries are passed, a list will be returned, holding 
                   results objects (dictionary or list of lists) for each set of input params.
                   See OPEM Input Output.xlsx, "Outputs" sheet, to find the name of each output.

    """
    standardized_input = standardize_input(input)

    run_number = 1
    if isinstance(standardized_input, dict):
        print(f"Run Number {run_number}")
        try:
            return run_batch(**standardized_input, return_dict=return_dict)
        except BaseException as err:
            print(err)
            print("Error")
            return [[f"ERROR in run number {run_number}"]]
    results = []
    for batch in standardized_input:
        print("")
        print(f"Run Number {run_number}")
        try:
            results.append(run_batch(**batch, return_dict=return_dict))
        except:
            print("")
            print("Error! Please check your inputs.")
            results.append([["", f"ERROR in run number {run_number}"]])
        run_number += 1
    return results


def run_batch(user_input, opgee_input=None, product_slate=None, return_dict=True):

    user_input = UserInput(user_input=user_input)
    if opgee_input is not None:
        opgee_input = OpgeeInput(opgee_input=opgee_input)
    else:
        opgee_input = OpgeeInput(opgee_input=asdict(user_input))

    if product_slate is not None:
        print("Processing product slate . . .")
        product_slate = ProductSlate(product_slate_input=product_slate)
        print(f"Oil Name: {product_slate.product_name}")
    else:
        print(f"Oil Name: {user_input.product_name}")
        print("Fetching product slate . . .")
        product_slate = get_product_slate_csv(user_input.product_name)

    constants = Constants(user_input=asdict(user_input))

    print("Processing Tanker/Barge Emission Factors . . .")

    tanker_barge_ef = TankerBargeEF(
        user_input=asdict(user_input), constants=constants, product_slate=product_slate)

    print("Processing Heavy-Duty Truck Emission Factors . . .")

    heavy_duty_truck_ef = HeavyDutyTruckEF(
        user_input=asdict(user_input), constants=constants)

    print("Processing Rail Emission Factors . . .")

    rail_ef = RailEF(user_input=asdict(user_input), constants=constants)

    print("Processing Pipeline Emission Factors . . .")

    pipeline_ef = PipelineEF(user_input=asdict(
        user_input), constants=constants)

    petrochem_ef = PetroChemEF(user_input=asdict(
        user_input), constants=constants)

    transport_ef = TransportEF(user_input=asdict(user_input), pipeline_ef=pipeline_ef,
                               rail_ef=rail_ef,
                               heavy_duty_truck_ef=heavy_duty_truck_ef,
                               tanker_barge_ef=tanker_barge_ef)

    print("Processing Combustion Emission Factors . . .")

    combustion_ef = CombustionEF(user_input=asdict(
        user_input), constants=constants)

    print("Calculating results . . .")
    opem = OPEM(user_input=asdict(user_input), transport_ef=transport_ef,
                combustion_ef=combustion_ef, petrochem_ef=petrochem_ef, product_slate=product_slate, opgee_input=opgee_input, constants=constants)
    print("Model run completed.")

    return opem.results(return_dict)
