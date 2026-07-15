#!/usr/bin/env python3
"""
FastAPI server for geometric embeddings visualization.
Provides API for embeddings, fibers, and experiment results.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
from pathlib import Path
import numpy as np
import yaml

app = FastAPI(
    title="Geometric Embeddings API",
    description="API for geometric embeddings and fiber bundle visualization",
    version="0.1.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to actual frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class EmbeddingRequest(BaseModel):
    geometry: str = "euclidean"
    dimension: int = 300

class FiberRequest(BaseModel):
    word: str
    geometry: str = "euclidean"
    max_variants: int = 10

class ExperimentRequest(BaseModel):
    config: Dict
    name: str

# Mock data path
MOCK_DATA_PATH = Path(__file__).parent.parent / "data" / "mock_fiber_data.json"

# Load mock data
def load_mock_data():
    with open(MOCK_DATA_PATH, 'r') as f:
        return json.load(f)

mock_data = load_mock_data()

@app.get("/")
async def root():
    return {
        "message": "Geometric Embeddings API",
        "version": "0.1.0",
        "endpoints": {
            "/api/embeddings": "Get all embeddings",
            "/api/fiber/{word}": "Get fiber for a word",
            "/api/experiments": "List experiments",
            "/api/health": "Health check"
        }
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2026-03-30T23:58:00Z"}

@app.get("/api/embeddings")
async def get_embeddings(geometry: str = "euclidean", dim: int = 300):
    """
    Get embeddings for all words.
    
    Args:
        geometry: euclidean, hyperbolic, or spherical
        dim: embedding dimension
        
    Returns:
        List of embeddings with metadata
    """
    # For now, return mock data
    words = []
    for word_data in mock_data["words"]:
        words.append({
            "id": word_data["id"],
            "embedding": word_data["base_embedding"],
            "geometry": geometry,
            "dimension": dim
        })
    
    return {
        "geometry": geometry,
        "dimension": dim,
        "count": len(words),
        "embeddings": words
    }

@app.get("/api/fiber/{word}")
async def get_fiber(word: str, geometry: str = "euclidean", max_variants: int = 10):
    """
    Get fiber (nearby variants) for a specific word.
    
    Args:
        word: The word to get fiber for
        geometry: Geometry type
        max_variants: Maximum number of variants to return
        
    Returns:
        Fiber data including variants and distances
    """
    # Find the word in mock data
    for word_data in mock_data["words"]:
        if word_data["id"] == word:
            fiber_data = word_data["fiber"]
            
            # Limit variants if needed
            variants = fiber_data["variants"]
            if len(variants) > max_variants:
                variants = variants[:max_variants]
            
            return {
                "word": word,
                "base_embedding": word_data["base_embedding"],
                "fiber": {
                    "variants": variants,
                    "radius": fiber_data["radius"],
                    "geometry": fiber_data["geometry"]
                },
                "connections": [
                    conn for conn in mock_data["connections"]
                    if conn["source"] == word or conn["target"] == word
                ]
            }
    
    # Word not found
    raise HTTPException(status_code=404, detail=f"Word '{word}' not found")

@app.get("/api/experiments")
async def list_experiments():
    """
    List available experiments.
    """
    config_dir = Path(__file__).parent.parent / "configs"
    experiments = []
    
    if config_dir.exists():
        for config_file in config_dir.glob("*.yaml"):
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                experiments.append({
                    "id": config_file.stem,
                    "name": config.get("experiment", {}).get("name", config_file.stem),
                    "description": config.get("experiment", {}).get("description", ""),
                    "geometry": config.get("model", {}).get("geometry", "unknown"),
                    "status": "completed"  # Mock status
                })
    
    return {
        "experiments": experiments,
        "total": len(experiments)
    }

@app.get("/api/results/{experiment_id}")
async def get_experiment_results(experiment_id: str):
    """
    Get results for a specific experiment.
    
    Args:
        experiment_id: Experiment ID (config filename without .yaml)
    """
    # For now, return mock results
    mock_results = {
        "experiment_id": experiment_id,
        "status": "completed",
        "metrics": {
            "mean_rank": 15.3,
            "map": 0.67,
            "spearman": 0.72,
            "training_time": 125.4  # seconds
        },
        "embeddings_path": f"results/{experiment_id}/embeddings.npy",
        "config_path": f"configs/{experiment_id}.yaml",
        "log_path": f"results/{experiment_id}/train_*.log"
    }
    
    return mock_results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)