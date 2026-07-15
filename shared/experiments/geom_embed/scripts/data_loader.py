#!/usr/bin/env python3
"""
Data loader for geometric embeddings experiments.
Supports WordNet (hierarchy), BATS (analogy), and SimLex-999 (similarity).
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SemanticDataset:
    """Base class for semantic datasets."""
    
    def __init__(self, name: str, data_dir: Path):
        self.name = name
        self.data_dir = data_dir
        self.vocab = set()
        self.relations = []
        
    def load(self) -> bool:
        """Load dataset from disk."""
        raise NotImplementedError
        
    def get_word_pairs(self, relation_type: Optional[str] = None) -> List[Tuple[str, str, str]]:
        """Get word pairs (word1, word2, relation_type)."""
        if relation_type is None:
            return self.relations
        return [(w1, w2, rel) for w1, w2, rel in self.relations if rel == relation_type]
    
    def get_vocab(self) -> List[str]:
        """Get vocabulary list."""
        return list(self.vocab)
    
    def vocab_size(self) -> int:
        return len(self.vocab)

class WordNetDataset(SemanticDataset):
    """WordNet hierarchical relations."""
    
    def load(self) -> bool:
        try:
            # For now, use a small sample
            # In production, load from actual WordNet files
            sample_relations = [
                # hypernym/hyponym relations
                ("cat", "animal", "hypernym"),
                ("dog", "animal", "hypernym"),
                ("rose", "flower", "hypernym"),
                ("oak", "tree", "hypernym"),
                # meronym/holonym relations
                ("wheel", "car", "part_of"),
                ("engine", "car", "part_of"),
                # etc.
            ]
            
            self.relations = sample_relations
            for w1, w2, _ in sample_relations:
                self.vocab.add(w1)
                self.vocab.add(w2)
                
            logger.info(f"Loaded WordNet dataset with {len(self.relations)} relations, {len(self.vocab)} unique words")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load WordNet dataset: {e}")
            return False

class BATSDataset(SemanticDataset):
    """BATS (Bigger Analogy Test Set)."""
    
    def load(self) -> bool:
        try:
            # BATS categories: inflectional morphology, derivational morphology, 
            # lexicographic semantics, encyclopedic semantics
            sample_analogies = [
                # Inflectional morphology
                ("walk", "walked", "past_tense"),
                ("run", "ran", "past_tense"),
                # Derivational morphology
                ("happy", "happiness", "noun_form"),
                ("sad", "sadness", "noun_form"),
                # Lexicographic semantics
                ("dog", "puppy", "young"),
                ("cat", "kitten", "young"),
                # Encyclopedic semantics
                ("France", "Paris", "capital"),
                ("Germany", "Berlin", "capital"),
            ]
            
            self.relations = [(w1, w2, f"analogy:{rel}") for w1, w2, rel in sample_analogies]
            for w1, w2, _ in sample_analogies:
                self.vocab.add(w1)
                self.vocab.add(w2)
                
            logger.info(f"Loaded BATS dataset with {len(self.relations)} analogies, {len(self.vocab)} unique words")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load BATS dataset: {e}")
            return False

class SimLexDataset(SemanticDataset):
    """SimLex-999 similarity dataset."""
    
    def load(self) -> bool:
        try:
            # SimLex-999 provides word pairs with similarity scores (0-10)
            sample_similarities = [
                ("cat", "dog", 8.5),
                ("car", "automobile", 9.2),
                ("happy", "joyful", 8.7),
                ("big", "large", 9.1),
                ("computer", "keyboard", 3.2),
            ]
            
            self.relations = [(w1, w2, f"similarity:{score}") for w1, w2, score in sample_similarities]
            for w1, w2, _ in sample_similarities:
                self.vocab.add(w1)
                self.vocab.add(w2)
                
            logger.info(f"Loaded SimLex dataset with {len(self.relations)} similarity pairs, {len(self.vocab)} unique words")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load SimLex dataset: {e}")
            return False

class CombinedDataset:
    """Combine multiple semantic datasets."""
    
    def __init__(self, datasets: List[SemanticDataset]):
        self.datasets = datasets
        self.vocab = set()
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.all_relations = []
        
    def load_all(self) -> bool:
        """Load all datasets."""
        success = all(dataset.load() for dataset in self.datasets)
        if not success:
            return False
            
        # Combine vocab
        for dataset in self.datasets:
            self.vocab.update(dataset.get_vocab())
            self.all_relations.extend(dataset.relations)
            
        # Create word to index mapping
        self.word_to_idx = {word: idx for idx, word in enumerate(sorted(self.vocab))}
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}
        
        logger.info(f"Combined dataset: {len(self.vocab)} unique words, {len(self.all_relations)} total relations")
        return True
    
    def get_relation_triplets(self) -> List[Tuple[int, int, str]]:
        """Get relations as (idx1, idx2, relation_type) triplets."""
        triplets = []
        for w1, w2, rel in self.all_relations:
            idx1 = self.word_to_idx.get(w1)
            idx2 = self.word_to_idx.get(w2)
            if idx1 is not None and idx2 is not None:
                triplets.append((idx1, idx2, rel))
        return triplets
    
    def get_vocab_size(self) -> int:
        return len(self.vocab)
    
    def get_word_index(self, word: str) -> Optional[int]:
        return self.word_to_idx.get(word)
    
    def get_word(self, idx: int) -> Optional[str]:
        return self.idx_to_word.get(idx)
    
    def get_vocab(self) -> List[str]:
        """Get vocabulary as list."""
        return list(self.vocab)

def load_dataset(config: Dict) -> Optional[CombinedDataset]:
    """Load dataset based on configuration."""
    data_dir = Path(config.get('data', {}).get('path', 'data/'))
    datasets_to_load = config.get('data', {}).get('datasets', ['wordnet', 'bats', 'simlex'])
    
    datasets = []
    
    if 'wordnet' in datasets_to_load:
        datasets.append(WordNetDataset('WordNet', data_dir / 'wordnet'))
    
    if 'bats' in datasets_to_load:
        datasets.append(BATSDataset('BATS', data_dir / 'bats'))
    
    if 'simlex' in datasets_to_load:
        datasets.append(SimLexDataset('SimLex', data_dir / 'simlex'))
    
    combined = CombinedDataset(datasets)
    if combined.load_all():
        return combined
    else:
        logger.error("Failed to load one or more datasets")
        return None

if __name__ == "__main__":
    # Test the data loader
    import logging
    logging.basicConfig(level=logging.INFO)
    
    test_config = {
        'data': {
            'path': 'data/',
            'datasets': ['wordnet', 'bats', 'simlex']
        }
    }
    
    dataset = load_dataset(test_config)
    if dataset:
        print(f"Vocabulary size: {dataset.get_vocab_size()}")
        print(f"Number of relations: {len(dataset.all_relations)}")
        print("Sample relations:", dataset.all_relations[:5])