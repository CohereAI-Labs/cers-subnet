# The MIT License (MIT)
# Copyright © 2024 Cohere

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import time
import typing
import bittensor as bt

# Bittensor Miner Template:
import cers_subnet

import torch
from sentence_transformers import SentenceTransformer

import asyncio
import secrets
import chromadb
import csv
import os

# import base miner class which takes care of most of the boilerplate
from cers_subnet.base.miner import BaseMinerNeuron

# New imports for the API
import fastapi
import uvicorn
import threading, os, csv
from pydantic import BaseModel


class DocumentPayload(BaseModel):
    id: str
    document: str

class Miner(BaseMinerNeuron):
    """
    Your miner neuron class. You should use this class to define your miner's behavior. In particular, you should replace the forward function with your own logic. You may also want to override the blacklist and priority functions according to your needs.

    This class inherits from the BaseMinerNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a miner such as blacklisting unrecognized hotkeys, prioritizing requests based on stake, and forwarding requests to the forward function. If you need to define custom
    """

    def __init__(self, config=None):
        super(Miner, self).__init__(config=config)

        # TODO(developer): Set up everything specific to your use case here.
        # For example, loading a search model, a vector database, etc.
        bt.logging.info("Miner for Cohere Enterprise RAG Subnet initialized.")

        # For this example, we'll use a sentence-transformer model for embeddings.
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        bt.logging.info("Sentence Transformer model loaded.")

        # Explicitly move the model to the configured device (e.g., "cuda" or "cpu")
        self.device = self.config.get("neuron.device", "cuda" if torch.cuda.is_available() else "cpu")
        self.embedding_model.to(self.device)
        bt.logging.info(f"Embedding model moved to device: {self.device}")

        # --- Configuration for API and Database ---
        self.api_port = self.config.get('miner.api_port', 8001)
        self.api_key = os.getenv('MINER_API_KEY')
        db_path = self.config.get('miner.db_path', './chroma_db')
        collection_name = self.config.get('miner.collection_name', 'enterprise-rag')

        if not self.api_key:
            bt.logging.error(
                "MINER_API_KEY environment variable not set. The miner's API will be unsecured. Please set a secure key."
            )

        # Setup ChromaDB. We'll use a persistent client to store data on disk.
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            # It's good practice to specify the embedding function for the collection
            # although we are providing the embeddings manually in this case.
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )
        bt.logging.info("ChromaDB client and collection initialized.")

        # If the collection is empty, we populate it with initial documents from a CSV file in batches.
        if self.collection.count() == 0:
            bt.logging.info("ChromaDB collection is empty. Populating with initial documents...")
            self.load_documents_from_csv()
        
        # Setup and run the API server in a background thread
        self.app = fastapi.FastAPI()
        self.api_key_header = fastapi.security.APIKeyHeader(name="X-API-Key", auto_error=False)
        self.setup_api_routes()

        self.api_thread = threading.Thread(
            target=self.run_api,
            daemon=True
        )
        self.api_thread.start()

    def load_documents_from_csv(self):
        """Loads documents from a CSV file and adds them to the ChromaDB collection."""
        documents_file = self.config.get('miner.documents_file', 'data/documents.csv')
        documents_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            documents_file
        )
        
        batch_size = self.config.get('miner.batch_size', 100)
        bt.logging.info(f"Starting to load documents from {documents_path} with batch size {batch_size}.")

        try:
            documents_to_add, ids_to_add = [], []
            with open(documents_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ids_to_add.append(row['id'])
                    documents_to_add.append(row['text'])

                    if len(ids_to_add) >= batch_size:
                        embeddings = self.embedding_model.encode(documents_to_add).tolist()
                        self.collection.add(embeddings=embeddings, ids=ids_to_add)
                        bt.logging.info(f"Added batch of {len(documents_to_add)} documents to ChromaDB.")
                        documents_to_add, ids_to_add = [], []
            
            # Add any remaining documents
            if documents_to_add:
                embeddings = self.embedding_model.encode(documents_to_add).tolist()
                self.collection.add(embeddings=embeddings, ids=ids_to_add)
                bt.logging.info(f"Added final batch of {len(documents_to_add)} documents to ChromaDB.")

        except FileNotFoundError:
            bt.logging.error(f"Documents file not found at {documents_path}. Cannot populate miner knowledge base.")
        except Exception as e:
            bt.logging.error(f"Failed to load documents from CSV: {e}")

    def get_api_key(self, api_key_header: str = fastapi.Security(api_key_header)):
        # Use secrets.compare_digest for constant-time comparison to help prevent timing attacks
        if api_key_header and self.api_key and secrets.compare_digest(api_key_header, self.api_key):
            return api_key_header
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

    def run_api(self) -> None:
        """Runs the FastAPI server."""
        bt.logging.info(f"Running API server on port {self.api_port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.api_port)

    def setup_api_routes(self) -> None:
        """Sets up the API routes for the miner."""
        @self.app.post("/documents", status_code=201)
        async def upsert_endpoint(payload: DocumentPayload, api_key: str = fastapi.Security(self.get_api_key)):
            if not await self.upsert_document(payload.id, payload.document):
                raise fastapi.HTTPException(status_code=500, detail="Failed to upsert document")
            return {"status": "success", "id": payload.id, "message": "Document upserted successfully."}

        @self.app.delete("/documents/{doc_id}")
        async def delete_endpoint(doc_id: str, api_key: str = fastapi.Security(self.get_api_key)):
            if not await self.delete_document(doc_id):
                raise fastapi.HTTPException(status_code=404, detail="Document not found or failed to delete")
            return {"status": "success", "id": doc_id, "message": "Document deleted successfully."}

        @self.app.get("/health", status_code=200)
        def health_check():
            """A simple health check endpoint for monitoring."""
            return {"status": "ok"}

    async def forward(
        self, synapse: cers_subnet.protocol.EnterpriseRAG
    ) -> cers_subnet.protocol.EnterpriseRAG:
        """
        Processes the incoming 'EnterpriseRAG' synapse by performing a simulated document search.
        This method should be replaced with actual logic relevant to the miner's purpose.

        Args:
            synapse (cers_subnet.protocol.EnterpriseRAG): The synapse object containing the query.

        Returns:
            cers_subnet.protocol.EnterpriseRAG: The synapse object with the 'documents' field filled with the search results.
        """
        # Now, we use ChromaDB to perform the semantic search.
        bt.logging.info(f"Received query: {synapse.query}")

        def _search_and_retrieve(query: str) -> list:
            """
            Encapsulates the synchronous, CPU/GPU-bound and I/O-bound operations.
            """
            # 1. Encode the query to get its embedding.
            query_embedding = self.embedding_model.encode(query).tolist()

            # 2. Query ChromaDB for the top-k most similar documents.
            k = self.config.get('miner.search_k', 2)  # Number of documents to return
            
            # Ensure we don't ask for more results than exist
            n_results = min(k, self.collection.count())
            if n_results == 0:
                return []
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            return results.get('ids', [[]])[0]

        # Run the blocking operations in a separate thread to avoid blocking the asyncio event loop.
        # This is crucial for maintaining responsiveness under load.
        synapse.document_ids = await asyncio.to_thread(_search_and_retrieve, synapse.query)

        bt.logging.info(f"Returning {len(synapse.document_ids)} document IDs.")
        return synapse

    def _blocking_upsert(self, doc_id: str, document: str):
        """
        The synchronous, blocking part of the upsert operation.
        This involves encoding the document and writing to the database.
        """
        embedding = self.embedding_model.encode(document).tolist()
        self.collection.upsert(
            ids=[doc_id],
            embeddings=[embedding]
            # We do not store the document content itself for security reasons.
        )

    async def upsert_document(self, doc_id: str, document: str) -> bool:
        """
        Asynchronously upserts a document into the ChromaDB collection.

        Args:
            doc_id (str): The unique ID of the document to update.
            document (str): The text content for the document.
        
        Returns:
            bool: True if upsert was successful, False otherwise.
        """
        try:
            await asyncio.to_thread(self._blocking_upsert, doc_id, document)
            bt.logging.info(f"Successfully upserted document with id: {doc_id}")
            return True
        except Exception as e:
            bt.logging.error(f"Failed to upsert document with id {doc_id}: {e}")
            return False

    def _blocking_delete(self, doc_id: str):
        """The synchronous, blocking part of the delete operation."""
        self.collection.delete(ids=[doc_id])

    async def delete_document(self, doc_id: str) -> bool:
        """Asynchronously deletes a document from the ChromaDB collection using its ID."""
        try:
            await asyncio.to_thread(self._blocking_delete, doc_id)
            bt.logging.info(f"Successfully deleted document with id: {doc_id}")
            return True
        except Exception as e:
            bt.logging.error(f"Failed to delete document with id {doc_id}: {e}")
            return False

    async def blacklist(
        self, synapse: cers_subnet.protocol.EnterpriseRAG
    ) -> typing.Tuple[bool, str]:
        """
        Determines whether an incoming request should be blacklisted and thus ignored. Your implementation should
        define the logic for blacklisting requests based on your needs and desired security parameters.

        Blacklist runs before the synapse data has been deserialized (i.e. before synapse.data is available).
        The synapse is instead contracted via the headers of the request. It is important to blacklist
        requests before they are deserialized to avoid wasting resources on requests that will be ignored.

        Args:
            synapse (cers_subnet.protocol.EnterpriseRAG): A synapse object constructed from the headers of the incoming request.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the synapse's hotkey is blacklisted,
                            and a string providing the reason for the decision.

        This function is a security measure to prevent resource wastage on undesired requests. It should be enhanced
        to include checks against the metagraph for entity registration, validator status, and sufficient stake
        before deserialization of synapse data to minimize processing overhead.

        Example blacklist logic:
        - Reject if the hotkey is not a registered entity within the metagraph.
        - Consider blacklisting entities that are not validators or have insufficient stake.

        In practice it would be wise to blacklist requests from entities that are not validators, or do not have
        enough stake. This can be checked via metagraph.S and metagraph.validator_permit. You can always attain
        the uid of the sender via a metagraph.hotkeys.index( synapse.dendrite.hotkey ) call.

        Otherwise, allow the request to be processed further.
        """

        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            bt.logging.warning(
                "Received a request without a dendrite or hotkey."
            )
            return True, "Missing dendrite or hotkey"

        # TODO(developer): Define how miners should blacklist requests.
        uid = self.metagraph.hotkeys.index(synapse.dendrite.hotkey)
        if (
            not self.config.blacklist.allow_non_registered
            and synapse.dendrite.hotkey not in self.metagraph.hotkeys
        ):
            # Ignore requests from un-registered entities.
            bt.logging.trace(
                f"Blacklisting un-registered hotkey {synapse.dendrite.hotkey}"
            )
            return True, "Unrecognized hotkey"

        if self.config.blacklist.force_validator_permit:
            # If the config is set to force validator permit, then we should only allow requests from validators.
            if not self.metagraph.validator_permit[uid]:
                bt.logging.warning(
                    f"Blacklisting a request from non-validator hotkey {synapse.dendrite.hotkey}"
                )
                return True, "Non-validator hotkey"

        bt.logging.trace(
            f"Not Blacklisting recognized hotkey {synapse.dendrite.hotkey}"
        )
        return False, "Hotkey recognized!"

    async def priority(self, synapse: cers_subnet.protocol.EnterpriseRAG) -> float:
        """
        The priority function determines the order in which requests are handled. More valuable or higher-priority
        requests are processed before others. You should design your own priority mechanism with care.

        This implementation assigns priority to incoming requests based on the calling entity's stake in the metagraph.

        Args:
            synapse (cers_subnet.protocol.EnterpriseRAG): The synapse object that contains metadata about the incoming request.

        Returns:
            float: A priority score derived from the stake of the calling entity.

        Miners may receive messages from multiple entities at once. This function determines which request should be
        processed first. Higher values indicate that the request should be processed first. Lower values indicate
        that the request should be processed later.

        Example priority logic:
        - A higher stake results in a higher priority value.
        """
        if synapse.dendrite is None or synapse.dendrite.hotkey is None:
            bt.logging.warning(
                "Received a request without a dendrite or hotkey."
            )
            return 0.0

        # TODO(developer): Define how miners should prioritize requests.
        caller_uid = self.metagraph.hotkeys.index(
            synapse.dendrite.hotkey
        )  # Get the caller index.
        priority = float(
            self.metagraph.S[caller_uid]
        )  # Return the stake as the priority.
        bt.logging.trace(
            f"Prioritizing {synapse.dendrite.hotkey} with value: {priority}"
        )
        return priority


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with Miner() as miner:
        while True:
            bt.logging.info(f"Miner running... {time.time()}")
            time.sleep(5)
