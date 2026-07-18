# import math
# import os
import re
from .analysis_data import ROLE_CATALOG,SECTION_RULES,SKILL_ONTOLOGY
import streamlit as st

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#./-]{1,}")
WORD_BOUNDARY_TEMPLATE = r"(?<![a-z0-9]){}(?![a-z0-9])"

def normalize_text(text):
    return re.sub(r"\s+"," ",(text or "")).strip()

def normalize_token(text):
    return re.sub(r"[^a-z0-9+#]+"," ",(text or "").lower()).strip()

def extract_keywords(text):
    tokens=[tokens.lower() for token in TOKEN_PATTERN.findall(text or "")]
    stopwords = {
        "with", "that", "this", "from", "into", "have", "your", "will", "they",
        "their", "about", "using", "used", "build", "role", "team", "work",
        "years", "year", "must", "should", "good", "strong", "ability", "skills",
        "experience", "knowledge", "and", "the", "for", "are", "you", "our"
    }
    filtered=[token for token in tokens if token not in stopwords and len(token)>2]
    return list(dict.fromkeys(filtered))

def build_skill_alias_map():
    alias_map={}
    canonical_to_meta={}
    for entry in SKILL_ONTOLOGY:
        canonical=entry["name"]
        canonical_to_meta[canonical]=entry
        for alias in [canonical,*entry.get("aliases",[])]:
            alias_map[normalize_token(alias)]=canonical
    return alias_map,canonical_to_meta

SKILL_ALIAS_MAP, SKILL_META = build_skill_alias_map()

def canonicalize_skill(skill):
    normalized = normalize_token(skill)
    return SKILL_ALIAS_MAP.get(
        normalized,
        skill.strip() if isinstance(skill, str) else skill
    )



def canonicalize_skills(skills):
    canonical = []
    seen = set()

    for skill in skills or []:
        value = canonicalize_skill(skill)
        normalized = normalize_token(value)
        if normalized and normalized not in seen:
            seen.add(normalized)
            canonical.append(value)

    return canonical


def extract_resume_evidence(resume_text,parsed_skills):
    lowered=f"{normalize_text(resume_text).lower()}"
    evidence={}

    for skill in canonicalize_skills(parsed_skills):
        evidence[skill]={
            "skill":skill,
            "source":"parser",
            "mentions":1,
            "category":SKILL_META.get(skill, {}).get("category", "Skills"),
        }
    for entry in SKILL_ONTOLOGY:
        canonical=entry["name"]
        matched_aliases=[]
        seen_aliases=set()
        unique_aliases=[]

        for alias in [canonical,*entry.get("aliases",[])]:
            alias_key=normalize_token(alias)
            if alias_key and alias_key not in seen_aliases:
                seen_aliases.add(alias_key)
                unique_aliases.append(alias)
        for alias in unique_aliases:
            pattern=WORD_BOUNDARY_TEMPLATE.format(re.escape(alias.lower()))
            if re.search(pattern,lowered):
                matched_aliases.append(alias)
        if matched_aliases:
            current = evidence.get(
                canonical,
                {
                    "skill": canonical,
                    "source": "resume_text",
                    "mentions": 0,
                    "category": entry["category"],
                }
            )
            current["mentions"] += len(matched_aliases)
            current["matched_aliases"] = sorted(
                set(
                    current.get("matched_aliases", [])
                    + matched_aliases
                )
            )

            if current.get("source") == "parser":
                current["source"] = "parser+resume_text"

            evidence[canonical] = current

    return dict(
        sorted(
            evidence.items(),
            key=lambda item: (
                -item[1]["mentions"],
                item[0].lower()
            )
        )
    )
result = extract_resume_evidence(
    "Built APIs with FastAPI and PostgreSQL",
    ["FastAPI", "Postgres", "FastAPI"],
)
print(result)




