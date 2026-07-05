import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.embedder import get_embedding, get_embeddings_batch
from app.services.extractor import extract_skills, extract_section


def calculate_match_score(resume_text: str, jd_text: str) -> dict:
    """
    Multi-level matching:
    1. Full document similarity
    2. Skills section similarity  
    3. Experience section similarity
    4. Weighted final score
    5. Gap analysis
    """

    # Full document score 
    resume_emb = get_embedding(resume_text)
    jd_emb = get_embedding(jd_text)
    full_score = float(cosine_similarity(
        resume_emb.reshape(1, -1),
        jd_emb.reshape(1, -1)
    )[0][0])

    #  Skills section score 
    resume_skills_text = extract_section(resume_text, "SKILLS")
    jd_skills_text = extract_section(jd_text, "SKILLS") or jd_text
    # If JD has no skills section, compare against full JD

    if resume_skills_text:
        skills_emb_r = get_embedding(resume_skills_text)
        skills_emb_j = get_embedding(jd_skills_text)
        skills_score = float(cosine_similarity(
            skills_emb_r.reshape(1, -1),
            skills_emb_j.reshape(1, -1)
        )[0][0])
    else:
        skills_score = full_score  # fallback

    # Experience section score 
    resume_exp_text = extract_section(resume_text, "EXPERIENCE") \
                   or extract_section(resume_text, "PROJECTS")
    jd_exp_text = extract_section(jd_text, "RESPONSIBILITIES") or jd_text

    if resume_exp_text:
        exp_emb_r = get_embedding(resume_exp_text)
        exp_emb_j = get_embedding(jd_exp_text)
        exp_score = float(cosine_similarity(
            exp_emb_r.reshape(1, -1),
            exp_emb_j.reshape(1, -1)
        )[0][0])
    else:
        exp_score = full_score  # fallback

    #  Weighted final score 
    # Skills weighted higher for freshers
    # Adjust these weights based on role type later
    weighted_score = (
        full_score   * 0.3 +
        skills_score * 0.5 +
        exp_score    * 0.2
    )

    # Gap analysis 
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text))

    matched_skills = list(resume_skills & jd_skills)   # in both
    missing_skills = list(jd_skills - resume_skills)   # in JD but not resume
    extra_skills = list(resume_skills - jd_skills)     # in resume but not JD

    return {
        "scores": {
            "overall": round(weighted_score, 4),
            "percentage": round(weighted_score * 100, 2),
            "label": get_match_label(weighted_score),
            "breakdown": {
                "full_document": round(full_score, 4),
                "skills_section": round(skills_score, 4),
                "experience_section": round(exp_score, 4)
            }
        },
        "skills": {
            "matched": sorted(matched_skills),
            "gaps": sorted(missing_skills),
            "extras": sorted(extra_skills)
        }
    }


def get_match_label(score: float) -> str:
    if score >= 0.75:
        return "Strong Match"
    elif score >= 0.55:
        return "Moderate Match"
    elif score >= 0.35:
        return "Weak Match"
    else:
        return "Poor Match"