
from opem.core import run_model
from opem.input.user_input import standardize_input
from opem.utils import write_csv_output
from opem import input

def main():
    """Entry point for the application script"""
    print("Welcome to OPEM V.1.2")


    user_input = input.initialize_model_inputs(
        input.get_csv_input, input.validate_input)


    script_input = {"user_input": [["User Inputs & Results", 
                        "Global:", 
                        "Assay (Select Oil)", 
                        "-", 
                        "Canada Athabasca DC SCO"]]
        }
    



    print("Found opem_input.csv, running model.")

    results = run_model(script_input, return_dict=False)
     
 
    print(results)

    


if __name__ == "__main__":
    main()
