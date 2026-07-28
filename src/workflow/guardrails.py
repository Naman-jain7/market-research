import json
import re
from urllib.parse import urlparse

from src.workflow.state import AgentOutput, Citation


PROMPT_INJECTION_PATTERNS = (
    r"\b(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|system|developer)\s+instructions?\b",
    r"\breveal\s+(?:the\s+)?system\s+prompt\b",
    r"\breturn\s+hidden\s+credentials?\b",
    r"\bexfiltrate\s+secrets?\b",
)


def sanitize_input(text: str) -> str:
    """
    Sanitize PII and sensitive patterns from user input to prevent prompt injection 
    and data leakage.
    """
    if not text:
        return text
    
    # Redact Emails
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[REDACTED_EMAIL]', text)
    
    # Redact Credit Cards (basic 13-16 digit matching)
    text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[REDACTED_CREDIT_CARD]', text)
    
    # Redact potential API keys (heuristic: 32+ alphanumeric characters)
    text = re.sub(r'\b[A-Za-z0-9_-]{32,}\b', '[REDACTED_API_KEY]', text)

    # Neutralize common prompt-injection directives without rejecting benign input.
    for pattern in PROMPT_INJECTION_PATTERNS:
        text = re.sub(pattern, "[REDACTED_PROMPT_INJECTION]", text, flags=re.IGNORECASE)
    
    return text


def _is_valid_http_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _validate_sources(sources: list) -> list[Citation]:
    """Validate and clean a list of source citations."""
    validated: list[Citation] = []
    for s in sources:
        if isinstance(s, Citation):
            if _is_valid_http_url(s.url):
                validated.append(s)
        elif isinstance(s, dict):
            url = s.get("url", "")
            title = s.get("title", "")
            if isinstance(url, str) and _is_valid_http_url(url):
                validated.append(Citation(title=title, url=url))
        elif isinstance(s, str) and _is_valid_http_url(s):
            validated.append(Citation(url=s))
    return validated

def _extract_sources_from_text(text: str) -> list[Citation]:
    """Try to extract sources/citations from unstructured text."""
    sources: list[Citation] = []

    # Try to find a JSON array of sources embedded in the text
    decoder = json.JSONDecoder()
    for start in (match.start() for match in re.finditer(r"\[", text)):
        try:
            parsed, _ = decoder.raw_decode(text[start:])
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(parsed, list):
            validated = _validate_sources(parsed)
            if validated:
                return validated

    # Fallback: extract markdown links [title](url)
    md_links = re.findall(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', text)
    for title, url in md_links:
        if _is_valid_http_url(url):
            sources.append(Citation(title=title, url=url))

    # Fallback: extract bare URLs
    urls = re.findall(r'https?://[^\s\)\]>\"\']+', text)
    existing_urls = {s.url for s in sources}
    for url in urls:
        if url not in existing_urls and _is_valid_http_url(url):
            sources.append(Citation(url=url))
            existing_urls.add(url)

    return sources

def validate_agent_output(output) -> AgentOutput:
    """
    Validate and extract agent output ensuring it strictly follows the AgentOutput schema.
    If it fails, fall back to a default score.
    """
    score = None
    text = str(output)
    sources: list[Citation] = []
    
    # Try parsing from CrewAI's output_pydantic if it exists
    if hasattr(output, 'pydantic') and output.pydantic:
        parsed = output.pydantic
        text = getattr(parsed, 'text', text)
        score = getattr(parsed, 'score', None)
        raw_sources = getattr(parsed, 'sources', None)
        if raw_sources:
            sources = _validate_sources(raw_sources)
    
    # Fallback: Extract via regex
    if score is None:
        match = re.search(r'(?:[Ss]core(?:\s*field)?[:\s\*\*]+)(\d+(?:\.\d+)?)', text)
        if match:
            try:
                score = float(match.group(1))
            except ValueError:
                pass

    # Extract sources from text if pydantic didn't provide them
    if not sources:
        sources = _extract_sources_from_text(text)
                
    # Validation and default fallback
    if score is None or not (0.0 <= score <= 10.0):
        score = 5.0
        
    return AgentOutput(text=text, score=score, sources=sources)
