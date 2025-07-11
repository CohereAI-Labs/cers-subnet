import requests
import os
import uuid
import argparse

# --- Configuration ---
def get_config():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Test script for the miner's API.")
    parser.add_argument("--host", default=os.getenv("MINER_HOST", "127.0.0.1"), help="Miner host address.")
    parser.add_argument("--port", type=int, default=int(os.getenv("MINER_PORT", 8001)), help="Miner API port.")
    return parser.parse_args()

# Load the API key from an environment variable for security
API_KEY = os.getenv("MINER_API_KEY")

def test_upsert_document(base_url: str):
    """Tests the /documents endpoint to upsert a document."""
    print("--- Testing Document Upsert ---")
    
    if not API_KEY:
        print("🔴 ERROR: MINER_API_KEY environment variable is not set.")
        return None

    doc_id = f"test-doc-{uuid.uuid4()}"
    doc_content = "This is a test document about AI and decentralized networks."
    
    url = f"{base_url}/documents"
    headers = {"X-API-Key": API_KEY}
    payload = {"id": doc_id, "document": doc_content}

    print(f"Attempting to upsert document with ID: {doc_id}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            print(f"✅ Success: Document upserted successfully. Response: {response.json()}")
            return doc_id
        else:
            print(f"🔴 Failure: Received status code {response.status_code}. Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"🔴 ERROR: An exception occurred during the request: {e}")
        return None

def test_delete_document(base_url: str, doc_id: str):
    """Tests the /documents/{doc_id} endpoint to delete a document."""
    print("\n--- Testing Document Deletion ---")

    url = f"{base_url}/documents/{doc_id}"
    headers = {"X-API-Key": API_KEY}

    print(f"Attempting to delete document with ID: {doc_id}")

    try:
        response = requests.delete(url, headers=headers)

        if response.status_code == 200:
            print(f"✅ Success: Document deleted successfully. Response: {response.json()}")
        else:
            print(f"🔴 Failure: Received status code {response.status_code}. Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"🔴 ERROR: An exception occurred during the request: {e}")

if __name__ == "__main__":
    config = get_config()
    base_url = f"http://{config.host}:{config.port}"
    print(f"Starting miner API tests for {base_url}...")
    upserted_doc_id = test_upsert_document(base_url)
    if upserted_doc_id:
        test_delete_document(base_url, upserted_doc_id)
    print("\nAPI tests finished.")