# import math
# import os
import os
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
    tokens=[token.lower() for token in TOKEN_PATTERN.findall(text or "")]
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

def evaluate_resume_score(resume_text):
    score=0
    checks=[]
    lowered=normalize_text(resume_text or "").lower()
    bullet_hits = len(
        re.findall(
            r"^\s*[\-\*\u2022\u25cf]",
            resume_text or "",
            re.MULTILINE
        )
    )
    for rule in SECTION_RULES:
        matched = any(
            re.search(
                WORD_BOUNDARY_TEMPLATE.format(re.escape(pattern)),
                lowered
            )
            for pattern in rule["patterns"]
        )
        awarded_score=0
        matched_by=None
        if matched:
            awarded_score+=rule['weight']
            matched_by="pattern"
        else:
            fallback=rule.get('fallback')

            if fallback and fallback.get("type")=="bullet_count":
                if bullet_hits>=fallback.get("minimum",0):
                    matched=True
                    awarded_score=fallback.get("score",0)
                    matched_by="bullet_fallback"

        score+=awarded_score

        checks.append(
            {
                "key": rule["key"],
                "label": rule["label"],
                "category": rule["category"],
                "matched": matched,
                "matched_by": matched_by,
                "score": awarded_score,
                "weight": rule["weight"],
                "success": rule["success"],
                "warning": rule["warning"],
            }
        )
    metric_metions=len(
        re.findall(
            r"\b\d+%|\b\d+\+|\$\d+|\b\d+\s*"
            r"(users|customers|clients|ms|sprints?|months?)\b",
            lowered
        )
    )
    quality_bonus=0
    if metric_metions>=2:
        quality_bonus+=8
    elif metric_metions==1:
        quality_bonus+=4
    if bullet_hits>=4:
        quality_bonus+=8
    elif bullet_hits>=2:
        quality_bonus+=3
        
    return min(score+quality_bonus,100) ,checks
        
def infer_candidate_level(page_count,resume_text):
    lowered=normalize_text(resume_text).lower()
    if not lowered:
        return "NA"
    year_matches = [
        int(match)
        for match in re.findall(
            r"\b(\d{1,2})\+?\s+years?\b",
            lowered
        )
    ]
    max_years = max(year_matches) if year_matches else 0
    project_hits = len(
        re.findall(r"\b(project|projects)\b", lowered))
    internship_hits = len(
        re.findall(
            r"\b(internship|internships|intern)\b",
            lowered
        )
    )
    experience_hits = len(
        re.findall(
            r"\b(experience|employment|work experience)\b",
            lowered
        )
    )
    if max_years>=4 or internship_hits or project_hits>=2:
        return "Experienced"
    if max_years >= 1 or internship_hits or project_hits >= 2:
        return "Intermediate"
    return "Fresher"

def infer_role_from_skills(skills,resume_text=""):
    resume_evidence=extract_resume_evidence(
        resume_text,skills
    )
    normalized_skills={
        normalize_token(skill)
        for skill in resume_evidence.keys()
    }
    resume_text_lower = normalize_text(resume_text).lower()
    best_role=None
    best_overlap=0.0
    best_score=0
    best_matching=[]
    best_missing = []
    for role in ROLE_CATALOG:
        role_score=0
        matched_keywords=[]
        for keyword in role["keywords"]:
            canonical_keyword=canonicalize_skill(keyword)
            normalize_keyword=normalize_token(canonical_keyword)

            if normalize_keyword in normalized_skills:
                role_score+=2
                matched_keywords.append(canonical_keyword)
            elif keyword.lower() in resume_text_lower:
                role_score+=1
                matched_keywords.append(keyword)
        if role_score>best_score:
            best_score=role_score
            best_role=role
            best_matching=matched_keywords
            best_missing=[
                canonicalize_skill(keyword)
                for keyword in role["keywords"]
                if normalize_token(canonicalize_skill(keyword))
                not in normalized_skills
            ]
    if not best_role:
        fallback_role = ROLE_CATALOG[0]
        return {
            "title": fallback_role["title"],
            "field": "General",
            "recommended_skills": fallback_role["recommended_skills"],
            "courses_key": fallback_role["courses_key"],
            "match_reason": (
                "Using a general fallback because the resume skills were sparse."
            ),
        }
    recommended = []
    for skill in best_missing + best_role["recommended_skills"]:
        if skill not in recommended:
            recommended.append(skill)

    return {
        "title": best_role["title"],
        "field": best_role["field"],
        "recommended_skills": recommended[:6],
        "courses_key": best_role["courses_key"],
        "match_reason": (
            f"Detected {best_score} aligned role signals: "
            f"{', '.join(best_matching[:4]) or 'general skills'}."
        ),
    }

def cosine_similarity(vec_a,vec_b):
    dot=sum( a*b for a,b in zip(vec_a,vec_b))
    magnitude_a=sum(value*value for value in vec_a)**0.5
    magnitude_b=sum(value*value for value in vec_b)**0.5
    if magnitude_a==0 or magnitude_b==0:
        return 0.0
    return dot/(magnitude_b*magnitude_a)

def load_embedding_model():
    from sentence_transformers import SentenceTransformer
    hf_token=os.getenv("HF_TOKEN")
    if hf_token:
        return SentenceTransformer(EMBEDDING_MODEL_NAME,token=hf_token)
    return SentenceTransformer(EMBEDDING_MODEL_NAME)
    
    


def build_vector_indexes():
    model=load_embedding_model()
    role_doc=[]
    skill_doc=[]
    for role in ROLE_CATALOG:
       text=( f"{role['title']}."
        f"'Field':{role['field']}."
        f"keywords:{' ,'.join(role['keywords'])}."
        )
       role_doc.append(text)
    for entry in SKILL_ONTOLOGY:
        skill_doc.append(
            f"{entry['name']}. Category: {entry['category']}. Aliases: {', '.join(entry.get('aliases', []))}."
        )
    role_vec=model.encode(role_doc,convert_to_numpy=True)
    skill_vec=model.encode(skill_doc,convert_to_numpy=True)

    return {
        "model":model,
        "role_vectors":role_vec,
        "skill_vectors":skill_vec,
        "role_texts":role_doc,
        "skill_texts":skill_doc,
    }

def compute_semantic_matches(
            job_description,resume_text,resume_skills):
    jd_keywords=extract_keywords(job_description)
    resume_evidence=extract_resume_evidence(resume_text,resume_skills)
    return {
        "resume_job_similarity": 0,
        "role_matches": [],
        "jd_skill_matches": [],
        "resume_skill_evidence": list(resume_evidence.values()),
        "missing_keywords": jd_keywords,
        "priority_keywords": jd_keywords[:8],
    }

result = compute_semantic_matches(
    "Looking for FastAPI Docker PostgreSQL",
    "Built APIs with FastAPI and Postgres",
    ["Python"]
)

print(result["priority_keywords"])
print([item["skill"] for item in result["resume_skill_evidence"]])
        


            


    


        



