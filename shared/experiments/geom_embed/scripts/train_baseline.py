#!/usr/bin/env python3
"""
Baseline training script for geometric embeddings.
Supports Euclidean, Hyperbolic (Poincaré ball), and Spherical geometries.
"""

import argparse
import yaml
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
import logging
import time
import random
import numpy as np
from datetime import datetime
from typing import List, Tuple, Dict

# Geoopt will be imported conditionally
try:
    import geoopt
    GEOOPT_AVAILABLE = True
except ImportError:
    GEOOPT_AVAILABLE = False
    print("WARNING: geoopt not installed. Install with: pip install geoopt")

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent))

try:
    from data_loader import load_dataset, CombinedDataset
    from losses import create_loss_function, GeometricLoss
    from negative_sampler import create_negative_sampler, NegativeSampler
except ImportError as e:
    print(f"WARNING: Failed to import local modules: {e}")
    print("Make sure data_loader.py, losses.py, and negative_sampler.py are in the same directory")

def setup_logging(log_dir):
    """Setup logging to file and console."""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"train_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class GeometricEmbedding(nn.Module):
    """Embedding module supporting different geometries."""
    
    def __init__(self, vocab_size, embedding_dim, geometry="euclidean", **manifold_args):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.geometry = geometry
        
        if geometry == "euclidean":
            self.embeddings = nn.Embedding(vocab_size, embedding_dim)
            nn.init.normal_(self.embeddings.weight, mean=0.0, std=0.01)
            
        elif geometry == "hyperbolic" and GEOOPT_AVAILABLE:
            # Poincaré ball model
            self.manifold = geoopt.PoincareBall(**manifold_args)
            self.embeddings = geoopt.ManifoldParameter(
                torch.randn(vocab_size, embedding_dim) * 0.01,
                manifold=self.manifold
            )
            
        elif geometry == "spherical" and GEOOPT_AVAILABLE:
            # Sphere S^(d-1)
            self.manifold = geoopt.Sphere(**manifold_args)
            self.embeddings = geoopt.ManifoldParameter(
                torch.randn(vocab_size, embedding_dim) * 0.01,
                manifold=self.manifold
            )
            
        else:
            raise ValueError(f"Unsupported geometry: {geometry} or geoopt not installed")
    
    def forward(self, indices):
        """Get embeddings for given indices."""
        if self.geometry == "euclidean":
            return self.embeddings(indices)
        else:
            # For manifold embeddings, the parameter is already on the manifold
            return self.embeddings[indices]
    
    def distance(self, u, v):
        """Compute distance between embeddings u and v."""
        if self.geometry == "euclidean":
            return torch.norm(u - v, dim=-1)
        elif self.geometry == "hyperbolic":
            return self.manifold.dist(u, v)
        elif self.geometry == "spherical":
            return self.manifold.dist(u, v)
        else:
            raise ValueError(f"Unsupported geometry: {self.geometry}")

