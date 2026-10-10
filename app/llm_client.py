import json
import logging 
import time

from groq import Groq

from app.config import settings
from app.metrics import LATENCY, REQUEST_COUNT, TOKENS
from app.prompts import get_prompt

logger = logging.getLogger("llmops")
client = Groq(api_key=settings.groq_api_key)

def ask_llm(question: str, prompt_version:str) -> dict:
    system_prompt = get_prompt(prompt_version)
    start = time.perf_counter()
    
    try:
        response = client.chat.completions.create(
            model = settings.model_name,
            max_tokens = settings.max_tokens,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )
    except Exception: 
        REQUEST_COUNT.labels(settings.model_name, prompt_version,"error").inc()
        logger.exception("LLM call Failed")
        raise
    
    latency = time.perf_counter() - start
    usage = response.usage
    
    LATENCY.labels(settings.model_name, prompt_version).observe(latency)
    REQUEST_COUNT.labels(settings.model_name, prompt_version, "success").inc()
    TOKENS.labels(settings.model_name, prompt_version, "prompt").inc(usage.prompt_tokens)
    TOKENS.labels(settings.model_name, prompt_version, "completion").inc(usage.completion_tokens)   

    result = {
        "answer" : response.choices[0].message.content,
        "model" : settings.model_name,
        "prompt_version" : prompt_version,
        "latency" : round(latency,3),
        "prompt_tokens" : usage.prompt_tokens,
        "completion_tokens" : usage.completion_tokens,
    }
    logger.info(json.dumps(result))
    return result