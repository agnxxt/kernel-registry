import asyncio
import os
from typing import Dict, Any, List

# Optional import for prod
try:
    import litellm
except ImportError:
    litellm = None

class CognitiveModelRunner:
    """
    The inference engine of the kernel.
    Utilizes LiteLLM for multi-cloud, multi-provider abstraction.
    Handles dynamic routing and prompt injection.
    """
    def __init__(self):
        pass

    async def invoke_model(self, request_payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a cognitive inference request via LiteLLM.
        """
        model_path = f"{request_payload.get('provider', 'openai')}/{request_payload.get('model', 'gpt-4o')}"
        
        system_prompt = self._build_governed_prompt(context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(request_payload.get("input", "Compute action"))}
        ]

        if litellm and not os.getenv("MOCK_INFERENCE", "true").lower() == "true":
            try:
                response = await litellm.acompletion(model=model_path, messages=messages)
                return {
                    "model_output": response.choices[0].message.content,
                    "runner": "LiteLLM",
                    "usage": dict(response.usage),
                    "system_prompt_applied": system_prompt[:100] + "..."
                }
            except Exception as e:
                # Log error and fallback
                pass
        
        # Fallback if litellm is not installed or we hit an error, but in a real prod env
        # MOCK_INFERENCE=false would fail. For scaffolding to work, we simulate.
        if os.getenv("MOCK_INFERENCE", "true").lower() == "false":
            raise RuntimeError(f"LiteLLM missing or invocation failed for {model_path} in production mode.")

        await asyncio.sleep(0.1)
        return {
            "model_output": f"Simulated routing success for {model_path}. Please set MOCK_INFERENCE=false to use litellm.",
            "runner": "MockRunner",
            "usage": {"prompt_tokens": 150, "completion_tokens": 45},
            "system_prompt_applied": system_prompt[:100] + "..."
        }

    def _build_governed_prompt(self, context: Dict[str, Any]) -> str:
        """
        Injects Deontic Constraints and Spiritual Axioms into the LLM system prompt.
        """
        base = "You are a governed Agent within the Kernel ecosystem."
        constraints = "\nDEONTIC GUARDRAILS:\n- Do not access unauthorized payroll data.\n- Prioritize life-safety axioms."
        context_str = f"\nCURRENT CONTEXT:\n- Weather: {context.get('weather')}\n- Trust Score: {context.get('trust_score')}"
        
        return f"{base}{constraints}{context_str}"
