from dataclasses import asdict
from opem.core import calculate_opem_transport
from opem import input
from opem.utils import initialize_from_list, nested_access, visit_dict, initialize_from_dataclass
import os


def main():
    """Entry point for the application script"""
    print("Get started with OPEM model")
    # run_model()
    user_params = input.initialize_model_inputs(
        input.get_csv_input, input.validate_input)
    transport_results = calculate_opem_transport(asdict(user_params))
    product_slate = input.get_product_slate(user_params.product_name)