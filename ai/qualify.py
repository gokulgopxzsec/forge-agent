import json

from search.models import Candidate
from ai.ollama import ask_qwen_json


def qualify_candidate(candidate: Candidate) -> dict:

    evidence_text = json.dumps(
        candidate.evidence,
        indent=2,
        ensure_ascii=False,
    )

    prompt = f"""
Analyze this business for potential relevance to HorseTrace.

HorseTrace is a hose asset management and tagging application
designed for businesses that manage hydraulic or industrial hoses.

BUSINESS

Name:
{candidate.name}

Website:
{candidate.website}

Phone:
{candidate.phone}

City:
{candidate.city}

State:
{candidate.state}

SOURCE:
{candidate.source}

EVIDENCE:
{evidence_text}

Analyze ONLY the evidence above.

Return this exact JSON structure:

{{
    "industry": "",
    "business_type": "",
    "hose_relevance": "low|medium|high",
    "potential_horsetrace_fit": "low|medium|high",
    "reasoning": "",
    "outreach_angle": "",
    "confidence": 0.0
}}

Rules:

1. Do not invent company information.
2. Do not assume a company provides a service unless evidence supports it.
3. If evidence is insufficient, say so.
4. hose_relevance means how strongly the evidence indicates
   the business works with hoses.
5. potential_horsetrace_fit means how relevant the business
   appears to be as a potential HorseTrace prospect.
6. reasoning must reference the evidence.
7. outreach_angle should describe a possible business conversation,
   not claim that the company definitely has a particular problem.
8. confidence must be between 0 and 1.
"""

    return ask_qwen_json(prompt)