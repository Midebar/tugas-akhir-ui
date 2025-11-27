class LlamaCPPBackend:
    def __init__(self, local_model_path: str):
        """
        local_model_path: Must point to a specific .gguf FILE, not just a directory.
        """
        if not LLAMACPP_AVAILABLE: raise ImportError("llama-cpp-python not installed. Run 'pip install llama-cpp-python'")
        
        # n_gpu_layers=-1 means offload ALL layers to GPU
        self.llm = Llama(
            model_path=local_model_path, 
            n_ctx=0,
            n_gpu_layers=-1, 
            verbose=False
        )

    def generate(self, prompt: str, max_new_tokens: int = 512, temperature: float = 0.0, **kwargs) -> str:
        output = self.llm(
            prompt,
            max_tokens=max_new_tokens,
            stop=[],
            echo=True, # Return prompt + completion to match others
            temperature=temperature
        )
        return output['choices'][0]['text']