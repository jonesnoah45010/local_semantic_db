from sentence_transformers import SentenceTransformer
import chromadb
import uuid
from pathlib import Path

class local_semantic_db:
    def __init__(self, persist_directory="chroma_db",collection_name="my_collection",sentence_transformer_name='all-MiniLM-L6-v2'):
        """
        Initialize the vector database using PersistentClient.
        Data will be persisted at the specified path.
        """
        persist_path = Path(persist_directory)
        if not persist_path.exists():
            persist_path.mkdir(parents=True, exist_ok=True)
            
        self.embedding_model = SentenceTransformer(sentence_transformer_name) 
        self.client = chromadb.PersistentClient(path=str(persist_path))
        self.collection = None
        self.collection_name = None
        if collection_name is not None:
            self.collection_name = collection_name
            self.set_collection(collection_name)


    def set_collection(self, collection_name="my_collection"):
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(collection_name)


    def embed_text(self, text):
        """
        Generate embeddings for the input text using the embedding model.
        """
        return self.embedding_model.encode(text).tolist()

    def embed_texts(self, texts, batch_size=16, show_progress_bar=True):
        return self.embedding_model.encode(texts, batch_size=batch_size, show_progress_bar=show_progress_bar).tolist()


    def insert(self, text=None, metadata=None, text_id=None):
        """
        Add or update an entry in the database.
        :param text_id: Unique identifier for the text.
        :param text: The text content to be stored.
        :param metadata: Optional dictionary containing metadata for the text.
        """
        if type(text) is list and type(metadata) is list and type(text_id) is list:
            return self.batch_insert(texts=text, metadatas=metadata, text_ids=text_id)

        if text_id is None:
            text_id = str(uuid.uuid4())  # Generate a UUID if text_id is None
        
        if not text:
            raise ValueError("The text content cannot be None.")
        
        embedding = self.embed_text(text)  # Generate embedding for the text

        self.collection.upsert(
            ids=[text_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata] if metadata else None
        )

        print(f"Upserted text with ID: {text_id}, Metadata: {metadata}")
        return text_id


    def batch_insert(self, texts=None, metadatas=None, text_ids=None):
        """
        Add or update multiple entries in the database efficiently.
        :param texts: List of text content to be stored.
        :param metadatas: List of metadata dictionaries for each text.
        :param text_ids: List of unique identifiers for the texts.
        """
        if texts is None or not isinstance(texts, list) or len(texts) == 0:
            raise ValueError("The 'texts' parameter must be a non-empty list of strings.")
        # Generate unique IDs if not provided
        if text_ids is None:
            text_ids = [str(uuid.uuid4()) for _ in texts]
        elif len(text_ids) != len(texts):
            raise ValueError("The number of 'text_ids' must match the number of 'texts'.")

        # Make sure all text_ids exist if incomplete list provided
        if any(x is None for x in text_ids):
            i = 0
            for item in text_ids:
                if item is None:
                    text_ids[i] = uuid.uuid4()
                i+=1

        # Generate embeddings for all texts in batch
        embeddings = self.embed_texts(texts)

        # If metadatas are not provided, default to None
        if metadatas is None:
            metadatas = [None] * len(texts)
        elif len(metadatas) != len(texts):
            raise ValueError("The number of 'metadatas' must match the number of 'texts'.")
        
        # Perform batched upsert
        self.collection.upsert(
            ids=text_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        print(f"Upserted {len(texts)} texts into the database.")
        return text_ids


    def query(self, query_text, top_k=5, where=None):
        """
        Query the database for semantically similar entries.
        :param query_text: The input text to find similar entries.
        :param top_k: The number of similar entries to retrieve.
        :param where: Optional dictionary for filtering results based on metadata.
        :return: list of dicts.
        Example:
            filter_metadata_values = ["123", "456", "101"]
            query_result = db.query(
                query_text="physical activity, sports, and fitness",
                top_k=3,
                where={"metadata_key": {"$in": filter_ids}}  # Use $in to filter by multiple values
            )
            query_result = db.query(
                query_text="physical activity, sports, and fitness",
                top_k=2,
                where={"metadata_key": "456"}  # Add a filter condition on metadata
            )
        """
        embedding = self.embed_text(query_text)  # Generate embedding for the query text

        query_params = {
            "query_embeddings": [embedding],
            "n_results": top_k,
        }

        if where:
            query_params["where"] = where

        results = self.collection.query(**query_params)

        # Flatten the results
        flattened_results = []
        for i in range(len(results["ids"][0])):
            flattened_results.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else None,
                "distance": results["distances"][0][i]
            })
        return flattened_results


    def get(self, text_id):
        """
        Retrieve an entry from the database based on the ID.
        :param text_id: Unique identifier for the text entry.
        :return: A dictionary containing the entry data (text and metadata).
        """
        results = self.collection.get(ids=[text_id])
        if not results["documents"]:
            raise ValueError(f"No entry found with ID: {text_id}")
        
        entry = {
            "id": text_id,
            "text": results["documents"][0],
            "metadata": results["metadatas"][0] if results["metadatas"] else None
        }
        return entry


    def delete(self, text_id):
        """
        Delete an entry from the database based on the ID.
        :param text_id: Unique identifier for the text entry.
        """
        self.collection.delete(ids=[text_id])
        print(f"Deleted entry with ID: {text_id}")


    def update(self, text_id, text=None, metadata=None):
        """
        Update an existing entry in the database.
        Raises an error if the entry does not exist.
        """
        if text_id is None:
            raise ValueError(f"Must use valid text_id, text_id should not be None")
        results = self.collection.get(ids=[text_id])
        if not results["documents"]:
            raise ValueError(f"No entry found with ID: {text_id}")
        
        self.collection.upsert(
            ids=[text_id],
            documents=[text],
            metadatas=[metadata] if metadata else None
        )
        print(f"Updated entry with ID: {text_id}, Metadata: {metadata}")











if __name__ == "__main__":
    # Initialize DB
    db = local_semantic_db(collection_name="interests")

    # # Insert some entries
    # db.insert("I enjoy hiking and mountain climbing.", metadata={"name": "Alice"})
    # db.insert("Swimming and running are my favorite activities.", metadata={"name": "Bob"})
    # db.insert("I love reading books and watching movies.", metadata={"name": "Charlie"})
    # db.insert("I like working out and running.", metadata={"name": "Charlie"})


    texts = ['An article about football and soccer', 'An article about baseball', 'A detailed explanation of quantum mechanics', 'A guide to making the perfect lasagna', 'Exploring the beaches in Hawaii', 'Advice on cardio workouts and staying fit']
    metadatas = [{'name': 'Sports Article', 'category': 'sports', 'page_number': 12}, {'name': 'Sports Article 2', 'category': 'sports', 'page_number': 13}, {'name': 'Science News', 'category': 'science', 'page_number': 45}, {'name': 'Cooking Tips', 'category': 'cooking', 'page_number': 30}, {'name': 'Travel Guide', 'category': 'travel', 'page_number': 70}, {'name': 'Fitness Tips', 'category': 'fitness', 'page_number': 15}]
    text_ids = None


    # Insert multiple entries using batch_insert
    db.batch_insert(texts=texts, metadatas=metadatas, text_ids=text_ids)

    # Query for similar entries related to 'physical activity'
    query_result = db.query("physical activity, sports, and fitness", top_k=2)
    query_result_filter = db.query("physical activity, sports, and fitness", top_k=1, where={"name":"Charlie"})

    print("\nwithout filter...\n")
    print(query_result)

    print("\nwith filter...\n")
    print(query_result_filter)















