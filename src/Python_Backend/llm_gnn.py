
import torch
import json
from LLM2 import generate_response
from GNN.data_process import open_helper
from inference import run_inference

"""
Before running, in an independent terminal, run combine_LLM_adapter.py 
"""


def LLM_GNN():
    data_base = "/home/ai/Documents/LLM_GNN_compal/GNN_data/"
    reset_hist = {
        "current_action": "",
        "previous_actions": []
    }
    with open(f"{data_base}history/runs.json", "w") as hist_in:
        json.dump(reset_hist, hist_in)

    human_instruction = input("Give task: ", )

    #TODO:
    # LLM GOES HERE
    decomposed = generate_response(human_instruction,1)
    decomposed = decomposed.replace("(","")
    decomposed = decomposed.replace(")","")
    ###############


    # decomposed = human_instruction #TODO: UPDATE WITH LLM RESPONSE, THIS IS FOR TESTING ONLY
    goal, target_wire, target_terminal = decomposed.split("-")
    instruction_dict = {
        "prompt": human_instruction,
        "llm_decomposed": decomposed,
        "to_gnn":{"goal": goal, "target_wire": target_wire, "target_terminal": target_terminal}
    }

    with open(f"{data_base}llm/current_instruction.json", "w") as update_llm:
        json.dump(instruction_dict, update_llm)

    # Load data
    hist = open_helper(f"{data_base}history/runs.json")
    environment = open_helper(f"{data_base}vision/current_env.json")
    instruction = open_helper(f"{data_base}llm/current_instruction.json")

    # Run GNN for action-object pair prediction
    wire_id, action = run_inference(environment, instruction["to_gnn"])

    return wire_id, action

###### TESTING ###########
wire_id, action = LLM_GNN()

print(wire_id, action)
device_index = torch.cuda.current_device()
print(torch.cuda.get_device_name(device_index))



