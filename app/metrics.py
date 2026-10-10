from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "llm_requests_total",
    "Total number of LLM requests",
    ["model", "prompt_version", "status"]
)

LATENCY = Histogram(
    "llm_request_latency_seconds",
    "Time spent waiting for the LLM",
    ["model", "prompt_version"]
)

TOKENS = Counter(
    "llm_tokens_total",
    "Total tokens consumed",
    ["model", "prompt_version", "type"]
)