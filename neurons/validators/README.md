# CERS Subnet Validator

This document provides a comprehensive guide for setting up and running a validator on the Cohere Enterprise RAG Subnet (CERS).

## Introduction

Validators are crucial for maintaining the integrity and performance of the CERS subnet. Their primary role is to act as enterprise proxies, evaluating the quality of the retrieval services provided by miners and distributing TAO rewards accordingly.

The responsibilities of a validator include:
1.  **Generating Queries**: Validators create and send query embeddings to the network of miners. These queries are designed to test the miners' ability to retrieve relevant information from their indexed data.
2.  **Evaluating Miners**: Validators score the responses from miners based on a benchmark dataset. This dataset contains queries with known, ground-truth relevant document IDs. Performance is measured by accuracy metrics like precision, recall, and Mean Reciprocal Rank (MRR).
3.  **Setting Weights**: Based on the performance scores, validators set weights on the Bittensor network. These weights determine how TAO rewards are distributed. High-performing, honest miners receive more rewards, while poor-performing or malicious miners are penalized.

By running a validator, you play a key role in ensuring the subnet provides a high-quality, decentralized retrieval service.

## Hardware Requirements

Validator hardware requirements are generally less intensive than those for miners, but a reliable setup is still essential for consistent operation.

-   **GPU**: **Optional but Recommended**. A GPU is not strictly required for the base validator logic. However, having a GPU can be beneficial for generating query embeddings or running more complex evaluation models locally in the future.
-   **CPU**: A modern multi-core CPU (e.g., 4+ cores).
-   **RAM**: Minimum 16GB.
-   **Storage**: A fast SSD with at least 50GB of free space is sufficient for the operating system and validator state.
-   **Network**: A stable, low-latency internet connection is critical for sending queries and receiving responses from miners in a timely manner.

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
btcli wallet new_coldkey --wallet.name my_validator_wallet
btcli wallet new_hotkey --wallet.name my_validator_wallet --wallet.hotkey default
```

## Running the Validator

### From Source
Launch the validator, pointing it to your wallet and the desired netuid.
```bash
python neurons/validator.py \
    --netuid 69 \
    --wallet.name my_validator_wallet \
    --wallet.hotkey default \
    --logging.debug
```

### Using Docker
A Docker container provides a consistent and isolated environment.

1.  **Build the Docker Image**:
    *You can use the same Dockerfile as the miner, as the environment is identical.*
    ```bash
    docker build . -t cers-validator -f neurons/miners/Dockerfile
    ```

2.  **Run the Docker Container**:
    ```bash
    docker run -d \
        --name cers-validator-container \
        cers-validator \
        python neurons/validator.py \
            --netuid 69 \
            --wallet.name my_validator_wallet \
            --wallet.hotkey default
    ```

## Configuration

The validator can be configured using command-line arguments. Key parameters are related to the wallet, network, and logging. You can see all available options by running:
```bash
python neurons/validator.py --help
```

For more advanced configurations, such as custom scoring scripts or evaluation datasets, refer to the validator's source code.