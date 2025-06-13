import pinecone
from pinecone import Pinecone, ServerlessSpec
from app.core.settings import get_settings

settings = get_settings()

pc = Pinecone(api_key=settings.pinecone_api_key)


# Check or create your index
index_name = "products2"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name, 
        dimension=384, 
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-west-1'
        )
    )

index = pc.Index(index_name)
