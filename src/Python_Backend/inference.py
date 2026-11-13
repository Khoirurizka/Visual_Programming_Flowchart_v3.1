import torch
import GNN
import config_GNN
from torch_geometric.data import Data
import networkx as nx
import json

def run_inference(vision_data, llm_data):
    # Load model 
    device = config_GNN.DEVICE
    possible_actions = config_GNN.ACTION_PRIMS

    # Create graph
    graph = GNN.graph.InferenceTaskGraphHeterogeneous(possible_actions, vision_data, llm_data)
    
    wire_encodings, terminal_encodings = graph.get_node_features()
    x = torch.cat([wire_encodings, terminal_encodings.unsqueeze(0)])

    edge_index = graph.get_edge_index()
    edge_attr = graph.get_edge_attr()
    wire_mask, terminal_mask = graph.get_node_masks()     
    wire_map = graph.get_wire_mappings()

    data = Data(x=x,
                edge_index=edge_index,
                edge_attr=edge_attr,
                wire_mask=wire_mask,
                terminal_mask=terminal_mask,
                )
    data.to(device)

    model_params = torch.load(config_GNN.MODEL_PARAMS_PATH, map_location=device)
    model = GNN.models.TwoHeadGATSmall(
        in_dim=data.x.shape[1],
        edge_feat_dim=2,
        hidden_dim=config_GNN.HIDDEN_DIM,
        num_actions=len(possible_actions),      
    )

    with torch.no_grad():
        model.load_state_dict(model_params)
        model.to(device)
        model.eval()

        wire_logits, action_logits = model(
            data.x.float(), wire_mask, data.edge_index, data.edge_attr, data.batch
        )

        predicted_wire_local = wire_logits.argmax(dim=0).cpu().numpy().tolist()
        predicted_wire_global = wire_map[predicted_wire_local]['global_id']
        predicted_action = action_logits.argmax(dim=1).cpu().numpy().tolist()

        predicted_action_name = possible_actions[predicted_action[0]]
    
    return predicted_wire_global, predicted_action_name