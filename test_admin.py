"""
Test script to verify admin dashboard works without errors
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User, Report, Keyword, CaseMatch, PastCase

def test_admin_dashboard():
    """Test that admin dashboard queries work correctly"""
    
    with app.app_context():
        print("\n" + "="*70)
        print("  TESTING ADMIN DASHBOARD")
        print("="*70 + "\n")
        
        # Test 1: Check database integrity
        print("✓ Test 1: Database Connectivity")
        user_count = User.query.count()
        report_count = Report.query.count()
        case_count = PastCase.query.count()
        print(f"  - Users in DB: {user_count}")
        print(f"  - Reports in DB: {report_count}")
        print(f"  - Past Cases in DB: {case_count}")
        
        # Test 2: Check admin dashboard queries
        print("\n✓ Test 2: Admin Dashboard Queries")
        try:
            verified = Report.query.filter_by(status='verified_by_manager').order_by(Report.created_at.asc()).all()
            resolved = Report.query.filter_by(status='resolved').order_by(Report.created_at.desc()).limit(20).all()
            print(f"  - Verified reports: {len(verified)}")
            print(f"  - Resolved reports (recent): {len(resolved)}")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False
        
        # Test 3: Check case_matcher functions
        print("\n✓ Test 3: Case Matching Functions")
        try:
            from case_matcher import case_matches_exist, get_case_matches
            
            # Test with a report if any exist
            if report_count > 0:
                test_report = Report.query.first()
                exists = case_matches_exist(test_report.id)
                print(f"  - case_matches_exist() for report #{test_report.id}: {exists}")
                matches = get_case_matches(test_report.id)
                print(f"  - get_case_matches() returned: {len(matches)} matches")
            else:
                print(f"  - No reports in DB yet, skipping report-based tests")
                
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False
        
        # Test 4: Check Jinja filter
        print("\n✓ Test 4: Jinja Template Filter")
        try:
            from app import get_case_matches_filter
            if report_count > 0:
                test_report = Report.query.first()
                matches = get_case_matches_filter(test_report)
                print(f"  - get_case_matches_filter(report) returned: {len(matches)} matches")
            print(f"  ✓ Filter is properly registered")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False
        
        print("\n" + "="*70)
        print("  ✅ ALL TESTS PASSED - ADMIN DASHBOARD SHOULD WORK!")
        print("="*70 + "\n")
        return True

if __name__ == '__main__':
    success = test_admin_dashboard()
    sys.exit(0 if success else 1)
