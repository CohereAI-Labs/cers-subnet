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
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT of OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import bittensor as bt
import random

from cers_subnet.protocol import EnterpriseRAG
from cers_subnet.validator.reward import get_rewards
from cers_subnet.utils.uids import get_random_uids


async def forward(self):
    """
    The forward pass queries the network and scores the responses.
    """

    miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)

    # The validator should have a benchmark dataset of queries and their expected results.
    # This should be loaded in the validator's __init__ method.
    if not self.benchmark_dataset:
        bt.logging.error("No benchmark dataset loaded. Cannot proceed with forward pass.")
        return

    # Select a random query and its ground truth from the dataset
    benchmark_item = random.choice(self.benchmark_dataset)
    query_text = benchmark_item['query']
    expected_doc_ids = set(benchmark_item['relevant_docs']) # Use a set for efficient lookups

    bt.logging.info(f"Sending query: '{query_text}' to miners: {miner_uids}")
    bt.logging.info(f"Expected document IDs: {expected_doc_ids}")

    # The dendrite client queries the network.
    responses = await self.dendrite(
        axons=[self.metagraph.axons[uid] for uid in miner_uids],
        synapse=EnterpriseRAG(query=query_text),
        deserialize=False, # We need the full synapse object for scoring
        timeout=self.config.neuron.timeout, # Add a timeout for robustness
    )

    # The reward function now needs the expected IDs to score responses.
    rewards = get_rewards(self, expected_doc_ids=expected_doc_ids, responses=responses)

    bt.logging.info(f"Scored responses: {rewards}")
    self.update_scores(rewards, miner_uids)