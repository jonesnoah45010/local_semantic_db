


# Local Semantic Database

## Overview

This Python script implements a local semantic database using `chromadb` and `SentenceTransformer` for managing and querying text entries based on semantic similarity. The database is persistent and supports efficient operations for adding, updating, deleting, and querying text entries with optional metadata.

----------

## Features

-   **Persistence**: The database uses `chromadb.PersistentClient` to store data on disk, ensuring data is retained across sessions.
    
-   **Text Embedding**: Utilizes `SentenceTransformer` models to generate semantic embeddings of text entries.
    
-   **Batch Operations**: Supports efficient batch insertion of multiple text entries.
    
-   **Flexible Queries**: Allows querying for semantically similar entries, with optional metadata-based filters.
    
-   **CRUD Operations**:
    
    -   Create: Insert or batch-insert text entries with optional metadata.
        
    -   Read: Retrieve specific entries by ID or query similar entries.
        
    -   Update: Modify existing entries.
        
    -   Delete: Remove entries from the database.
        

----------

## Installation

### Prerequisites

Ensure you have Python installed (version >= 3.7).

### Dependencies

Install the required dependencies:

```
pip install -r requirements.txt
```

**requirements.txt**:

```
chromadb
sentence-transformers
numpy<2.0
textsplit
```

----------

## Usage

### Initialization

To initialize the semantic database:

```
from local_semantic_db import local_semantic_db

# Initialize the database
semantic_db = local_semantic_db(collection_name="my_collection")
```

### Adding Entries

-   **Single Entry**:
    

```
semantic_db.insert(
    text="I enjoy hiking and mountain climbing.",
    metadata={"name": "Alice"}
)
```

-   **Batch Entries**:
    

```
texts = [
    'An article about football and soccer',
    'A guide to making the perfect lasagna'
]

metadatas = [
    {"name": "Sports", "category": "sports"},
    {"name": "Cooking Tips", "category": "cooking"}
]

semantic_db.batch_insert(texts=texts, metadatas=metadatas)
```

### Querying

-   **Basic Query**:
    

```
query_result = semantic_db.query("physical activity, sports, and fitness", top_k=5)
print(query_result)
```

-   **Filtered Query**:
    

```
query_result = semantic_db.query(
    "physical activity",
    top_k=3,
    where={"category": "sports"}
)
print(query_result)
```

### CRUD Operations

-   **Retrieve Entry**:
    

```
entry = semantic_db.get(text_id="some_id")
print(entry)
```

-   **Update Entry**:
    

```
semantic_db.update(
    text_id="some_id",
    text="Updated text content",
    metadata={"name": "Updated Name"}
)
```

-   **Delete Entry**:
    

```
semantic_db.delete(text_id="some_id")
```

----------

## Example

```
if __name__ == "__main__":
    db = local_semantic_db(collection_name="interests")

    texts = [
        'An article about football and soccer',
        'Exploring the beaches in Hawaii'
    ]

    metadatas = [
        {"name": "Sports Article", "category": "sports"},
        {"name": "Travel Guide", "category": "travel"}
    ]

    # Insert entries
    db.batch_insert(texts=texts, metadatas=metadatas)

    # Query entries
    result = db.query("football", top_k=2)
    print(result)
```

----------

## Project Structure

-   `local_semantic_db.py`: Core script implementing the semantic database.
    
-   `requirements.txt`: Dependency list.
    

----------

## Limitations

-   The script currently supports only local persistence using `chromadb`.
    
-   Limited filtering options for metadata queries.
    

----------

## Future Improvements

-   Add support for remote databases.
    
-   Enhance metadata filtering capabilities.
    
-   Optimize batch processing for larger datasets.
    

----------

## License

This project is open-source and available under the MIT License.