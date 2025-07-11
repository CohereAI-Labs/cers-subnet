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
from typing import List

def get_rewards(
    self,
    query: str,
    responses: List[bt.Synapse],
) -> torch.FloatTensor:
    """
    Returns a tensor of rewards for the given query and responses.
    
    Args:
    - query (str): The query sent to the miner.
    - responses (List[bt.Synapse]): A list of responses from the miner synapses.
    
    Returns:
    - torch.FloatTensor: A tensor of rewards for the responses.
    """
    # Get the scores for the responses.
    scores = torch.FloatTensor([self.score_response(response) for response in responses]).to(self.device)
    return scores

def score_response(self, response: bt.Synapse) -> float:
    """
    Scores a single response. In this placeholder, we reward based on whether documents were returned.
    This function uses a Cross-Encoder model to score the relevance of the documents.
    A Cross-Encoder is more accurate than a bi-encoder for re-ranking tasks.
    """
    if not response.documents or len(response.documents) == 0:
        return 0.0

    # A Cross-Encoder model expects a list of [query, document] pairs.
    try:
        # Create pairs of [query, document] for the cross-encoder
        model_input = [[response.query, doc] for doc in response.documents]
        
        # Get scores from the cross-encoder model. The output is a numpy array.
        scores = self.cross_encoder_model.predict(model_input)
        
        # The score for the response is the highest score among all returned documents.
        # We convert it to a float.
        return float(max(scores))

    except Exception as e:
        bt.logging.error(f"Error during scoring with cross-encoder: {e}")
        return 0.0