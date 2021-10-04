
from opem.core import run_model
from opem.utils import write_csv_output
from opem import input

def main():
    """Entry point for the application script"""
    print("Welcome to OPEM V.1.2")

    user_input = input.initialize_model_inputs(
        input.get_csv_input, input.validate_input)

    print("Found opem_input.csv, running model.")

    results = run_model(user_input)
     
    print("Writing results . . .")
 
    write_csv_output(results)

    


if __name__ == "__main__":
    main()
