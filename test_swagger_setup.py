#!/usr/bin/env python3

"""
Simple test script to verify swagger/OpenAPI setup works
"""

import sys
import os
import json

# Add the docassemble modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'docassemble_webapp'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'docassemble_base'))

def test_schema_generation():
    """Test that schemas can be generated from SQLAlchemy models"""
    try:
        from docassemble.webapp.openapi_spec import UserSchema, RoleSchema, spec
        
        print("✓ Successfully imported schemas")
        
        # Test UserSchema
        user_schema = UserSchema()
        print(f"✓ UserSchema created with fields: {list(user_schema.fields.keys())}")
        
        # Test RoleSchema  
        role_schema = RoleSchema()
        print(f"✓ RoleSchema created with fields: {list(role_schema.fields.keys())}")
        
        # Test spec generation
        spec_dict = spec.to_dict()
        print(f"✓ OpenAPI spec generated with {len(spec_dict.get('components', {}).get('schemas', {}))} schemas")
        
        # Check if our schemas are in the spec
        schemas = spec_dict.get('components', {}).get('schemas', {})
        if 'User' in schemas:
            print("✓ User schema found in OpenAPI spec")
        if 'Role' in schemas:
            print("✓ Role schema found in OpenAPI spec")
            
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_flask_apispec_config():
    """Test Flask-APISpec configuration"""
    try:
        from docassemble.webapp.openapi_spec import init_docs
        from flask import Flask
        
        # Create a test app
        app = Flask(__name__)
        
        # Initialize docs
        docs = init_docs(app)
        
        print("✓ Flask-APISpec initialized successfully")
        print(f"✓ Swagger JSON URL: {app.config.get('APISPEC_SWAGGER_URL')}")
        print(f"✓ Swagger UI URL: {app.config.get('APISPEC_SWAGGER_UI_URL')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Swagger/OpenAPI Setup...")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing Schema Generation:")
    success &= test_schema_generation()
    
    print("\n2. Testing Flask-APISpec Configuration:")
    success &= test_flask_apispec_config()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Swagger setup is working correctly.")
        
        print("\nNext steps:")
        print("- Install dependencies: pip install flask-apispec marshmallow-sqlalchemy")
        print("- Access Swagger UI at: http://localhost:5000/api/docs/")
        print("- Access Swagger JSON at: http://localhost:5000/api/swagger.json")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)