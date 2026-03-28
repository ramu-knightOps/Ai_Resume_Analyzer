import math
import os
import re
from collections import Counter

from analysis_data import ROLE_CATALOG, SECTION_RULES, SKILL_ONTOLOGY

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.\-/]{1,}")
WORD_BOUNDARY_TEMPLATE = r"(?<![a-z0-9]){}(?![a-z0-9])"

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None


def normalize_text(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def normalize_token(text):
    return re.sub(r"[^a-z0-9+#]+", " ", (text or "").lower()).strip()


def extract_keywords(text):
    tokens = [token.lower() for token in TOKEN_PATTERN.findall(text or "")]
    stopwords = {
        "with", "that", "this", "from", "into", "have", "your", "will", "they",
        "their", "about", "using", "used", "build", "role", "team", "work",
        "years", "year", "must", "should", "good", "strong", "ability", "skills",
        "experience", "knowledge", "and", "the", "for", "are", "you", "our"
    }
    filtered = [token for token in tokens if token not in stopwords and len(token) > 2]
    return list(dict.fromkeys(filtered))


def _build_skill_alias_map():
    alias_map = {}
    canonical_to_meta = {}
    for entry in SKILL_ONTOLOGY:
        canonical = entry["name"]
        canonical_to_meta[canonical] = entry
        for alias in [canonical, *entry.get("aliases", [])]:
            alias_map[normalize_token(alias)] = canonical
    return alias_map, canonical_to_meta


SKILL_ALIAS_MAP, SKILL_META = _build_skill_alias_map()


def canonicalize_skill(skill):
    normalized = normalize_token(skill)
    return SKILL_ALIAS_MAP.get(normalized, skill.strip() if isinstance(skill, str) else skill)


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


def extract_resume_evidence(resume_text, parsed_skills):
    lowered = f" {normalize_text(resume_text).lower()} "
    evidence = {}

    for skill in canonicalize_skills(parsed_skills):
        evidence[skill] = {
            "skill": skill,
            "source": "parser",
            "mentions": 1,
            "category": SKILL_META.get(skill, {}).get("category", "Skills"),
        }

    for entry in SKILL_ONTOLOGY:
        canonical = entry["name"]
        aliases = [canonical, *entry.get("aliases", [])]
        matched_aliases = []
        for alias in aliases:
            pattern = WORD_BOUNDARY_TEMPLATE.format(re.escape(alias.lower()))
            if re.search(pattern, lowered):
                matched_aliases.append(alias)

        if matched_aliases:
            current = evidence.get(canonical, {
                "skill": canonical,
                "source": "resume_text",
                "mentions": 0,
                "category": entry["category"],
            })
            current["mentions"] += len(matched_aliases)
            current["matched_aliases"] = sorted(set(current.get("matched_aliases", []) + matched_aliases))
            if current.get("source") == "parser":
                current["source"] = "parser+resume_text"
            evidence[canonical] = current

    return dict(sorted(evidence.items(), key=lambda item: (-item[1]["mentions"], item[0].lower())))


def infer_candidate_level(page_count, resume_text):
    lowered = (resume_text or "").lower()
    if page_count < 1:
        return "NA"
    year_matches = [int(match) for match in re.findall(r"\b(\d{1,2})\+?\s+years?\b", lowered)]
    max_years = max(year_matches) if year_matches else 0
    project_hits = len(re.findall(r"\b(project|projects)\b", lowered))
    internship_hits = len(re.findall(r"\b(internship|internships|intern)\b", lowered))
    experience_hits = len(re.findall(r"\b(experience|employment|work experience)\b", lowered))

    if max_years >= 4 or experience_hits or (experience_hits and project_hits >= 2):
        return "Experienced"
    if max_years >= 1 or internship_hits or project_hits >= 2:
        return "Intermediate"
    return "Fresher"


def evaluate_resume_score(resume_text):
    lowered = (resume_text or "").lower()
    score = 0
    checks = []
    for rule in SECTION_RULES:
        matched = any(re.search(WORD_BOUNDARY_TEMPLATE.format(re.escape(pattern)), lowered) for pattern in rule["patterns"])
        if matched:
            score += rule["weight"]
        elif rule["label"] in {"Experience", "Projects"}:
            bullet_hits = len(re.findall(r"^\s*[\-\*\u2022\u25cf]", resume_text or "", re.MULTILINE))
            if bullet_hits >= 2:
                matched = True
                score += max(3, rule["weight"] // 2)
        checks.append({
            "label": rule["label"],
            "matched": matched,
            "success": rule["success"],
            "warning": rule["warning"],
            "weight": rule["weight"],
        })

    metric_mentions = len(re.findall(r"\b\d+%|\b\d+\+|\$\d+|\b\d+\s*(users|customers|clients|ms|sprint|months?)\b", lowered))
    bullet_lines = len(re.findall(r"^\s*[\-\*\u2022\u25cf]", resume_text or "", re.MULTILINE))
    section_headings = len([check for check in checks if check["matched"]])

    quality_bonus = 0
    if metric_mentions >= 2:
        quality_bonus += 8
    elif metric_mentions == 1:
        quality_bonus += 4
    if bullet_lines >= 4:
        quality_bonus += 8
    elif bullet_lines >= 2:
        quality_bonus += 3
    if section_headings >= 5:
        quality_bonus += 4

    return min(score + quality_bonus, 100), checks


def infer_role_from_skills(skills, resume_text=""):
    resume_evidence = extract_resume_evidence(resume_text, skills)
    normalized_skills = {skill.lower() for skill in resume_evidence.keys()}
    best_role = None
    best_overlap = 0.0
    best_missing = []

    for role in ROLE_CATALOG:
        role_keywords = {canonicalize_skill(keyword).lower() for keyword in role["keywords"]}
        overlap_terms = normalized_skills.intersection(role_keywords)
        overlap = len(overlap_terms)
        if overlap and resume_text:
            resume_text_lower = (resume_text or "").lower()
            summary_hits = sum(1 for keyword in role["keywords"] if keyword.lower() in resume_text_lower)
            overlap += min(summary_hits * 0.15, 1.2)
        if overlap > best_overlap:
            best_overlap = overlap
            best_role = role
            best_missing = [
                canonicalize_skill(keyword)
                for keyword in role["keywords"]
                if canonicalize_skill(keyword).lower() not in normalized_skills
            ]

    if best_role:
        return {
            "title": best_role["title"],
            "field": best_role["field"],
            "recommended_skills": best_missing[:6] + [
                skill for skill in best_role["recommended_skills"] if skill not in best_missing[:6]
            ],
            "courses_key": best_role["courses_key"],
            "match_reason": f"Detected {int(best_overlap)} aligned role signals from parser and resume evidence.",
        }

    fallback_role = ROLE_CATALOG[0]
    return {
        "title": fallback_role["title"],
        "field": "General",
        "recommended_skills": fallback_role["recommended_skills"],
        "courses_key": fallback_role["courses_key"],
        "match_reason": "Using a general fallback because the resume skills were sparse.",
    }


def _cache_resource(func):
    if st is None:
        return func
    return st.cache_resource(show_spinner=False)(func)


@_cache_resource
def load_embedding_model():
    from sentence_transformers import SentenceTransformer

    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token
        os.environ["HF_TOKEN"] = hf_token
        return SentenceTransformer(EMBEDDING_MODEL_NAME, token=hf_token)

    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@_cache_resource
def build_vector_indexes():
    model = load_embedding_model()
    role_documents = [
        f"{role['title']}. Field: {role['field']}. Summary: {role['summary']}. Keywords: {', '.join(role['keywords'])}. Recommended skills: {', '.join(role['recommended_skills'])}."
        for role in ROLE_CATALOG
    ]
    skill_documents = [
        f"{entry['name']}. Category: {entry['category']}. Aliases: {', '.join(entry.get('aliases', []))}."
        for entry in SKILL_ONTOLOGY
    ]
    role_vectors = model.encode(role_documents, convert_to_numpy=True)
    skill_vectors = model.encode(skill_documents, convert_to_numpy=True)
    return {
        "model": model,
        "role_documents": role_documents,
        "role_vectors": role_vectors,
        "skill_documents": skill_documents,
        "skill_vectors": skill_vectors,
    }


def cosine_similarity(vec_a, vec_b):
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if not norm_a or not norm_b:
        return 0.0
    return dot_product / (norm_a * norm_b)


def _rank_vectors(query_vector, candidates, metadata, top_k):
    scored = []
    for item, vector in zip(metadata, candidates):
        scored.append((cosine_similarity(query_vector, vector), item))
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:top_k]


def _fallback_similarity(query_text, candidate_text):
    query_tokens = set(extract_keywords(query_text))
    candidate_tokens = set(extract_keywords(candidate_text))
    if not query_tokens or not candidate_tokens:
        return 0.0
    overlap = len(query_tokens.intersection(candidate_tokens))
    return overlap / max(len(query_tokens), 1)


def compute_semantic_matches(job_description, resume_text, resume_skills, top_k=3):
    normalized_job = normalize_text(job_description)
    normalized_resume = normalize_text(resume_text)
    resume_evidence = extract_resume_evidence(resume_text, resume_skills)
    resume_skill_set = {skill.lower() for skill in resume_evidence.keys()}

    try:
        indexes = build_vector_indexes()
        model = indexes["model"]
        query_vectors = model.encode([normalized_job, normalized_resume], convert_to_numpy=True)
        job_vector, resume_vector = query_vectors

        role_matches = []
        for role, role_vector in zip(ROLE_CATALOG, indexes["role_vectors"]):
            job_score = cosine_similarity(job_vector, role_vector)
            resume_score = cosine_similarity(resume_vector, role_vector)
            keyword_alignment = len(
                resume_skill_set.intersection({canonicalize_skill(keyword).lower() for keyword in role["keywords"]})
            ) / max(len(role["keywords"]), 1)
            blended_score = (job_score * 0.45) + (resume_score * 0.35) + (keyword_alignment * 0.20)
            role_matches.append(
                {
                    "title": role["title"],
                    "field": role["field"],
                    "summary": role["summary"],
                    "recommended_skills": role["recommended_skills"],
                    "score": round(blended_score * 100, 1),
                    "job_similarity": round(job_score * 100, 1),
                    "resume_similarity": round(resume_score * 100, 1),
                    "keyword_alignment": round(keyword_alignment * 100, 1),
                }
            )

        role_matches.sort(key=lambda item: item["score"], reverse=True)

        ranked_skills = _rank_vectors(job_vector, indexes["skill_vectors"], SKILL_ONTOLOGY, top_k=16)
        jd_skill_matches = []
        missing_keywords = []
        for score, entry in ranked_skills:
            canonical = entry["name"]
            if score < 0.22:
                continue
            skill_payload = {
                "skill": canonical,
                "category": entry["category"],
                "score": round(score * 100, 1),
                "present_in_resume": canonical.lower() in resume_skill_set,
            }
            jd_skill_matches.append(skill_payload)
            if not skill_payload["present_in_resume"]:
                missing_keywords.append(canonical)

        priority_keywords = [item["skill"] for item in jd_skill_matches if not item["present_in_resume"]][:8]
        resume_job_similarity = cosine_similarity(job_vector, resume_vector)
    except Exception:
        role_matches = []
        for role in ROLE_CATALOG:
            role_document = f"{role['title']} {role['summary']} {' '.join(role['keywords'])}"
            job_score = _fallback_similarity(normalized_job, role_document)
            resume_score = _fallback_similarity(normalized_resume, role_document)
            keyword_alignment = len(
                resume_skill_set.intersection({canonicalize_skill(keyword).lower() for keyword in role["keywords"]})
            ) / max(len(role["keywords"]), 1)
            blended_score = (job_score * 0.45) + (resume_score * 0.35) + (keyword_alignment * 0.20)
            role_matches.append(
                {
                    "title": role["title"],
                    "field": role["field"],
                    "summary": role["summary"],
                    "recommended_skills": role["recommended_skills"],
                    "score": round(blended_score * 100, 1),
                    "job_similarity": round(job_score * 100, 1),
                    "resume_similarity": round(resume_score * 100, 1),
                    "keyword_alignment": round(keyword_alignment * 100, 1),
                }
            )
        role_matches.sort(key=lambda item: item["score"], reverse=True)
        jd_skill_matches = []
        missing_keywords = []
        for entry in SKILL_ONTOLOGY:
            skill_text = f"{entry['name']} {' '.join(entry.get('aliases', []))}"
            score = _fallback_similarity(normalized_job, skill_text)
            if score <= 0:
                continue
            present_in_resume = entry["name"].lower() in resume_skill_set
            jd_skill_matches.append(
                {
                    "skill": entry["name"],
                    "category": entry["category"],
                    "score": round(score * 100, 1),
                    "present_in_resume": present_in_resume,
                }
            )
            if not present_in_resume:
                missing_keywords.append(entry["name"])
        jd_skill_matches.sort(key=lambda item: item["score"], reverse=True)
        jd_skill_matches = jd_skill_matches[:16]
        priority_keywords = [item["skill"] for item in jd_skill_matches if not item["present_in_resume"]][:8]
        resume_job_similarity = _fallback_similarity(normalized_job, normalized_resume)

    keyword_density = Counter(extract_keywords(job_description))
    lexical_priority = [
        canonicalize_skill(keyword) for keyword, _ in keyword_density.most_common(12)
        if canonicalize_skill(keyword).lower() not in resume_skill_set
    ]
    merged_priority = []
    for keyword in [*priority_keywords, *lexical_priority]:
        if keyword not in merged_priority:
            merged_priority.append(keyword)

    return {
        "role_matches": role_matches[:top_k],
        "resume_job_similarity": round(resume_job_similarity * 100, 1),
        "missing_keywords": missing_keywords[:12],
        "priority_keywords": merged_priority[:8],
        "resume_skill_evidence": list(resume_evidence.values()),
        "jd_skill_matches": jd_skill_matches[:12],
    }


def build_resume_highlights(resume_data):
    name = resume_data.get("name") or "Candidate"
    skills = ", ".join(resume_data.get("skills") or [])
    degree = ", ".join(resume_data.get("degree") or []) if resume_data.get("degree") else "Not specified"
    pages = resume_data.get("no_of_pages") or 0
    return (
        f"{name} has a resume with {pages} pages. "
        f"Education: {degree}. "
        f"Skills: {skills}."
    )
