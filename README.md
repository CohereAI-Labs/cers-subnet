<div align="center">

# **Cohere Enterprise RAG Subnet** <!-- omit in toc -->
[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor) <!-- TODO: Update with the project's Discord if applicable -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

## The Incentivized Internet <!-- omit in toc -->

[Discord](https://discord.gg/bittensor) • [@cohere](https://x.com/cohere) • [Website](https://www.cohere.com)
</div>

---
- [Introduction](#introduction)
  - [Subnet Concept](#subnet-concept)
  - [Strategic Partnership](#strategic-partnership)
- [How it works on Bittensor](#how-it-works-on-bittensor)
- [🔒 Security and Data Privacy](#-security-and-data-privacy)
  - [Architecture Overview](#architecture-overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Clone \& Install](#1-clone--install)
  - [2. Configure Your Wallet](#2-configure-your-wallet)
  - [3. Run the Subnet](#3-run-the-subnet)
    - [For Miners](#for-miners)
- [License](#license)

---
## Introduction

The **Cohere Enterprise RAG Subnet** is a decentralized network on Bittensor, designed to enhance Retrieval Augmented Generation (RAG) systems for Cohere's enterprise clients.

### Subnet Concept

This subnet specializes in optimizing RAG pipelines. Miners on the network contribute in several ways:
- **Specific Knowledge Indexing**: They store and index embeddings derived from private, company-specific knowledge bases to enable highly accurate and secure searches. Miners never have access to the raw document content.
- **Retrieval Algorithm Optimization**: They develop and run information retrieval algorithms optimized for specific domains.
- **Secure Retrieval**: They return document IDs corresponding to the most relevant information, which the enterprise can then use to retrieve the actual content from its own secure datastores.

### Strategic Partnership

As a leader in enterprise AI solutions, Cohere uses this subnet to offer its clients enhanced customization and performance for their language models on proprietary data. This partnership allows companies to benefit from a decentralized, robust, and secure RAG infrastructure without having to manage it in-house.

---

## How it works on Bittensor

The Bittensor blockchain hosts multiple self-contained incentive mechanisms called **subnets**. Subnets are playing fields in which:
- Subnet miners who produce value, and
- Subnet validators who produce consensus

determine together the proper distribution of TAO for the purpose of incentivizing the creation of value, i.e., generating digital commodities, such as intelligence or data. 

Each subnet consists of:
- Subnet miners and subnet validators.
- A protocol using which the subnet miners and subnet validators interact with one another. This protocol is part of the incentive mechanism.
- The Bittensor API using which the subnet miners and subnet validators interact with Bittensor's onchain consensus engine [Yuma Consensus](https://bittensor.com/documentation/validating/yuma-consensus). The Yuma Consensus is designed to drive these actors: subnet validators and subnet miners, into agreement on who is creating value and what that value is worth. 


---

## 🔒 Security and Data Privacy

In an enterprise context, data privacy is paramount. This subnet is designed with a **privacy-first architecture** where sensitive enterprise data is never exposed to the public network or the miners.

### Architecture Overview

The following diagram illustrates the data flow and the separation of concerns between the enterprise environment and the Bittensor network, ensuring that raw data never leaves the enterprise's secure perimeter.

```mermaid
graph TD
    subgraph "Enterprise Secure Environment"
        User((User)) -- "Asks a question" --> RAGApp["RAG Application"]
        RAGApp -- "Sends query to Validator" --> Validator
        Validator -- "Returns Document IDs" --> RAGApp
        RAGApp -- "Retrieves documents by ID" --> SecureDB[("Secure Datastore")]
        SecureDB -- "Document content" --> RAGApp
        RAGApp -- "Generates final response" --> User
        RawDocs[("Raw Documents")] --> EmbedGen["Embedding Generation"]
        EmbedGen -- "Indexing:<br>Embeddings + Doc IDs" --> Miner
    end

    subgraph "Bittensor Network (CERS Subnet)"
        Validator["Validator"] -- "Sends query embedding" --> Miner["Miner<br>(Vector Index)"]
        Miner -- "Returns relevant Document IDs" --> Validator
    end

    style SecureDB fill:#f9f,stroke:#333,stroke-width:2px
    style RawDocs fill:#f9f,stroke:#333,stroke-width:2px
```

Here’s how it works:
1.  **Data Stays On-Premise**: The enterprise's raw documents (the knowledge base) remain within their secure environment.
2.  **Embeddings, Not Data**: The enterprise generates numerical representations (embeddings) of their documents. Only these non-reversible embeddings, along with anonymous document IDs, are sent to the miners for indexing.
3.  **Miner's Role**: Miners store and maintain a searchable index of these embeddings. They perform similarity searches based on query embeddings provided by validators. **Miners never see the original document content.**
4.  **Secure Retrieval**: When a miner finds relevant results, it returns only the corresponding document IDs to the validator.
5.  **Final-Mile RAG**: The enterprise uses these IDs to retrieve the full document text from its own secure database to complete the RAG process.

This model ensures that companies can leverage the decentralized power of the Bittensor network for high-performance retrieval without ever compromising the confidentiality of their proprietary data.

---
## Getting Started

This guide provides the essential steps to get the Cohere Enterprise RAG Subnet up and running.

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or later
- `pip` and `venv`

You also need to have `bittensor` installed. If you haven't installed it yet, follow the instructions here.

### 1. Clone & Install

First, clone the repository and navigate into the directory:
```bash
git clone https://github.com/CohereAI-Labs/cers-subnet.git
cd cers-subnet
```

Next, set up a virtual environment and install the necessary dependencies. Using a virtual environment is highly recommended.
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install the package in editable mode
pip install -e .
```

### 2. Configure Your Wallet

To interact with the Bittensor network, you need a wallet with a coldkey and a hotkey.
If you don't have one, create it using the Bittensor CLI (`btcli`):
```bash
# Create a new coldkey
btcli wallet new_coldkey --wallet.name my_wallet

# Create a new hotkey for your wallet
btcli wallet new_hotkey --wallet.name my_wallet --wallet.hotkey default
```

### 3. Run the Subnet

You can participate in the subnet as either a miner or a validator.

#### For Miners

To run a miner, use the following command:
```bash
python neurons/miner.py --netuid <your-netuid> --wallet.name my_wallet --wallet.hotkey default --logging.debug --miner.api_key <your_secure_api_key>
```

**To run a validator:**
```bash
python neurons/validator.py --netuid <your-netuid> --wallet.name my_wallet --wallet.hotkey default --logging.debug
```
> **Note**: Replace `<your-netuid>` with the actual `netuid` of the subnet you wish to connect to.

For more detailed instructions, including how to register your keys and run on different networks (local, testnet, mainnet), please refer to our full documentation:
- Running Subnet Locally
- Running on the Test Network
- Running on the Main Network


## License
This repository is licensed under the MIT License.
```text
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
```
