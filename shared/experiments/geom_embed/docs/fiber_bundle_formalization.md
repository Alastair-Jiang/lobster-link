# Fiber Bundle Formalization for Geometric Embeddings

_Draft version 0.1 – 2026-03-30_

## 1. Philosophical Framework (Dongxu's View)

> "创新和一般进步的区别在于创新是地基向上搭建、空中楼阁同时向下联通的过程，所以不合理性不应该被直接否定，而是合理化。"

This means innovation often starts with a bold conceptual framework ("castle in the air") that is later grounded in rigor ("building foundations downward"). We embrace this exploratory mindset.

## 2. Informal Definition

### Fiber (纤维)
**Definition**: "相近义的量化指标维度距离与关系"  
**Interpretation**: For each word/concept, its fiber is a local geometric space containing:
- Synonyms and near-synonyms
- Contextual variants
- Related terms with quantified semantic distances

**Example**: The fiber for "cat" might contain {"猫咪", "小猫", "喵星人", "feline", ...} with pairwise distances representing semantic similarity.

### Connection (联络)
**Definition**: "纤维的分散和集群"  
**Interpretation**: The mechanism describing how fibers:
- **Disperse** into variants (polysemy, contextual shifts)
- **Cluster** into higher-level semantic groups

**Example**: How "cat" fibers connect to "pet" fibers to "animal" fibers (hierarchy), or how "cat" ↔ "dog" fibers relate through analogy.

## 3. Mathematical Formalization (Draft)

### 3.1 Basic Structure

We define a **semantic fiber bundle** (E, π, B, F) where:

- **Total space E**: The complete semantic representation space
- **Base space B**: Word embeddings in some global geometry (Euclidean/Hyperbolic/Spherical)
- **Projection π**: E → B maps each point in a fiber to its base word
- **Fiber Fₓ**: The local geometric space over word x ∈ B

### 3.2 Fiber Construction

For a word w with embedding b_w ∈ B:
```
F_w = { (b_w, v) | v ∈ V_w }
```
where V_w is a vector space (or manifold) representing the local variations of w.

### 3.3 Connection (Ehresmann Connection)

A connection Γ on E specifies:
1. **Horizontal distribution**: How to move between fibers while preserving semantic relationships
2. **Parallel transport**: How to translate semantic meaning from one fiber to another

**Example operations**:
- **Analogy transport**: king → queen ≈ man → woman
- **Hierarchy transport**: cat → animal (upward), animal → cat (downward)
- **Polysemy transport**: "bank" (financial) → "bank" (river)

## 4. Implementation Sketch

### 4.1 Data Structure
```python
class SemanticFiberBundle:
    def __init__(self, base_geometry="euclidean", fiber_dim=50):
        self.base_manifold = create_manifold(base_geometry)
        self.fibers = {}  # word -> Fiber object
        
    class Fiber:
        def __init__(self, base_embedding):
            self.base = base_embedding
            self.variants = []  # list of (variant_embedding, relation_type)
            self.metric = None  # distance function on fiber
```

### 4.2 Connection Implementation
```python
class SemanticConnection:
    def parallel_transport(self, vector, from_fiber, to_fiber, relation_type):
        """
        Transport semantic vector from one fiber to another.
        
        Args:
            vector: Semantic variation to transport
            from_fiber: Source fiber
            to_fiber: Target fiber  
            relation_type: "analogy", "hierarchy", "synonym", etc.
        """
        # Implementation depends on relation type
        if relation_type == "analogy":
            return self.analogy_transport(vector, from_fiber, to_fiber)
        elif relation_type == "hierarchy":
            return self.hierarchical_transport(vector, from_fiber, to_fiber)
        # ...
```

## 5. Success Criteria

**Exploratory Research Mindset**:
- ≥10% improvement over Euclidean baseline is considered **positive signal**
- We're looking for **proof of concept**, not production-ready performance
- "Unreasonable" aspects should be **rationalized**, not rejected

## 6. Research Questions

1. **Fiber geometry**: What local geometry best captures semantic variations?
2. **Connection learning**: Can connections be learned from data (e.g., WordNet, BATS)?
3. **Base vs fiber tradeoff**: How much semantic information should be in base vs fiber?
4. **Computational efficiency**: Can we make this practical for large vocabularies?

## 7. Next Steps

1. **Week 1**: Implement basic fiber bundle structure for 100 core words
2. **Week 2**: Implement analogy and hierarchy connections
3. **Week 3**: Quantitative evaluation on WordNet/BATS
4. **Week 4**: Visualization platform integration