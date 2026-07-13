#!/usr/bin/env python3
"""Verification script for Analysis model implementation."""
import sys
from app import create_app
from models.analysis import Analysis


def verify_analysis_model():
    """Verify Analysis model structure and functionality."""
    print("Verifying Analysis model implementation...")
    
    app = create_app()
    
    with app.app_context():
        # Test 1: Verify model attributes
        print("\n1. Checking model attributes...")
        required_attrs = [
            'id', 'user_id', 'resume_id', 'job_description',
            'match_score', 'ats_score', 'quality_score',
            'extracted_skills', 'match_breakdown', 'recommendations',
            'industry', 'created_at'
        ]
        
        for attr in required_attrs:
            if not hasattr(Analysis, attr):
                print(f"   ❌ Missing attribute: {attr}")
                return False
            print(f"   ✓ Found attribute: {attr}")
        
        # Test 2: Create an Analysis instance
        print("\n2. Creating Analysis instance...")
        try:
            analysis = Analysis(
                user_id=1,
                resume_id=1,
                job_description='Python developer with 3+ years experience',
                match_score=85.5,
                ats_score=92.0,
                quality_score=88.0,
                extracted_skills={
                    'technical': ['Python', 'Django', 'PostgreSQL'],
                    'soft': ['Communication', 'Teamwork']
                },
                match_breakdown={
                    'required_skills_score': 90.0,
                    'preferred_skills_score': 80.0,
                    'experience_score': 85.0
                },
                recommendations=[
                    'Add more Python project details',
                    'Emphasize Django experience'
                ],
                industry='Technology'
            )
            print("   ✓ Analysis instance created successfully")
        except Exception as e:
            print(f"   ❌ Failed to create Analysis instance: {e}")
            return False
        
        # Test 3: Verify attribute values
        print("\n3. Verifying attribute values...")
        checks = [
            (analysis.user_id == 1, "user_id"),
            (analysis.resume_id == 1, "resume_id"),
            ('Python developer' in analysis.job_description, "job_description"),
            (analysis.match_score == 85.5, "match_score"),
            (analysis.ats_score == 92.0, "ats_score"),
            (analysis.quality_score == 88.0, "quality_score"),
            ('Python' in analysis.extracted_skills['technical'], "extracted_skills"),
            (analysis.match_breakdown['required_skills_score'] == 90.0, "match_breakdown"),
            (len(analysis.recommendations) == 2, "recommendations"),
            (analysis.industry == 'Technology', "industry")
        ]
        
        for check, name in checks:
            if not check:
                print(f"   ❌ Failed check: {name}")
                return False
            print(f"   ✓ Passed check: {name}")
        
        # Test 4: Test __repr__ method
        print("\n4. Testing __repr__ method...")
        analysis.id = 10
        repr_str = repr(analysis)
        if '<Analysis 10 for resume 1>' == repr_str:
            print(f"   ✓ __repr__ works correctly: {repr_str}")
        else:
            print(f"   ❌ __repr__ incorrect: {repr_str}")
            return False
        
        # Test 5: Test to_dict method
        print("\n5. Testing to_dict method...")
        try:
            analysis_dict = analysis.to_dict()
            required_keys = [
                'id', 'user_id', 'resume_id', 'job_description',
                'match_score', 'ats_score', 'quality_score',
                'extracted_skills', 'match_breakdown', 'recommendations',
                'industry', 'created_at'
            ]
            
            for key in required_keys:
                if key not in analysis_dict:
                    print(f"   ❌ Missing key in dict: {key}")
                    return False
            
            print("   ✓ to_dict method works correctly")
            print(f"   ✓ Dict contains all required keys: {', '.join(required_keys)}")
        except Exception as e:
            print(f"   ❌ to_dict method failed: {e}")
            return False
        
        # Test 6: Test with nullable industry
        print("\n6. Testing nullable industry field...")
        try:
            analysis_no_industry = Analysis(
                user_id=1,
                resume_id=1,
                job_description='Generic job',
                match_score=75.0,
                ats_score=80.0,
                quality_score=85.0,
                extracted_skills={},
                match_breakdown={},
                recommendations=[],
                industry=None
            )
            if analysis_no_industry.industry is None:
                print("   ✓ Nullable industry field works correctly")
            else:
                print(f"   ❌ Industry should be None but is: {analysis_no_industry.industry}")
                return False
        except Exception as e:
            print(f"   ❌ Failed to create Analysis with null industry: {e}")
            return False
        
        # Test 7: Verify relationships
        print("\n7. Checking relationships...")
        if hasattr(Analysis, 'user'):
            print("   ✓ User relationship defined")
        else:
            print("   ❌ User relationship missing")
            return False
        
        if hasattr(Analysis, 'resume'):
            print("   ✓ Resume relationship defined")
        else:
            print("   ❌ Resume relationship missing")
            return False
        
        print("\n" + "="*50)
        print("✅ All Analysis model verifications passed!")
        print("="*50)
        return True


if __name__ == '__main__':
    success = verify_analysis_model()
    sys.exit(0 if success else 1)
