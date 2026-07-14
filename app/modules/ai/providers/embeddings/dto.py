from dataclasses import dataclass

@dataclass(slots=True)
class Embedding:
    """Embedding data: vector, model name, and dimension."""
    vector: list[float]
    model: str
    dimension: int