# CERS Subnet Miner

This document provides a comprehensive guide for setting up and running a miner on the Cohere Enterprise RAG Subnet (CERS).

## Introduction

Miners are the backbone of the CERS subnet. Their primary role is to act as high-performance, specialized retrieval engines for enterprise data. By participating as a miner, you contribute to a decentralized marketplace for information retrieval and earn TAO rewards based on your performance.

The responsibilities of a miner include:
1.  **Securely Indexing Data**: Miners expose a private API that allows enterprises to push document embeddings (not raw text) for indexing. These embeddings are stored in a high-performance vector database.
2.  **Efficient Searching**: Miners run sophisticated search algorithms on their indexed vectors to find the most relevant documents for a given query from a validator.
3.  **Returning Results**: Miners return a ranked list of document IDs to the validator, which are then scored for accuracy and speed.

Top-performing miners (those who are fast, accurate, and reliable) receive the highest rewards.

## Hardware Requirements

To be competitive, miners should run on hardware capable of handling large-scale vector search and embedding generation efficiently.

-   **GPU**: **Highly Recommended**. While the miner can run on a CPU, a dedicated NVIDIA GPU with at least 12GB of VRAM is recommended for competitive performance. This allows for faster processing of potential custom embedding models and large-scale similarity searches.
-   **CPU**: A modern multi-core CPU (e.g., 8+ cores).
-   **RAM**: Minimum 32GB. More RAM is beneficial for caching and handling large datasets.
-   **Storage**: A fast NVMe SSD with at least 200GB of free space. The storage requirement will grow depending on the amount of data indexed.
-   **Network**: A stable, low-latency internet connection.

## 🔒 Security Best Practices

Running a miner involves exposing an API to the internet, so security is critical. Follow these best practices to protect your node and the data you are entrusted with.

### 1. API Key Management
Your `MINER_API_KEY` is a secret and must be protected.

-   **Use Strong, Random Keys**: Generate a long, random string for your API key.
-   **Use Environment Variables**: As shown in the examples, always load your API key from an environment variable. **Never hardcode it in your scripts or commit it to version control (e.g., Git).**
-   **Do Not Share It**: The API key should only be known to you and the enterprise/validator you are serving.

### 2. Network Security
By default, the miner's API is accessible on the network.

-   **Firewall Configuration**: It is **highly recommended** to configure a firewall on your server to restrict access to the miner's API port (`--miner.api_port`, default `8001`). Only allow incoming connections from the specific IP addresses of the validators or enterprise systems that need to push data to you. This prevents unauthorized access and potential abuse.
-   **Avoid Exposing Unnecessary Ports**: Only expose the ports that are absolutely necessary for the miner's operation (the API port and the Bittensor axon port).

### 3. Data Handling
This subnet is designed with a privacy-first approach.

-   **No Raw Data**: Remember that as a miner, you only handle non-reversible numerical embeddings and document IDs, not the original sensitive document content. This significantly reduces your security risk and liability.

### 4. System Hardening
-   **Regular Updates**: Keep your operating system and all software dependencies (including Python packages and Docker) up to date with the latest security patches.
-   **Principle of Least Privilege**: Run the miner process with a dedicated, non-root user that has only the necessary permissions to operate.

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/CohereAI-Labs/cers-subnet.git
cd cers-subnet
```

### 2. Install Dependencies
It is highly recommended to use a virtual environment.
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install the package in editable mode
pip install -e .
```

### 3. Configure Your Wallet
You need a Bittensor wallet to participate. If you don't have one, create it:
```bash
# Create a new coldkey and hotkey
btcli wallet new_coldkey --wallet.name my_miner_wallet
btcli wallet new_hotkey --wallet.name my_miner_wallet --wallet.hotkey default
```

## Running the Miner

### From Source
1.  **Set Your API Key**: The miner's API is protected by an API key. Set this key as an environment variable. Choose a strong, secure key.
    ```bash
    export MINER_API_KEY='your_super_secret_and_long_api_key'
    ```

2.  **Run the Miner**: Launch the miner, pointing it to your wallet and the desired netuid.
    ```bash
    python neurons/miner.py \
        --netuid 69 \
        --wallet.name my_miner_wallet \
        --wallet.hotkey default \
        --miner.db_path ./chroma_db
        --logging.debug
    ```

### Using Docker
A Docker container provides a consistent and isolated environment for running the miner.

1.  **Build the Docker Image**:
    ```bash
    docker build . -t cers-miner -f neurons/miners/Dockerfile
    ```

2.  **Run the Docker Container**:
    You must pass the `MINER_API_KEY` environment variable and map the API port. It's also recommended to mount a volume for the ChromaDB database to persist data across container restarts.

    ```bash
    # Create a directory on your host to store the database
    mkdir -p $(pwd)/miner_db

    docker run -d \
        --name cers-miner-container \
        -p 8001:8001 \
        -e MINER_API_KEY="your_super_secret_and_long_api_key" \
        -v $(pwd)/miner_db:/app/chroma_db \
        --gpus all \
        cers-miner \
        python neurons/miner.py \
            --netuid <your_netuid> \
            --wallet.name my_miner_wallet \
            --wallet.hotkey default \
            --miner.db_path /app/chroma_db
    ```
    *   `--gpus all` is required to give the container access to your GPUs.
    *   `-v $(pwd)/miner_db:/app/chroma_db` mounts the local `miner_db` directory into the container where ChromaDB will store its data.
    *   We override `--miner.db_path` to point to the mounted volume inside the container.

## Configuration

The miner can be configured using command-line arguments. Here are some of the key parameters:

| Argument | Default Value | Description |
|---|---|---|
| `--miner.api_port` | `8001` | The port on which the miner's private API will run. |
| `--miner.db_path` | `./chroma_db` | Path to the directory where the ChromaDB vector database will be stored. |
| `--miner.collection_name` | `enterprise-rag` | The name of the collection within ChromaDB. |
| `--miner.documents_file` | `data/documents.csv` | Path to the initial CSV file to populate the database on first run. |
| `--miner.batch_size` | `100` | The number of documents to process in a single batch during initial loading. |
| `--miner.search_k` | `2` | The default number of document IDs to return for a given query. |
| `--neuron.device` | `cuda` if available, else `cpu` | The device to use for the embedding model (`cuda` or `cpu`). |

You can see all available options by running:
```bash
python neurons/miner.py --help
```

## Troubleshooting

-   **API Key Error**: If you see errors related to `401 Unauthorized` when testing the API, ensure the `MINER_API_KEY` environment variable is correctly set in the shell where you are running the miner.
-   **Port Conflict**: If you get an `Address already in use` error, it means another application is using the port specified by `--miner.api_port`. Change the port to an unused one.
-   **CUDA Errors**: If you encounter CUDA-related issues, make sure you have the correct NVIDIA drivers and CUDA Toolkit version installed on your host machine. Verify with `nvidia-smi`.
-   **Database Permissions**: If running locally, ensure you have write permissions for the directory specified by `--miner.db_path`. If using Docker, ensure the volume is mounted correctly.