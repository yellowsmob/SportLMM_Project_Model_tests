# llm_client.py
"""
LLM Client - Handles communication with Language Models
Local LLM (LM Studio) support
"""

import requests
import time
from typing import Optional
from config import (
    USE_LOCAL_LLM,
    LOCAL_LLM_ENDPOINT,
    LOCAL_LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    MAX_RETRIES,
    REQUEST_TIMEOUT
)


class LLMClient:
    """Base LLM Client for local LM Studio"""
    
    def __init__(
        self,
        use_local: bool = USE_LOCAL_LLM,
        local_endpoint: str = LOCAL_LLM_ENDPOINT,
        local_model: str = LOCAL_LLM_MODEL,
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS
    ):
        self.use_local = use_local
        self.local_endpoint = local_endpoint
        self.local_model = local_model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using LLM"""
        return self._generate_local(prompt, system_prompt)
    
    def _generate_local(self, prompt: str, system_prompt: Optional[str]) -> str:
        """Generate using local LM Studio"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(
                    f"{self.local_endpoint}/chat/completions",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": self.local_model,
                        "messages": messages,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "stream": False
                    },
                    timeout=REQUEST_TIMEOUT
                )
                
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except requests.exceptions.ConnectionError:
                print("Erreur: Impossible de se connecter à LM Studio")
                print(f"Vérifiez que LM Studio est lancé sur {self.local_endpoint}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2)
                else:
                    return ""
                    
            except Exception as e:
                print(f" Erreur LLM: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2)
                else:
                    return ""
        
        return ""


class FrenchLLMClient(LLMClient):
    """LLM client optimized for French language"""
    
    def __init__(self, use_local: bool = USE_LOCAL_LLM, **kwargs):
        super().__init__(use_local=use_local, **kwargs)
        
        self.french_system_context = """Tu es un assistant expert en analyse de données équestres.
Tu réponds toujours en français, de manière claire et précise.
Tu utilises une ontologie RDF pour interroger une base de connaissances sur les chevaux, cavaliers, et entraînements."""
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate with French context"""
        if system_prompt:
            combined_system = f"{self.french_system_context}\n\n{system_prompt}"
        else:
            combined_system = self.french_system_context
        
        return super().generate(prompt, combined_system)


if __name__ == "__main__":
    print("Test de connexion au LLM...")
    
    client = FrenchLLMClient()
    response = client.generate("Dis bonjour en français")
    
    if response:
        print(f"Réponse: {response}")
        print("LLM fonctionne correctement!")
    else:
        print("Pas de réponse du LLM")
