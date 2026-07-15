#!/usr/bin/env python3
"""
Negative sampling for geometric embeddings.
"""

import random
import numpy as np
from typing import List, Tuple, Dict
import torch

class NegativeSampler:
    """Base class for negative sampling."""
    
    def __init__(self, vocab: List[str], word_to_idx: Dict[str, int], num_negatives: int = 10):
        self.vocab = vocab
        self.word_to_idx = word_to_idx
        self.idx_to_word = {idx: word for word, idx in word_to_idx.items()}
        self.vocab_size = len(vocab)
        self.num_negatives = num_negatives
        
    def sample(self, anchor_word: str, positive_word: str, relation_type: str) -> List[str]:
        """Sample negative examples for a given (anchor, positive) pair."""
        raise NotImplementedError
        
    def sample_batch(self, anchors: List[str], positives: List[str], relation_types: List[str]) -> List[List[str]]:
        """Sample negative examples for a batch."""
        negatives = []
        for anchor, positive, rel in zip(anchors, positives, relation_types):
            negs = self.sample(anchor, positive, rel)
            negatives.append(negs)
        return negatives

class UniformNegativeSampler(NegativeSampler):
    """Uniform random negative sampling."""
    
    def sample(self, anchor_word: str, positive_word: str, relation_type: str) -> List[str]:
        """Sample uniformly from vocabulary, excluding anchor and positive."""
        candidates = [w for w in self.vocab if w != anchor_word and w != positive_word]
        
        if len(candidates) < self.num_negatives:
            # If not enough candidates, allow repeats
            negs = random.choices(candidates, k=self.num_negatives)
        else:
            negs = random.sample(candidates, self.num_negatives)
            
        return negs

class FrequencyNegativeSampler(NegativeSampler):
    """Negative sampling weighted by word frequency."""
    
    def __init__(self, vocab: List[str], word_to_idx: Dict[str, int], 
                 word_frequencies: Dict[str, float], num_negatives: int = 10):
        super().__init__(vocab, word_to_idx, num_negatives)
        self.word_frequencies = word_frequencies
        
        # Create probability distribution
        freqs = np.array([word_frequencies.get(word, 1.0) for word in vocab])
        self.probs = freqs / freqs.sum()
        
    def sample(self, anchor_word: str, positive_word: str, relation_type: str) -> List[str]:
        """Sample negatives weighted by frequency."""
        # Get indices excluding anchor and positive
        exclude_indices = set()
        if anchor_word in self.word_to_idx:
            exclude_indices.add(self.word_to_idx[anchor_word])
        if positive_word in self.word_to_idx:
            exclude_indices.add(self.word_to_idx[positive_word])
            
        # Create filtered probabilities
        mask = np.ones(len(self.vocab), dtype=bool)
        if exclude_indices:
            mask[list(exclude_indices)] = False
            
        if not mask.any():
            # Fallback to uniform if all words are excluded
            candidates = [w for w in self.vocab if w != anchor_word and w != positive_word]
            return random.choices(candidates, k=self.num_negatives) if candidates else []
            
        filtered_vocab = np.array(self.vocab)[mask]
        filtered_probs = self.probs[mask]
        filtered_probs = filtered_probs / filtered_probs.sum()
        
        # Sample without replacement
        if len(filtered_vocab) >= self.num_negatives:
            indices = np.random.choice(len(filtered_vocab), self.num_negatives, replace=False, p=filtered_probs)
            negs = filtered_vocab[indices].tolist()
        else:
            # Sample with replacement if not enough candidates
            indices = np.random.choice(len(filtered_vocab), self.num_negatives, replace=True, p=filtered_probs)
            negs = filtered_vocab[indices].tolist()
            
        return negs

class RelationAwareNegativeSampler(NegativeSampler):
    """Negative sampling that considers relation types."""
    
    def __init__(self, vocab: List[str], word_to_idx: Dict[str, int], 
                 relation_groups: Dict[str, List[str]], num_negatives: int = 10):
        """
        Args:
            relation_groups: Mapping from relation type to list of words that appear in that relation
        """
        super().__init__(vocab, word_to_idx, num_negatives)
        self.relation_groups = relation_groups
        
    def sample(self, anchor_word: str, positive_word: str, relation_type: str) -> List[str]:
        """Sample negatives that are unlikely to have the given relation."""
        # Get words that commonly appear in this relation type
        related_words = set(self.relation_groups.get(relation_type, []))
        
        # Prefer words not commonly related through this relation
        candidates = []
        for word in self.vocab:
            if word == anchor_word or word == positive_word:
                continue
            if word not in related_words:
                candidates.append(word)
                
        if len(candidates) < self.num_negatives:
            # Fallback to all words if not enough candidates
            candidates = [w for w in self.vocab if w != anchor_word and w != positive_word]
            
        if len(candidates) >= self.num_negatives:
            negs = random.sample(candidates, self.num_negatives)
        else:
            negs = random.choices(candidates, k=self.num_negatives)
            
        return negs

def create_negative_sampler(config: Dict, vocab: List[str], word_to_idx: Dict[str, int]) -> NegativeSampler:
    """Create negative sampler based on configuration."""
    sampler_type = config.get('training', {}).get('negative_sampler', 'uniform')
    num_negatives = config.get('training', {}).get('negative_samples', 10)
    
    if sampler_type == 'uniform':
        return UniformNegativeSampler(vocab, word_to_idx, num_negatives)
    elif sampler_type == 'frequency':
        # For frequency sampler, we need word frequencies
        # For now, use uniform frequencies
        word_frequencies = {word: 1.0 for word in vocab}
        return FrequencyNegativeSampler(vocab, word_to_idx, word_frequencies, num_negatives)
    elif sampler_type == 'relation_aware':
        # For relation-aware sampler, we need relation groups
        # For now, use empty groups
        relation_groups = {}
        return RelationAwareNegativeSampler(vocab, word_to_idx, relation_groups, num_negatives)
    else:
        raise ValueError(f"Unknown sampler type: {sampler_type}")

if __name__ == "__main__":
    # Test negative samplers
    vocab = ["cat", "dog", "animal", "car", "tree", "flower", "house", "computer", "book", "water"]
    word_to_idx = {word: idx for idx, word in enumerate(vocab)}
    
    print("Testing negative samplers...")
    print(f"Vocabulary: {vocab}")
    
    # Uniform sampler
    uniform_sampler = UniformNegativeSampler(vocab, word_to_idx, num_negatives=3)
    negs = uniform_sampler.sample("cat", "animal", "hypernym")
    print(f"Uniform sampler (cat-animal): {negs}")
    
    # Frequency sampler (uniform frequencies)
    freqs = {word: 1.0 for word in vocab}
    freq_sampler = FrequencyNegativeSampler(vocab, word_to_idx, freqs, num_negatives=3)
    negs = freq_sampler.sample("cat", "animal", "hypernym")
    print(f"Frequency sampler (cat-animal): {negs}")