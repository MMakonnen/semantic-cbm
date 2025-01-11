import torch
from torch import nn
import os

from config import config
from concept_corrector_models import BaselineConceptCorrector, LSTMConceptCorrector, MultiLSTMConceptCorrector
from train import train_model
from eval import evaluate_baseline
from data_loader import load_data, create_splits, create_dataloaders, CustomDataset

# =========================
# Main Function
# =========================
def main():
    device = config['device']
    print(f"Using device: {device}")
    predicted_concepts, groundtruth_concepts, concept_to_cluster = load_data(config)
    train_split, val_split = create_splits(config)

    # Create dataloaders
    train_loader, val_loader = create_dataloaders(
        predicted_concepts, groundtruth_concepts, train_split, val_split, config['batch_size']
    )
    model_type = config['model']
    print(f"Selected model type: {model_type}")
    
    # Initialize the appropriate Concept Corrector model
    if model_type == 'MultiLSTM':
        ConceptCorrectorClass = MultiLSTMConceptCorrector
        concept_corrector = ConceptCorrectorClass(
            input_size=config['input_size'],
            hidden_size=config['hidden_size'],
            num_layers=config['num_layers'],
            output_size=config['output_size'],
            m_clusters=config['data_generation']['m'],
            concept_to_cluster=concept_to_cluster,
            input_format=config['input_format']
        ).to(device)
    elif model_type == 'LSTM':
        ConceptCorrectorClass = LSTMConceptCorrector
        concept_corrector = ConceptCorrectorClass(
            input_size=config['input_size'],
            hidden_size=config['hidden_size'],
            num_layers=config['num_layers'],
            output_size=config['output_size'],
            input_format=config['input_format']
        ).to(device)
    elif model_type == 'Baseline':
        ConceptCorrectorClass = BaselineConceptCorrector
        concept_corrector = ConceptCorrectorClass(
            input_size=config['input_size'],
            output_size=config['output_size'],
            input_format=config['input_format']
        ).to(device)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    print(f"{model_type} model initialized.")
    
    # Initialize model weights
    for name, param in concept_corrector.named_parameters():
        if 'weight' in name and param.ndimension() >= 2:
            nn.init.xavier_uniform_(param)
        elif 'bias' in name:
            nn.init.constant_(param, 0.0)
    print("Model weights initialized.")
    
    # Load adapter if provided
    adapter = None
    if config['adapter_path'] is not None:
        if os.path.exists(config['adapter_path']):
            adapter = torch.load(config['adapter_path']).to(device)
            print(f"Using adapter from: {config['adapter_path']}")
        else:
            raise FileNotFoundError(f"Adapter path {config['adapter_path']} does not exist.")
    else:
        print("No adapter path provided. Skipping adapter loading.")
    
    # Train the model if not Baseline
    if config['model'] != 'Baseline':
        train_model(concept_corrector, train_loader, val_loader, device, config, concept_to_cluster, adapter)
    else:
        # For Baseline model, perform intervention and print replacements based on verbose flag
        print("\nBaseline Model Evaluation with Interventions:")
        verbose = config['verbose']
        # Evaluate on Training Data
        print("Intervening on Training Data:")
        evaluate_baseline(concept_corrector, train_loader, device, config, concept_to_cluster, adapter, phase='Training', verbose=verbose)
        # Evaluate on Validation Data
        print("Intervening on Validation Data:")
        evaluate_baseline(concept_corrector, val_loader, device, config, concept_to_cluster, adapter, phase='Validation', verbose=verbose)
        print("Baseline model evaluation completed.")

if __name__ == '__main__':
    main()