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

    # Use the pre-loaded queries from the validator instance.
    if not self.queries:
        bt.logging.error("No queries loaded. Cannot proceed with forward pass.")
        return

    query_text = random.choice(self.queries)

    bt.logging.info(f"Sending query: '{query_text}' to miners: {miner_uids}")

    # The dendrite client queries the network.
    responses = await self.dendrite(
        axons=[self.metagraph.axons[uid] for uid in miner_uids],
        synapse=EnterpriseRAG(query=query_text),
        deserialize=False, # We need the full synapse object for scoring
    )

    rewards = get_rewards(self, query=query_text, responses=responses)

    bt.logging.info(f"Scored responses: {rewards}")
    self.update_scores(rewards, miner_uids)