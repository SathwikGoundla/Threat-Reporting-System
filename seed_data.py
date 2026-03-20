"""
Seed Database with Sample Police/Government Solved Cases
Run this once after database setup to load reference cases for AI matching

Usage: python seed_data.py
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, PastCase

def seed_past_cases():
    """Load sample police/government solved cases into the database"""
    
    with app.app_context():
        # Check if data already exists
        existing_count = PastCase.query.count()
        if existing_count > 0:
            print(f"\n⚠️  Database already contains {existing_count} cases.")
            response = input("Do you want to clear and reload? (yes/no): ").strip().lower()
            if response == 'yes':
                PastCase.query.delete()
                db.session.commit()
                print("✅ Cleared existing cases.")
            else:
                print("✅ Keeping existing cases. Exiting.")
                return
        
        print("\n" + "="*70)
        print("  SEEDING DATABASE WITH SAMPLE POLICE/GOVERNMENT CASES")
        print("="*70 + "\n")
        
        # Sample cases - These are realistic but fictional for demonstration
        sample_cases = [
            {
                'case_title': 'Workplace Sexual Harassment - IT Company Case',
                'category': 'workplace',
                'problem_type': 'Sexual Harassment',
                'description': 'Female employee reported unwanted physical contact and inappropriate remarks from senior manager. Investigation found evidence of repeated harassment over 6 months.',
                'solution': 'Manager was suspended pending investigation. Company conducted mandatory training for all staff. Victim was relocated to different team with protective measures. Compensation awarded for emotional trauma.',
                'authority': 'Police Cyber Crime Cell + Company HR',
                'keywords': 'harassment, workplace, physical contact, manager, inappropriate'
            },
            {
                'case_title': 'College Ragging and Physical Assault',
                'category': 'educational',
                'problem_type': 'Ragging and Bullying',
                'description': 'First-year student reported severe ragging by senior students including physical assault, sleep deprivation, and forced activities. Multiple victims identified.',
                'solution': 'All perpetrators were rusticated (expelled). College formed anti-ragging committee. Strict policies implemented. Counseling provided to victims. Criminal charges filed against senior students.',
                'authority': 'University Administration + Police Department',
                'keywords': 'ragging, bullying, assault, seniors, college'
            },
            {
                'case_title': 'Cyber Stalking and Blackmail Case',
                'category': 'workplace',
                'problem_type': 'Cyber Stalking/Blackmail',
                'description': 'Employee received threatening messages and was being stalked online. Harasser obtained private photos and threatened to publish them unless demands were met.',
                'solution': 'Hacker was traced and arrested. Company provided cybersecurity training. Victim received counseling support. Stronger data protection policies implemented. Criminal case registered under IT Act.',
                'authority': 'Cyber Crime Police + IT Security',
                'keywords': 'cyber, stalking, blackmail, online harassment, threat'
            },
            {
                'case_title': 'Gender Discrimination in Promotions',
                'category': 'workplace',
                'problem_type': 'Discrimination',
                'description': 'Female employee with better performance was denied promotion while junior male colleague was promoted. Pattern of discrimination found across organization.',
                'solution': 'Promotion granted retroactively with back pay and bonus. Company implemented gender-neutral promotion criteria. HR training on anti-discrimination. Policy reforms in hiring and advancement.',
                'authority': 'Labour Ministry + Company Management',
                'keywords': 'discrimination, promotion, gender, workplace equality'
            },
            {
                'case_title': 'Teacher Inappropriate Conduct with Student',
                'category': 'educational',
                'problem_type': 'Inappropriate Conduct',
                'description': 'Multiple students reported inappropriate behavior and comments from teacher. Investigation revealed pattern of misconduct spanning years.',
                'solution': 'Teacher was permanently terminated. School conducted awareness programs. Posted mandatory counselor in school. Student support groups formed. Criminal charges filed and conviction obtained.',
                'authority': 'Educational Board + Police Department',
                'keywords': 'teacher, inappropriate, student, school, conduct'
            },
            {
                'case_title': 'Caste-Based Harassment and Discrimination',
                'category': 'workplace',
                'problem_type': 'Caste Discrimination',
                'description': 'Employee from SC/ST category faced derogatory remarks, exclusion from meetings, and biased performance reviews. Managers made casteist comments openly.',
                'solution': 'Management conducted mandatory caste sensitivity training. Created workplace grievance cell. Victim promoted and compensated. Anti-discrimination policy strengthened. Strict action against offending managers.',
                'authority': 'SC/ST Commission + Labour Department',
                'keywords': 'caste discrimination, harassment, workplace, equality'
            },
            {
                'case_title': 'Academic Fraud and Online Blackmail',
                'category': 'educational',
                'problem_type': 'Fraud and Blackmail',
                'description': 'Student discovered teacher was fraudulently manipulating grades in exchange for money. When student refused to participate, was threatened and blackmailed.',
                'solution': 'Teacher was dismissed and prosecuted. Anti-corruption committee instituted. Automated automated grading system implemented. Student received marks correction and compensation.',
                'authority': 'University + Anti-Corruption Bureau',
                'keywords': 'fraud, blackmail, grades, corruption'
            },
            {
                'case_title': 'Physical Assault by Supervisor',
                'category': 'workplace',
                'problem_type': 'Physical Assault',
                'description': 'Supervisor physically assaulted employee due to minor workplace disagreement. Attack witnessed by multiple colleagues. Victim suffered injuries requiring hospitalization.',
                'solution': 'Supervisor arrested and prosecuted. Company provided immediate medical and counseling support to victim. Workplace violence policy reformed. Supervisor convicted and sentenced to 6 months imprisonment.',
                'authority': 'Police Department + Labour Court',
                'keywords': 'assault, violence, supervisor, physical injury'
            }
        ]
        
        created_count = 0
        for idx, case_data in enumerate(sample_cases, 1):
            try:
                past_case = PastCase(
                    case_title=case_data['case_title'],
                    category=case_data['category'],
                    problem_type=case_data['problem_type'],
                    description=case_data['description'],
                    solution=case_data['solution'],
                    authority=case_data['authority'],
                    keywords=case_data['keywords'],
                    case_date=datetime.utcnow() - timedelta(days=idx*30),  # Stagger dates
                    created_at=datetime.utcnow()
                )
                db.session.add(past_case)
                print(f"  [{idx}/8] ✓ {case_data['case_title']}")
                created_count += 1
            except Exception as e:
                print(f"  [{idx}/8] ✗ Error creating case: {e}")
        
        try:
            db.session.commit()
            print("\n" + "="*70)
            print(f"  ✅ SUCCESS! Loaded {created_count} police/government cases")
            print("="*70 + "\n")
            print("💡 These cases will be used for AI matching when users submit reports.\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing to database: {e}\n")

if __name__ == '__main__':
    seed_past_cases()
