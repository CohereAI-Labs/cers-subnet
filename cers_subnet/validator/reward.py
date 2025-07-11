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

import torch
import bittensor as bt
from typing import List, Set

def get_rewards(
    self,
    expected_doc_ids: Set[str],
    responses: List[bt.Synapse],
) -> torch.FloatTensor:
    """
    Returns a tensor of rewards for the given query and responses.

    Args:
    - expected_doc_ids (Set[str]): A set of relevant document IDs for the query.
    - responses (List[bt.Synapse]): A list of responses from the miner synapses.

    Returns:
    - torch.FloatTensor: A tensor of rewards for the responses.
    """
    # Get the scores for the responses.
    scores = torch.FloatTensor(
        [
            score_response(response, expected_doc_ids)
            for response in responses
        ]
    ).to(self.device)
    return scores

def score_response(response: bt.Synapse, expected_doc_ids: Set[str]) -> float:
    """
    Scores a single response based on the Mean Reciprocal Rank (MRR) of the returned document IDs.
    The score is 1/rank of the first relevant document found.
    """
    # Penalize responses that are not successful or have no document_ids
    if not response.dendrite.is_success or not response.document_ids:
        return 0.0

    # Find the rank of the first relevant document.
    for i, doc_id in enumerate(response.document_ids):
        if doc_id in expected_doc_ids:
            # Rank is i + 1. MRR score is 1 / rank.
            mrr_score = 1.0 / (i + 1)
            bt.logging.trace(f"Scored response for hotkey {response.axon.hotkey}: {mrr_score} (found relevant doc at rank {i+1})")
            return mrr_score
            
    # No relevant documents found in the response.
    bt.logging.trace(f"Scored response for hotkey {response.axon.hotkey}: 0.0 (no relevant docs found)")
    return 0.0