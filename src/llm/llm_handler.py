from typing import Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from config import settings
from src.utils import log


class LLMHandler:
    """Handle LLM interactions using HuggingFace models"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.top_p = settings.LLM_TOP_P
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        log.info(f"Using device: {self.device}")
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the LLM model and tokenizer"""
        try:
            log.info(f"Loading model: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                token=settings.HUGGINGFACE_TOKEN,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                token=settings.HUGGINGFACE_TOKEN,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                do_sample=True,
            )
            
            log.info(f"Successfully loaded model: {self.model_name}")
        
        except Exception as e:
            log.error(f"Error loading model: {str(e)}")
            raise
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate a response from the LLM"""
        try:
            generation_kwargs = {
                "max_new_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
                "top_p": self.top_p,
                "do_sample": True,
            }
            
            response = self.pipe(prompt, **generation_kwargs)
            generated_text = response[0]["generated_text"]
            
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
        
        except Exception as e:
            log.error(f"Error generating response: {str(e)}")
            raise
    
    def format_prompt(self, system_prompt: str, user_message: str, context: str = "") -> str:
        """Format prompt for Llama models"""
        if context:
            full_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}

Context:
{context}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        else:
            full_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return full_prompt
