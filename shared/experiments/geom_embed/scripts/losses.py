#!/usr/bin/env python3
"""
Loss functions for geometric embeddings.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Optional, Dict

class ContrastiveLoss(nn.Module):
    """Contrastive loss for semantic relations."""
    
    def __init__(self, margin: float = 1.0, distance_fn=None):
        super().__init__()
        self.margin = margin
        self.distance_fn = distance_fn if distance_fn is not None else self.euclidean_distance
        
    @staticmethod
    def euclidean_distance(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Euclidean distance."""
        return torch.norm(x - y, dim=-1)
    
    def forward(self, anchor: torch.Tensor, positive: torch.Tensor, negative: torch.Tensor) -> torch.Tensor:
        """
        Compute contrastive loss.
        
        Args:
            anchor: Anchor embeddings [batch_size, embedding_dim]
            positive: Positive (related) embeddings [batch_size, embedding_dim]
            negative: Negative (unrelated) embeddings [batch_size, embedding_dim]
            
        Returns:
            Loss value
        """
        pos_dist = self.distance_fn(anchor, positive)
        neg_dist = self.distance_fn(anchor, negative)
        
        # Contrastive loss: maximize pos_dist - neg_dist with margin
        losses = F.relu(pos_dist - neg_dist + self.margin)
        return losses.mean()

class MarginRankingLoss(nn.Module):
    """Margin ranking loss for relational learning."""
    
    def __init__(self, margin: float = 1.0, distance_fn=None):
        super().__init__()
        self.margin = margin
        self.distance_fn = distance_fn if distance_fn is not None else self.euclidean_distance
        
    @staticmethod
    def euclidean_distance(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Euclidean distance."""
        return torch.norm(x - y, dim=-1)
    
    def forward(self, anchor: torch.Tensor, positive: torch.Tensor, negative: torch.Tensor) -> torch.Tensor:
        """
        Compute margin ranking loss.
        
        Args:
            anchor: Anchor embeddings
            positive: Positive (related) embeddings
            negative: Negative (unrelated) embeddings
            
        Returns:
            Loss value
        """
        pos_dist = self.distance_fn(anchor, positive)
        neg_dist = self.distance_fn(anchor, negative)
        
        # Margin ranking loss: positive should be closer than negative by margin
        return F.margin_ranking_loss(
            -pos_dist, -neg_dist,  # Negative distances because we want smaller distance for positive
            torch.ones_like(pos_dist),
            margin=self.margin,
            reduction='mean'
        )

class GeometricLoss(nn.Module):
    """Loss function that adapts to geometry of embeddings."""
    
    def __init__(self, geometry: str = "euclidean", margin: float = 1.0):
        super().__init__()
        self.geometry = geometry
        self.margin = margin
        
        if geometry == "euclidean":
            self.distance_fn = self.euclidean_distance
        elif geometry == "hyperbolic":
            self.distance_fn = self.hyperbolic_distance
        elif geometry == "spherical":
            self.distance_fn = self.spherical_distance
        else:
            raise ValueError(f"Unsupported geometry: {geometry}")
    
    @staticmethod
    def euclidean_distance(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        return torch.norm(x - y, dim=-1)
    
    @staticmethod
    def hyperbolic_distance(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Poincaré ball distance (simplified)."""
        # Simplified version - actual hyperbolic distance is more complex
        # For now, use Euclidean as placeholder
        return torch.norm(x - y, dim=-1)
    
    @staticmethod
    def spherical_distance(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Spherical distance (simplified)."""
        # Cosine distance on unit sphere
        cos_sim = F.cosine_similarity(x, y, dim=-1)
        # Convert to angular distance
        return torch.acos(torch.clamp(cos_sim, -1.0, 1.0))
    
    def forward(self, anchor: torch.Tensor, positive: torch.Tensor, negative: torch.Tensor) -> torch.Tensor:
        """Compute geometric-aware loss."""
        pos_dist = self.distance_fn(anchor, positive)
        neg_dist = self.distance_fn(anchor, negative)
        
        # Margin loss
        loss = F.relu(pos_dist - neg_dist + self.margin)
        return loss.mean()

class MultiRelationLoss(nn.Module):
    """Loss for multiple relation types."""
    
    def __init__(self, relation_types: List[str], margin: float = 1.0, geometry: str = "euclidean"):
        super().__init__()
        self.relation_types = relation_types
        self.losses = nn.ModuleDict({
            rel: GeometricLoss(geometry=geometry, margin=margin)
            for rel in relation_types
        })
        
    def forward(self, 
                anchor: torch.Tensor, 
                positive: torch.Tensor, 
                negative: torch.Tensor,
                relation_types: List[str]) -> torch.Tensor:
        """
        Compute loss for multiple relation types.
        
        Args:
            anchor: Anchor embeddings [batch_size, embedding_dim]
            positive: Positive embeddings [batch_size, embedding_dim]
            negative: Negative embeddings [batch_size, embedding_dim]
            relation_types: List of relation types for each pair [batch_size]
            
        Returns:
            Weighted loss value
        """
        batch_size = anchor.size(0)
        total_loss = 0.0
        counts = {rel: 0 for rel in self.relation_types}
        
        for i in range(batch_size):
            rel = relation_types[i]
            if rel in self.losses:
                loss = self.losses[rel](
                    anchor[i].unsqueeze(0),
                    positive[i].unsqueeze(0),
                    negative[i].unsqueeze(0)
                )
                total_loss += loss
                counts[rel] += 1
        
        # Average by total batch size
        if batch_size > 0:
            return total_loss / batch_size
        else:
            return torch.tensor(0.0, device=anchor.device)

def create_loss_function(config: Dict) -> nn.Module:
    """Create loss function based on configuration."""
    loss_type = config.get('training', {}).get('loss', 'contrastive')
    margin = config.get('training', {}).get('margin', 1.0)
    geometry = config.get('model', {}).get('geometry', 'euclidean')
    
    if loss_type == 'contrastive':
        return ContrastiveLoss(margin=margin)
    elif loss_type == 'margin_ranking':
        return MarginRankingLoss(margin=margin)
    elif loss_type == 'geometric':
        return GeometricLoss(geometry=geometry, margin=margin)
    else:
        raise ValueError(f"Unknown loss type: {loss_type}")

if __name__ == "__main__":
    # Test loss functions
    batch_size = 4
    embedding_dim = 10
    
    anchor = torch.randn(batch_size, embedding_dim)
    positive = torch.randn(batch_size, embedding_dim)
    negative = torch.randn(batch_size, embedding_dim)
    
    # Test different losses
    contrastive_loss = ContrastiveLoss(margin=1.0)
    margin_loss = MarginRankingLoss(margin=1.0)
    geometric_loss = GeometricLoss(geometry="euclidean", margin=1.0)
    
    print(f"Contrastive loss: {contrastive_loss(anchor, positive, negative):.4f}")
    print(f"Margin ranking loss: {margin_loss(anchor, positive, negative):.4f}")
    print(f"Geometric loss: {geometric_loss(anchor, positive, negative):.4f}")