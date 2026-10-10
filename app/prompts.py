PROMPTs = {
    "v1" : " You are a helpful assistant. Answer Clearly.",
    "v2" : "You are an expert assistant. Answer in at most three sentences, using simple words.",
}

DEFAULT_VERSION = "v2"

def get_prompt(version: str) -> str:
    if version not in PROMPTs:
        raise ValueError(f"Unknown prompt version: {version}")
    return PROMPTs[version]