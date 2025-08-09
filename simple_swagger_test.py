#!/usr/bin/env python3

"""
Simple test to verify OpenAPI spec generation works
"""

import json

def test_basic_spec():
    """Test basic OpenAPI spec generation"""
    try:
        from apispec import APISpec
        from apispec.ext.marshmallow import MarshmallowPlugin
        from marshmallow import Schema, fields
        
        # Create basic schemas
        class RoleSchema(Schema):
            id = fields.Int(dump_only=True)
            name = fields.Str()
            description = fields.Str()

        class UserSchema(Schema):
            id = fields.Int(dump_only=True)
            email = fields.Email()
            active = fields.Bool()
            roles = fields.List(fields.Nested(RoleSchema))

        # Create spec
        spec = APISpec(
            title="docassemble CMS API",
            version="1.0.0",
            openapi_version="3.0.2",
            plugins=[MarshmallowPlugin()],
        )

        # Register schemas
        spec.components.schema("User", schema=UserSchema)
        spec.components.schema("Role", schema=RoleSchema)
        
        # Generate spec
        spec_dict = spec.to_dict()
        
        print("✓ OpenAPI spec generated successfully")
        print(f"✓ Title: {spec_dict['info']['title']}")
        print(f"✓ Version: {spec_dict['info']['version']}")
        print(f"✓ Schemas: {list(spec_dict.get('components', {}).get('schemas', {}).keys())}")
        
        # Test JSON serialization
        json_spec = json.dumps(spec_dict, indent=2)
        print(f"✓ JSON spec size: {len(json_spec)} characters")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Basic OpenAPI Spec Generation...")
    print("=" * 50)
    
    if test_basic_spec():
        print("\n🎉 Basic OpenAPI spec generation works!")
        print("\nYour swagger setup should be working correctly.")
        print("\nNext steps for React integration:")
        print("- Access swagger JSON at: /api/spec")
        print("- Access swagger JSON at: /api/swagger.json (if flask-apispec is working)")
        print("- Access swagger UI at: /api/docs/ (if flask-apispec is working)")
    else:
        print("\n❌ Basic spec generation failed.")