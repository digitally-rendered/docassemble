from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec import FlaskApiSpec
from marshmallow import Schema, fields
try:
    from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
    MARSHMALLOW_SQLALCHEMY_AVAILABLE = True
except ImportError:
    # Fallback to manual schema if marshmallow-sqlalchemy is not available
    MARSHMALLOW_SQLALCHEMY_AVAILABLE = False

# Define schemas - Force manual schemas to avoid SQLAlchemy auto-generation issues
MARSHMALLOW_SQLALCHEMY_AVAILABLE = False

if not MARSHMALLOW_SQLALCHEMY_AVAILABLE:
    # Manual schemas as fallback
    class RoleSchema(Schema):
        id = fields.Int(dump_only=True)
        name = fields.Str()
        description = fields.Str()

    class UserSchema(Schema):
        id = fields.Int(dump_only=True)
        social_id = fields.Str()
        nickname = fields.Str()
        email = fields.Email()
        confirmed_at = fields.DateTime(dump_only=True)
        active = fields.Bool()
        first_name = fields.Str()
        last_name = fields.Str()
        country = fields.Str()
        subdivisionfirst = fields.Str()
        subdivisionsecond = fields.Str()
        subdivisionthird = fields.Str()
        organization = fields.Str()
        timezone = fields.Str()
        language = fields.Str()
        pypi_username = fields.Str()
        modified_at = fields.DateTime(dump_only=True)
        last_login = fields.DateTime(dump_only=True)
        roles = fields.List(fields.Nested(RoleSchema))

# Additional schemas for API responses
class InterviewSessionSchema(Schema):
    """Schema for interview session data"""
    session_id = fields.Str(required=True, description="Unique session identifier")
    filename = fields.Str(required=True, description="Interview filename")
    user_id = fields.Int(required=True, description="User ID")
    encrypted = fields.Bool(description="Whether session is encrypted")
    title = fields.Str(description="Interview title")
    subtitle = fields.Str(description="Interview subtitle")  
    tags = fields.List(fields.Str(), description="Interview tags")
    created_at = fields.DateTime(dump_only=True, description="Session creation time")
    modified_at = fields.DateTime(dump_only=True, description="Last modification time")
    progress = fields.Float(description="Interview completion progress (0-1)")
    completed = fields.Bool(description="Whether interview is completed")

class SessionVariableSchema(Schema):
    """Schema for session variables"""
    name = fields.Str(required=True, description="Variable name")
    value = fields.Raw(description="Variable value")
    data_type = fields.Str(description="Variable data type")

class PackageSchema(Schema):
    """Schema for docassemble packages"""
    name = fields.Str(required=True, description="Package name")
    version = fields.Str(description="Package version")
    author = fields.Str(description="Package author")
    description = fields.Str(description="Package description")
    installed = fields.Bool(description="Whether package is installed")
    core = fields.Bool(description="Whether this is a core package")
    active = fields.Bool(description="Whether package is active")

class ErrorResponseSchema(Schema):
    """Schema for API error responses"""
    error = fields.Str(required=True, description="Error type")
    message = fields.Str(description="Error message")
    code = fields.Int(description="HTTP status code")

class SuccessResponseSchema(Schema):
    """Schema for API success responses"""
    success = fields.Bool(required=True, description="Operation success status")
    message = fields.Str(description="Success message")
    data = fields.Raw(description="Response data")

# APISpec configuration
spec = APISpec(
    title="docassemble CMS API",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[MarshmallowPlugin()],
    info=dict(
        description="RESTful API for docassemble interview and content management system",
        contact=dict(name="docassemble", url="https://docassemble.org"),
        license=dict(name="MIT", url="https://opensource.org/licenses/MIT")
    ),
    servers=[
        {"url": "/", "description": "Local server"}
    ],
    tags=[
        {"name": "users", "description": "User management operations"},
        {"name": "interviews", "description": "Interview management operations"},
        {"name": "sessions", "description": "Session management operations"},
        {"name": "packages", "description": "Package management operations"},
        {"name": "playground", "description": "CMS/Playground operations"},
        {"name": "system", "description": "System administration operations"}
    ]
)

# Register schemas - Temporarily disabled to fix startup issues
# spec.components.schema("User", schema=UserSchema)
# spec.components.schema("Role", schema=RoleSchema)
# spec.components.schema("InterviewSession", schema=InterviewSessionSchema)
# spec.components.schema("SessionVariable", schema=SessionVariableSchema)
# spec.components.schema("Package", schema=PackageSchema)
# spec.components.schema("ErrorResponse", schema=ErrorResponseSchema)
# spec.components.schema("SuccessResponse", schema=SuccessResponseSchema)

# Flask-APISpec instance (to be initialized with app)
docs = None

def init_docs(app):
    """Initialize Flask-APISpec with the Flask app"""
    global docs
    app.config.update({
        'APISPEC_SPEC': spec,
        'APISPEC_SWAGGER_URL': '/api/swagger.json',
        'APISPEC_SWAGGER_UI_URL': '/api/docs/',
    })
    docs = FlaskApiSpec(app)
    return docs
