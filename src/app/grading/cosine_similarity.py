from sentence_transformers import util
from app.init_objects import get_embedding_model

import asyncio


def cosine_similarity(a, b):
    return float(util.cos_sim(a, b)[0][0])


async def get_cosine_similarity(reference_answer: str, answer: str) -> float:
    embedding = get_embedding_model()

    reference_embedding, answer_embedding = await asyncio.gather(
        embedding.aembed_query(reference_answer), embedding.aembed_query(answer)
    )

    similarity = cosine_similarity(reference_embedding, answer_embedding)

    return similarity