def load_config(config_path):
    """Load experiment configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def create_training_batch(dataset: CombinedDataset, sampler: NegativeSampler, 
                          batch_size: int, device: torch.device):
    """Create a batch of training examples."""
    triplets = dataset.get_relation_triplets()
    if not triplets:
        return None, None, None, None
    
    # Sample random triplets
    if len(triplets) > batch_size:
        batch_indices = random.sample(range(len(triplets)), batch_size)
    else:
        batch_indices = list(range(len(triplets)))
    
    anchors, positives, relations = [], [], []
    for idx in batch_indices:
        anchor_idx, positive_idx, rel = triplets[idx]
        anchors.append(anchor_idx)
        positives.append(positive_idx)
        relations.append(rel)
    
    # Sample negatives
    anchor_words = [dataset.get_word(idx) for idx in anchors]
    positive_words = [dataset.get_word(idx) for idx in positives]
    negative_words_list = sampler.sample_batch(anchor_words, positive_words, relations)
    
    # Convert to tensors
    anchor_tensor = torch.tensor(anchors, dtype=torch.long, device=device)
    positive_tensor = torch.tensor(positives, dtype=torch.long, device=device)
    
    # For each anchor, we'll use one negative (first from the list)
    negatives = [negs[0] for negs in negative_words_list]
    negative_idxs = [dataset.get_word_index(neg) for neg in negatives]
    negative_tensor = torch.tensor(negative_idxs, dtype=torch.long, device=device)
    
    return anchor_tensor, positive_tensor, negative_tensor, relations

def evaluate_model(model: GeometricEmbedding, dataset: CombinedDataset, 
                   device: torch.device, logger: logging.Logger):
    """Simple evaluation: compute average distance for positive vs negative pairs."""
    model.eval()
    triplets = dataset.get_relation_triplets()
    
    if not triplets:
        return 0.0, 0.0
    
    # Sample some pairs for evaluation
    eval_size = min(100, len(triplets))
    eval_indices = random.sample(range(len(triplets)), eval_size)
    
    pos_distances, neg_distances = [], []
    
    with torch.no_grad():
        for idx in eval_indices:
            anchor_idx, positive_idx, rel = triplets[idx]
            
            # Get embeddings
            anchor_emb = model(torch.tensor([anchor_idx], device=device))
            positive_emb = model(torch.tensor([positive_idx], device=device))
            
            # Positive distance
            pos_dist = model.distance(anchor_emb, positive_emb).item()
            pos_distances.append(pos_dist)
            
            # Sample a random negative
            negative_candidates = [i for i in range(dataset.get_vocab_size()) 
                                  if i != anchor_idx and i != positive_idx]
            if negative_candidates:
                neg_idx = random.choice(negative_candidates)
                negative_emb = model(torch.tensor([neg_idx], device=device))
                neg_dist = model.distance(anchor_emb, negative_emb).item()
                neg_distances.append(neg_dist)
    
    model.train()
    
    if pos_distances and neg_distances:
        avg_pos = np.mean(pos_distances)
        avg_neg = np.mean(neg_distances)
        logger.info(f"Evaluation: avg positive distance = {avg_pos:.4f}, avg negative distance = {avg_neg:.4f}")
        return avg_pos, avg_neg
    else:
        return 0.0, 0.0

def main():
    parser = argparse.ArgumentParser(description="Train geometric embeddings")
    parser.add_argument("--config", type=str, required=True,
                       help="Path to configuration YAML file")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu",
                       help="Device to use (cuda or cpu)")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    device = torch.device(args.device)
    
    # Setup logging
    logger = setup_logging(config['logging']['log_dir'])
    logger.info(f"Starting experiment: {config['experiment']['name']}")
    logger.info(f"Configuration: {config}")
    logger.info(f"Using device: {device}")
    
    # Load dataset
    logger.info("Loading datasets...")
    dataset = load_dataset(config)
    if dataset is None:
        logger.error("Failed to load dataset")
        return
    
    vocab_size = dataset.get_vocab_size()
    logger.info(f"Dataset loaded: {vocab_size} words, {len(dataset.all_relations)} relations")
    
    # Update vocab size in config for model initialization
    config['data']['vocab_size'] = vocab_size
    
    # Initialize model
    model = GeometricEmbedding(
        vocab_size=vocab_size,
        embedding_dim=config['model']['embedding_dim'],
        geometry=config['model']['geometry'],
        **config['model'].get('manifold_args', {})
    ).to(device)
    
    # Create loss function and negative sampler
    loss_fn = create_loss_function(config)
    loss_fn = loss_fn.to(device)
    
    negative_sampler = create_negative_sampler(
        config, 
        dataset.get_vocab(), 
        dataset.word_to_idx
    )
    
    # Optimizer
    if config['training']['optimizer'] == "adam":
        optimizer = optim.Adam(model.parameters(), lr=config['training']['learning_rate'])
    else:
        optimizer = optim.SGD(model.parameters(), lr=config['training']['learning_rate'])
    
    # Training loop
    logger.info("Starting training...")
    start_time = time.time()
    
    batch_size = config['training']['batch_size']
    num_epochs = config['training']['num_epochs']
    
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        num_batches = 0
        
        # Create training batch
        anchor_idx, positive_idx, negative_idx, relations = create_training_batch(
            dataset, negative_sampler, batch_size, device
        )
        
        if anchor_idx is not None:
            # Forward pass
            anchor_emb = model(anchor_idx)
            positive_emb = model(positive_idx)
            negative_emb = model(negative_idx)
            
            # Compute loss
            loss = loss_fn(anchor_emb, positive_emb, negative_emb)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss = loss.item()
            num_batches = 1
        
        # Logging
        if (epoch + 1) % config['logging'].get('checkpoint_frequency', 10) == 0:
            logger.info(f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss:.4f}")
        
        # Evaluation
        if (epoch + 1) % config['evaluation']['eval_frequency'] == 0:
            avg_pos, avg_neg = evaluate_model(model, dataset, device, logger)
            diff_ratio = (avg_neg - avg_pos) / max(avg_pos, 1e-8)
            logger.info(f"Distance ratio (neg/pos): {diff_ratio:.2f}")
    
    total_time = time.time() - start_time
    logger.info(f"Training completed in {total_time:.2f} seconds")
    
    # Save final model
    save_path = Path(config['logging']['log_dir']) / "final_model.pt"
    torch.save({
        'model_state_dict': model.state_dict(),
        'config': config,
        'vocab': dataset.get_vocab(),
        'word_to_idx': dataset.word_to_idx
    }, save_path)
    logger.info(f"Model saved to {save_path}")
    
    # Save embeddings for visualization
    embeddings_path = Path(config['logging']['log_dir']) / "embeddings.npy"
    with torch.no_grad():
        all_indices = torch.arange(vocab_size, device=device)
        all_embeddings = model(all_indices).cpu().numpy()
        np.save(embeddings_path, all_embeddings)
    
    logger.info(f"Embeddings saved to {embeddings_path}")

if __name__ == "__main__":
    main()