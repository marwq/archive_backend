import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any, Optional
from llama_index.embeddings.gemini import GeminiEmbedding
from config import settings
from dataclasses import dataclass


model_name = "models/embedding-001"

embed_model = GeminiEmbedding(
    model_name=model_name, api_key=settings.GOOGLE_AI_API_KEY, title="this is a document"
)


@dataclass
class Doc:
    text: str
    id: str


def initialize_pinecone() -> Pinecone:
    # load_dotenv(find_dotenv())  # read local .env file
    api_key = settings.PINECONE_API_KEY
    environment = settings.PINECONE_ENVIRONMENT
    index_name = 'archive-hackaton'

    pc = Pinecone(api_key=api_key)

    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=768,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='azure',
                region=environment
            )
        )

    return pc.Index(index_name)


def text_to_vector(doc: Doc, index: Optional[Pinecone.Index] = None) -> List[float]:
    if index is None:
        index = initialize_pinecone()
    # Generate the vector for the document text
    vector = embed_model.get_text_embedding(doc.text)

    # Upsert the document to Pinecone
    index.upsert(vectors=[(doc.id, vector, {"id": doc.id, "text": doc.text})])

    return vector


def clear_all_docs(index: Pinecone.Index):
    index.delete(delete_all=True)


def search_text(text: str, index: Pinecone.Index) -> List[Dict[str, Any]]:
    # Generate the vector for the search text
    vector = embed_model.get_text_embedding(text)

    results = index.query(
        vector=vector,
        top_k=9,  # Number of top results to return
        include_metadata=True  # Include the metadata of the results
    )

    metadata_results = [match['metadata'] for match in results['matches']]
    return metadata_results
