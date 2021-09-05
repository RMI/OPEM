

from dataclasses import InitVar, dataclass, field
from typing import DefaultDict, Type
from math import isnan
from opem.combustion.combustion_EF import CombustionEF
from opem.products.product_slate import ProductSlate

from opem.transport.heavy_duty_truck_EF import HeavyDutyTruckEF
from opem.transport.pipeline_EF import PipelineEF
from opem.transport.rail_EF import RailEF
from opem.transport.tanker_barge_EF import TankerBargeEF
from opem.utils import initialize_from_dataclass, initialize_from_list, build_dict_from_defaults, fill_calculated_cells
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


def lookup_emission_factors_transport(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    return other_table_refs["TransportEF::TransportEmFactors"][row_key][target_table_ref["Transport Results"][row_key]["Choose Transport Fuel (from drop-down)"]]


def lookup_emission_factors_combustion(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    if row_key == "Coke":
        return other_table_refs["CombustionEF::ProductEmFactorsSolid"][extra["fuel_lookup"][row_key]]["Total GHGs (kg CO2eq. per kg petcoke)"]
    else:
        return other_table_refs["CombustionEF::ProductEmFactorsPet"][extra["fuel_lookup"][row_key]]["Total GHGs (kg CO2eq. per bbl)"]


def calc_emissions_transport(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    try:
        return target_table_ref["Transport Results"][row_key]["Emission Factor (g CO2eq. / kgkm)"] * \
            target_table_ref["Transport Results"][row_key]["Select Distance Traveled (km)"] * \
            other_table_refs["TankerBargeEF::ShareOfPetProducts"]["mass_flow_sum"]["total"] / 100000000
    except TypeError:
        pass


def calc_emissions_combustion(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    if row_key == "Coke":
        return (target_table_ref["Combustion Results"][row_key]["Combustion Emission Factors"] *
                target_table_ref["Combustion Results"][row_key]["% Combusted"] *
                (other_table_refs["ProductSlate::mass_flow"]["Coke"]["Flow"] +
                 other_table_refs["ProductSlate::mass_flow"]["Net Upstream Petcoke"]["Flow"]) /
                other_table_refs["ProductSlate::volume_flow"]["Barrels of Crude per Day"]["Flow"])
    else:
        return (target_table_ref["Combustion Results"][row_key]["Combustion Emission Factors"] *
                target_table_ref["Combustion Results"][row_key]["% Combusted"] *
                other_table_refs["ProductSlate::volume_flow"][row_key]["Flow"] /
                other_table_refs["ProductSlate::volume_flow"]["Barrels of Crude per Day"]["Flow"])


def calc_transport_sum(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):

    return sum(other_table_refs["Transport Results"][key][col_key]
               for key, row in other_table_refs["Transport Results"].items() if key not in ["full_table_name", "row_index_name"])


def calc_combustion_sum(row_key, col_key, target_table_ref=None, other_table_refs=None, other_tables_keymap=None, extra=None):
    return sum(other_table_refs["Combustion Results"][key][col_key]
               for key, row in other_table_refs["Combustion Results"].items() if key not in ["full_table_name", "row_index_name"])


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

        fill_calculated_cells(target_table_ref={"Transport Results": self.transport_results, "has_wrapper": True},
                              func_to_apply=lookup_emission_factors_transport,
                              included_cols=[
                                  "Emission Factor (g CO2eq. / kgkm)"],
                              extra={"fuel_lookup": {"NG": "Natural Gas"

                                                     },
                                     "keymap": {"Pipeline Emissions": (1, "Pipeline"),
                                                "Rail Emissions": (2, "Rail Emissions"),
                                                "Heavy-Duty Truck Emissions": (3, "Heavy-Duty Truck Emissions (full load)"),
                                                "Ocean Tanker Emissions": (4, "Ocean Tanker Emissions"),
                                                "Barge Emissions": (4, "Barge Emissions")}},
                              other_table_refs={"TransportEF::TransportEmFactors": self.transport_ef.transport_emission_factors_weighted_average})

        fill_calculated_cells(target_table_ref={"Combustion Results": self.combustion_results, "has_wrapper": True},
                              func_to_apply=lookup_emission_factors_combustion,
                              included_cols=["Combustion Emission Factors"],
                              excluded_rows=[
                                  "Fuel Oil", "Residual fuels", "Liquefied Petroleum Gases (LPG)"],
                              other_table_refs={"CombustionEF::ProductEmFactorsPet": self.combustion_ef.product_combustion_emission_factors_petroleum,
                                                "CombustionEF::ProductEmFactorsSolid": self.combustion_ef.product_combustion_emission_factors_derived_solids},
                              extra={"fuel_lookup": {"Gasoline": "Motor Gasoline",
                                                     "Jet Fuel": "Kerosene-Type Jet Fuel",
                                                     "Diesel": "Distillate Fuel Oil No. 2",
                                                     "Coke": "Petroleum Coke"
                                                     }})

        fill_calculated_cells(target_table_ref={"Transport Results": self.transport_results, "has_wrapper": True},
                              func_to_apply=calc_emissions_transport,
                              included_cols=[
                                  "Transport Emissions (kg CO2eq. / bbl of crude)"],
                              other_table_refs={"TankerBargeEF::ShareOfPetProducts": self.transport_ef.tanker_barge_ef.share_of_petroleum_products})

        fill_calculated_cells(target_table_ref={"Combustion Results": self.combustion_results, "has_wrapper": True},
                              func_to_apply=calc_emissions_combustion,
                              other_table_refs={"ProductSlate::mass_flow": self.product_slate.mass_flow_kg,
                                                "ProductSlate::volume_flow": self.product_slate.volume_flow_bbl},
                              included_cols=["Total Combustion Emissions (kg CO2eq. / bbl of crude)"])

        fill_calculated_cells(target_table_ref={"Transport Sum": self.transport_sum, "has_wrapper": True},
                              func_to_apply=calc_transport_sum,
                              other_table_refs={"Transport Results": self.transport_results})

        fill_calculated_cells(target_table_ref={"Combustion Sum": self.combustion_sum, "has_wrapper": True},
                              func_to_apply=calc_combustion_sum,
                              other_table_refs={"Combustion Results": self.combustion_results})

    def results(self):
        # should move mass flow total to a higher level object. It is strangle to
        # find it only in the tanker_barge object.
        return [["Output Name", "Value"],
                ["--OPEM Transport--", ""],
                ["Sum: Kilograms of Product per Day",
                    self.transport_ef.tanker_barge_ef.share_of_petroleum_products["mass_flow_sum"]["total"]],
                ["Transport Emissions (kg CO2eq. / bbl of crude)", ""],
                ["Pipeline Emissions", self.transport_results["Pipeline Emissions"]
                    ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
                ["Rail Emissions", self.transport_results["Rail Emissions"]
                    ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
                ["Heavy-Duty Truck Emissions", self.transport_results["Heavy-Duty Truck Emissions"]
                    ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
                ["Ocean Tanker Emissions", self.transport_results["Ocean Tanker Emissions"]
                    ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
                ["Barge Emissions", self.transport_results["Barge Emissions"]
                    ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
                ["Sum", self.transport_sum["Sum"]
                    ["Transport Emissions (kg CO2eq. / bbl of crude)"]],
                ["Sum Distance Travelled", self.transport_sum["Sum"]
                    ["Select Distance Traveled (km)"]],
                ["--OPEM Combustion--", ""],
                ["Total Combustion Emissions (kg CO2eq. / bbl of crude)", ""],
                ["Gasoline", self.combustion_results["Gasoline"]
                    ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
                ["Jet Fuel", self.combustion_results["Jet Fuel"]
                    ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
                ["Diesel", self.combustion_results["Diesel"]
                    ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
                ["Fuel Oil", self.combustion_results["Fuel Oil"]
                    ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
                ["Coke", self.combustion_results["Coke"]
                    ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
                ["Residual fuels", self.combustion_results["Residual fuels"]
                    ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
                ["Liquefied Petroleum Gases (LPG)", self.combustion_results["Liquefied Petroleum Gases (LPG)"]
                 ["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]],
                ["Sum", self.combustion_sum["Sum"]["Total Combustion Emissions (kg CO2eq. / bbl of crude)"]]]

    transport_ef: TransportEF
    combustion_ef: CombustionEF
    product_slate: ProductSlate

    # will this cause problems if I try to pass in a list?
    user_input: InitVar[DefaultDict] = {}

    # User Inputs & Results sheet, table: OPEM Transport
    # USER INPUT
    # CALCULATED
    transport_results: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Transport'))

    # User Inputs & Results sheet, table: OPEM Transport
    # CALCULATED
    transport_sum: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Transport Sum'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # USER INPUT
    # CALCULATED
    combustion_results: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Combustion'))

    # User Inputs & Results sheet, table: OPEM Combustion
    # CALCULATED
    combustion_sum: DefaultDict = field(
        default_factory=lambda: build_dict_from_defaults('Combustion Sum'))

    # hold sum of product volume from product slate here
    # product_volume_sum: int = None


@dataclass
class CombustionResults:
    pass


# @dataclass
# class ResultsDto:
#     transport: TransportResults
#     combustion: CombustionResults
#     opem_total: float


# def run_model():
#     # orchestrator function
#     # will call input functions,
#     # initialize EF objects
#     # and calculate opem
#     # main should call this function when it is ready.
#     user_params = input.initialize_model_inputs(
#         input.get_csv_input, input.validate_input)
#     product_slate = input.get_product_slate('test')

#     calculate_opem()


def calculate_opem_transport(user_input):
    # -> TransportResults:
    # instantiate all transport model EF objects (using the input dto),
    # pull required params for each object out of the generic user params input
    # object by turning the input object in a dictionary and using
    # TransportObj(for key in transport_obj.properties: input_dict[key])
    # then use them to instantiate total transport EF object
    # then us the Transport EF object, the product slate, and the input dto to
    # create the results object
    return TransportEF(user_input=user_input)


# def calculate_opem() -> ResultsDto:

#     calculate_opem_transport():

#     caclulate_opem_combustion():
