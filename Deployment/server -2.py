import litserve as ls
from vllm import LLM
from vllm.sampling_params import SamplingParams
from vllm.entrypoints.chat_utils import ChatCompletionMessageParam
from litserve.specs.openai import ChatMessage, OpenAISpec
from typing import List, Dict, Any, Generator


class VLLMLitAPI(ls.LitAPI):
    def setup(self, device: str):
        model_name = "rishabh9559/medical-llama-3.2-3B"

        self.llm = LLM(
            model=model_name,
            trust_remote_code=True,
            max_model_len=4096,
            gpu_memory_utilization=0.9,
            dtype="auto",
        )

    def decode_request(
        self, request: Dict[str, Any]
    ) -> List[ChatCompletionMessageParam]:
        return request["messages"]

    def predict(self, messages: List[ChatCompletionMessageParam]) -> Generator[str, None, None]:
        sampling_params = SamplingParams(
            temperature=0.2,
            max_tokens=512,
        )

        try:
            # For non-streaming (simpler)
            outputs = self.llm.chat(
                messages=messages,
                sampling_params=sampling_params,
            )
            
            if outputs and outputs[0].outputs:
                yield outputs[0].outputs[0].text
            else:
                yield ""
                
        except Exception as e:
            yield f"Error generating response: {str(e)}"

    def encode_response(self, output_generator: Generator[str, None, None]) -> Generator[ChatMessage, None, None]:
        for text in output_generator:
            yield ChatMessage(role="assistant", content=text)


if __name__ == "__main__":
    api = VLLMLitAPI(spec=OpenAISpec())
    server = ls.LitServer(
        api,
        accelerator="auto",
    )
    server.run(port=8000)