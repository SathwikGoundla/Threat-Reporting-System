"""
AI Case Matching System
Matches user reports with previously solved police/government cases
Uses keyword-based similarity with Jaccard algorithm and TF-IDF
"""

import os
import sys
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None

from models import PastCase, CaseMatch, Report, Keyword, db

def find_similar_cases(report, top_n=5, min_similarity=0.2):
    """
    Find similar past cases for a given report using multi-method matching
    
    Args:
        report: Report object
        top_n: Number of similar cases to return
        min_similarity: Minimum similarity threshold (0.0 to 1.0)
        
    Returns:
        list: List of (PastCase, similarity_score) tuples
    """
    # Get all past cases
    past_cases = PastCase.query.all()
    
    if not past_cases:
        return []
    
    # Extract keywords from report
    report_keywords = [kw.keyword for kw in report.keywords]
    report_text = f"{report.problem_type} {report.description} {' '.join(report_keywords)}"
    
    # Prepare past case texts
    case_texts = []
    for case in past_cases:
        case_text = f"{case.problem_type} {case.description} {case.keywords or ''}"
        case_texts.append(case_text)
    
    # If only 1-2 cases, use simple keyword matching
    if len(past_cases) < 3:
        return simple_keyword_matching(report, past_cases, top_n)
    
    # Use TF-IDF for similarity if sklearn is available
    if TfidfVectorizer and cosine_similarity:
        try:
            vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
            all_texts = [report_text] + case_texts
            
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            
            matches = []
            for idx, (case, score) in enumerate(zip(past_cases, similarity_scores)):
                if score >= min_similarity:
                    matches.append((case, float(score)))
            
            # Sort by similarity descending
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[:top_n]
            
        except Exception as e:
            print(f"⚠️ TF-IDF matching failed: {e}, falling back to keyword matching")
            return simple_keyword_matching(report, past_cases, top_n)
    
    # Fallback to keyword matching
    return simple_keyword_matching(report, past_cases, top_n)


def simple_keyword_matching(report, past_cases, top_n=5):
    """
    Fallback: Simple keyword overlap matching using Jaccard similarity
    
    Args:
        report: Report object
        past_cases: List of PastCase objects
        top_n: Number of results to return
    
    Returns:
        list: List of (PastCase, similarity_score) tuples
    """
    report_keywords = set(kw.keyword.lower() for kw in report.keywords)
    
    if not report_keywords:
        # If no keywords, use text similarity
        report_words = set(report.description.lower().split())
        report_words.update(report.problem_type.lower().split())
    else:
        report_words = report_keywords
    
    matches = []
    for case in past_cases:
        # Extract keywords from past case
        case_keywords = set(k.strip().lower() for k in (case.keywords or '').split(','))
        case_words = set(case.description.lower().split())
        case_words.update(case.problem_type.lower().split())
        case_words.update(case_keywords)
        
        # Calculate Jaccard similarity
        if not case_words:
            similarity = 0.0
        else:
            intersection = len(report_words & case_words)
            union = len(report_words | case_words)
            similarity = intersection / union if union > 0 else 0.0
        
        if similarity > 0:
            matches.append((case, similarity))
    
    # Sort by similarity descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:top_n]


def save_case_matches(report_id, similar_cases=None):
    """
    Find and store similar cases for a report in database
    
    Args:
        report_id: Report ID
        similar_cases: Optional pre-calculated list of (PastCase, similarity) tuples
    """
    report = Report.query.get(report_id)
    if not report:
        print(f"❌ Report #{report_id} not found")
        return
    
    # Delete existing matches
    CaseMatch.query.filter_by(report_id=report_id).delete()
    
    # Find similar cases if not provided
    if similar_cases is None:
        similar_cases = find_similar_cases(report, top_n=5)
    
    # Store matches
    matches_count = 0
    for past_case, similarity in similar_cases:
        try:
            match = CaseMatch(
                report_id=report_id,
                past_case_id=past_case.id,
                similarity=round(similarity, 4)  # Round to 4 decimal places
            )
            db.session.add(match)
            matches_count += 1
        except Exception as e:
            print(f"❌ Error saving case match: {e}")
    
    try:
        db.session.commit()
        print(f"✅ Stored {matches_count} similar case(s) for report #{report_id}")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error committing case matches: {e}")


def get_case_matches(report_id, limit=5):
    """
    Get stored case matches for a report from database
    
    Args:
        report_id: Report ID
        limit: Maximum number of matches to return
    
    Returns:
        list: List of (PastCase, similarity) tuples, sorted by similarity descending
    """
    matches = (CaseMatch.query
               .filter_by(report_id=report_id)
               .order_by(CaseMatch.similarity.desc())
               .limit(limit)
               .all())
    
    return [(match.past_case, match.similarity) for match in matches]


def get_all_case_matches(report_id):
    """
    Get all stored case matches for a report
    
    Args:
        report_id: Report ID
    
    Returns:
        list: List of CaseMatch objects
    """
    return (CaseMatch.query
            .filter_by(report_id=report_id)
            .order_by(CaseMatch.similarity.desc())
            .all())


def case_matches_exist(report_id):
    """Check if case matches exist for a report"""
    return db.session.query(CaseMatch.query.filter_by(report_id=report_id).exists()).scalar()
