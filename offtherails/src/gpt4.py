from typing import (
    Any,
    Dict,
    List, 
)

import asyncio

import logging 

logging.basicConfig(level=logging.INFO)


# The cost per token for each model input.
MODEL_COST_PER_INPUT = {
    'gpt-4': 3e-05,
}
# The cost per token for each model output.
MODEL_COST_PER_OUTPUT = {
    'gpt-4': 6e-05,
}


class GPT4Agent():
    """
    GPT-4 Wrapper.
    """
    def __init__(
        self, 
        llm: Any,
        **completion_config,
    ) -> None:
        self.llm = llm
        self.completion_config = completion_config
        self.all_responses = []
        self.total_inference_cost = 0

    def calc_cost(
        self, 
        response
    ) -> float:
        """
        Args:
            response (openai.ChatCompletion): The response from the API.

        Returns:
            float: The cost of the response.
        """
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = (
            MODEL_COST_PER_INPUT['gpt-4'] * input_tokens
            + MODEL_COST_PER_OUTPUT['gpt-4'] * output_tokens
        )
        return cost
    
    async def get_response(
        self, 
        messages: List[Dict[str, str]],
    ) -> Any:
        """Get the response from the model."""
        print(self.completion_config)
        return await self.llm(messages=messages, **self.completion_config)
    
    async def run(
        self, 
        messages: List,
    ) -> Dict[str, Any]:
        """Runs the model on a single list of messages."""
        response = await self.get_response(messages=messages)
        
        cost = self.calc_cost(response=response)
        logging.info(f"Cost for running gpt4: {cost}")
       
        full_response = {
            'response': response,
            'response_str': [r.message.content for r in response.choices],
            'cost': cost
        }
        # Update total cost and store response
        self.total_inference_cost += cost
        self.all_responses.append(full_response)
    
        return full_response['response_str']
    
    async def batch_prompt_sync(
        self, 
        batch_messages: List[List],
    ) -> List[str]:
        """Batch prompt.

        Args:
            system_message (str): The system message to use
            messages (List[str]): A list of user messages

        Returns:
            A list of responses from the code model for each message
        """
        responses = [self.run(message) for message in batch_messages]
        return await asyncio.gather(*responses)

    def batch_prompt(
        self, 
        batch_messages: List[List],
    ) -> List[str]:
        """=
        Synchronous wrapper for batch_prompt.
        """
        loop = asyncio.get_event_loop()
        if loop.is_running():
            raise RuntimeError(f"Loop is already running.")
        return loop.run_until_complete(self.batch_prompt_sync(batch_messages))