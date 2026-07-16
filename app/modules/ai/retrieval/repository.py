from sqlalchemy import select

from app.common.repository.base import BaseRepository

from app.modules.document.models import DocumentChunk

class RetrievalChunkRepository(BaseRepository[DocumentChunk]):
    def __init__(self, db):
        super().__init__(db, DocumentChunk)

    async def similarity_search(self, query_embedding: list[float], top_k: int = 5) -> list[DocumentChunk]:
        """Return top_k DocumentChunk instances with a `score` attribute set.

        The query selects both the mapped `DocumentChunk` and the cosine distance
        expression. We attach the returned score to the ORM instance so callers
        can read `chunk.score`.
        """
        score_expr = DocumentChunk.embedding.cosine_distance(query_embedding)
        stmt = select(DocumentChunk, score_expr.label("score")).order_by(score_expr).limit(top_k)
        result = await self.db.execute(stmt)
        rows = result.all()

        chunks: list[DocumentChunk] = []
        for row in rows:
            # SQLAlchemy returns a Row with (DocumentChunk, score)
            chunk, score = row[0], row[1]
            try:
                setattr(chunk, "score", float(score) if score is not None else None)
            except Exception:
                # fallback: ignore if we cannot set attribute
                pass
            chunks.append(chunk)

        return chunks