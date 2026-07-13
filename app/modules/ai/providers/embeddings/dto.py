from dataclasses import dataclass

@dataclass(slots=True)
class Embedding:
    """
    Represents an embedding for a chunk of data.

    Attributes:
        vector (list[float]): The embedding vector.
        model (str): The name of the model used to generate the embedding.
        dimension (int): The dimensionality of the embedding vector.
    """
    vector: list[float]
    model: str
    dimension: int