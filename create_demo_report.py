"""
Demo Script: Create a test report with matching police cases
This demonstrates how case matching works end-to-end
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User, Report, Keyword, CaseMatch
from case_matcher import find_similar_cases, save_case_matches

def create_demo_report():
    """Create a test report that matches harassment cases from PastCase"""
    
    with app.app_context():
        print("\n" + "="*70)
        print("  CREATING DEMO REPORT WITH CASE MATCHING")
        print("="*70 + "\n")
        
        # Get or create admin user for testing
        admin_user = User.query.filter_by(phone='+919949258081').first()
        if not admin_user:
            print("❌ Admin user not found. Please login as admin first.")
            return False
        
        # Create a test report that will match harassment cases
        demo_report = Report(
            user_id=admin_user.id,
            category='workplace',
            problem_type='Sexual Harassment',
            description='Senior manager made inappropriate remarks and unwanted physical contact. This happened repeatedly over several months. I reported to HR but no action was taken.',
            status='verified_by_manager'  # Set to verified so it appears in admin dashboard
        )
        
        db.session.add(demo_report)
        db.session.flush()  # Flush to get the report ID
        
        report_id = demo_report.id
        print(f"✓ Created report #{report_id}")
        print(f"  Category: {demo_report.category}")
        print(f"  Problem: {demo_report.problem_type}")
        print(f"  Status: {demo_report.status}\n")
        
        # Extract and add keywords
        keywords = ['harassment', 'inappropriate', 'sexual', 'manager', 'contact', 'HR', 'workplace']
        print(f"✓ Adding keywords:")
        for kw in keywords:
            keyword = Keyword(report_id=report_id, keyword=kw)
            db.session.add(keyword)
            print(f"  - {kw}")
        
        db.session.commit()
        print(f"\n✓ Report saved\n")
        
        # Now find and save matching cases
        print("Matching with police/government cases...")
        demo_report = Report.query.get(report_id)  # Refresh to get relationships
        
        try:
            similar_cases = find_similar_cases(demo_report, top_n=5, min_similarity=0.2)
            print(f"✓ Found {len(similar_cases)} similar cases:\n")
            
            if similar_cases:
                for idx, (past_case, similarity) in enumerate(similar_cases, 1):
                    print(f"  [{idx}] {past_case.case_title}")
                    print(f"      Similarity: {similarity*100:.1f}%")
                    print(f"      Authority: {past_case.authority}")
                    print(f"      Solution: {past_case.solution[:100]}...\n")
                
                # Save the matches to database
                save_case_matches(report_id, similar_cases)
                print(f"✓ Saved {len(similar_cases)} case matches to database\n")
            else:
                print("  ⚠️  No matching cases found\n")
        
        except Exception as e:
            print(f"❌ Error matching cases: {e}\n")
            return False
        
        # Verify the matches were saved
        matches = CaseMatch.query.filter_by(report_id=report_id).all()
        print("="*70)
        print(f"✅ SUCCESS! Report #{report_id} now has {len(matches)} case matches")
        print("="*70 + "\n")
        print(f"📍 View it in admin dashboard → Awaiting Resolution section")
        print(f"   The admin will see {len(matches)} similar police cases!\n")
        
        return True

if __name__ == '__main__':
    success = create_demo_report()
    sys.exit(0 if success else 1)
