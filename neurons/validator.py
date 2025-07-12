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
import os
import sys
import torch

# Bittensor
import bittensor as bt

# import base validator class which takes care of most of the boilerplate
from cers_subnet.base.validator import BaseValidatorNeuron

# Bittensor Validator Template:
from cers_subnet.validator import forward
from sentence_transformers import CrossEncoder


class Validator(BaseValidatorNeuron):
    """
    Your validator neuron class. You should use this class to define your validator's behavior. In particular, you should replace the forward function with your own logic.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()

        bt.logging.info("Validator for Cohere Enterprise RAG Subnet initialized.")

        # Explicitly set the device to use for the model
        self.device = self.config.get("neuron.device", "cuda" if torch.cuda.is_available() else "cpu")
        bt.logging.info(f"Using device: {self.device}")

        # Load the scoring model from configuration
        model_name = self.config.get('validator.cross_encoder_model', 'cross-encoder/ms-marco-MiniLM-L-6-v2')
        try:
            self.cross_encoder_model = CrossEncoder(model_name, device=self.device)
            bt.logging.info(f"Cross Encoder model '{model_name}' loaded successfully on {self.device}.")
        except Exception as e:
            bt.logging.error(f"Failed to load Cross Encoder model '{model_name}'. Error: {e}")
            bt.logging.error("Please ensure the model name is correct and you have an internet connection if it needs to be downloaded.")
            sys.exit(1) # Exit if the model can't be loaded, as it's essential for scoring.
        
        # Load queries from a file to make them easily configurable
        self.queries = self.load_queries()
        if not self.queries:
            bt.logging.error("No queries loaded. The validator requires queries to function.")
            sys.exit(1)

    def load_queries(self) -> list[str]:
        """Loads queries from the data/queries.txt file."""
        queries_file = self.config.get('validator.queries_file', 'data/queries.txt')
        queries_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            queries_file
        )
        queries = []
        try:
            with open(queries_path, "r", encoding="utf-8") as f:
                queries = [line.strip() for line in f if line.strip()]
            if queries:
                bt.logging.info(f"Loaded {len(queries)} queries from {queries_path}")
            else:
                bt.logging.warning(f"Queries file at {queries_path} is empty.")

        except FileNotFoundError:
            bt.logging.warning(f"Queries file not found at {queries_path}. Using default queries.")
        
        # If loading failed or the file was empty, use a default list
        if not queries:
            queries = [
                "What is Bittensor?", "How does Cohere's RAG work?", 
                "Explain the concept of a decentralized AI network.", "What is the capital of France?"
            ]
            bt.logging.info(f"Using {len(queries)} default queries.")
        
        return queries

    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        # TODO(developer): Rewrite this function based on your protocol definition.
        return await forward(self)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info(f"Validator running... {time.time()}")
            time.sleep(5)
