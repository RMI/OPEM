from opem import input


def main():
    """Entry point for the application script"""
    print("Get started with OPEM model")
    run_model()
    user_params_and_slate = input.initialize_model_inputs(
        input.get_csv_input, input.validate_input)
