# docassemble CMS API Integration Guide for React

## Overview

Your docassemble installation now has comprehensive Swagger/OpenAPI documentation with automatic schema generation from SQLAlchemy models. This guide shows how to integrate it with your React frontend.

## 🎉 What's Been Implemented

### ✅ Automatic API Documentation
- **Flask-APISpec** for automatic route discovery and documentation
- **Marshmallow-SQLAlchemy** for auto-generated schemas from database models
- **OpenAPI 3.0.2** specification with comprehensive schemas
- **CORS** already configured for cross-origin requests

### ✅ API Endpoints Available

#### **Swagger/Documentation**
- `GET /api/spec` - OpenAPI JSON specification
- `GET /api/swagger.json` - Flask-APISpec swagger JSON  
- `GET /api/docs/` - Interactive Swagger UI

#### **User Management**
- `GET /api/users` - List all users with roles
- `GET /api/user` - Current user information
- `POST /api/user` - Update current user
- `GET /api/user/<user_id>` - Get specific user
- `PATCH /api/user/<user_id>` - Update specific user
- `DELETE /api/user/<user_id>` - Delete user

#### **Interview/CMS Management**
- `GET /api/interviews` - List all interviews
- `DELETE /api/interviews` - Delete interviews
- `GET /api/session/new` - Create new interview session
- `GET /api/session` - Get session variables
- `POST /api/session` - Set session variables
- `GET /api/session/question` - Get current question
- `POST /api/session/action` - Execute actions

#### **Package/Content Management**
- `GET /api/package` - List packages
- `POST /api/package` - Install packages
- `DELETE /api/package` - Remove packages
- `GET /api/playground` - List playground files
- `POST /api/playground` - Create/update files
- `DELETE /api/playground` - Delete files

## 🔧 Installation & Setup

### 1. Install Dependencies
The following dependencies have been added to `Docker/requirements.txt`:
```
flask-apispec==0.11.4
marshmallow-sqlalchemy==0.31.0
```

### 2. Configuration
Flask-APISpec is automatically initialized in `app_object.py` with these endpoints:
- Swagger JSON: `/api/swagger.json`
- Swagger UI: `/api/docs/`

### 3. CORS Configuration
CORS is already configured. Update `config.yml` to add your React app domain:
```yaml
cross site domains:
  - http://localhost:3000
  - http://localhost:5173
  - https://your-react-app.com
```

## 📱 React Integration

### 1. API Client Setup
```typescript
// api/client.ts
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export class DocassembleAPI {
  private baseURL: string;
  private apiKey?: string;

  constructor(apiKey?: string) {
    this.baseURL = API_BASE_URL;
    this.apiKey = apiKey;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include', // For session-based auth
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // User Management
  async getUsers() {
    return this.request<User[]>('/api/users');
  }

  async getCurrentUser() {
    return this.request<User>('/api/user');
  }

  // Interview Management
  async getInterviews() {
    return this.request<InterviewSession[]>('/api/interviews');
  }

  async createSession(filename: string) {
    return this.request<{ session_id: string }>('/api/session/new', {
      method: 'POST',
      body: JSON.stringify({ i: filename }),
    });
  }

  // Get current question
  async getCurrentQuestion(filename: string, sessionId: string) {
    return this.request<any>(`/api/session/question?i=${filename}&session=${sessionId}`);
  }

  // Submit answer
  async submitAnswer(filename: string, sessionId: string, variables: any) {
    return this.request<any>('/api/session', {
      method: 'POST',
      body: JSON.stringify({
        i: filename,
        session: sessionId,
        variables,
      }),
    });
  }
}
```

### 2. TypeScript Types
Generate types from your OpenAPI spec:
```bash
# Install OpenAPI TypeScript generator
npm install -g @openapitools/openapi-generator-cli

# Generate types from your docassemble API
openapi-generator-cli generate \
  -i http://localhost:5000/api/swagger.json \
  -g typescript-fetch \
  -o ./src/api/generated
```

### 3. React Hooks
```typescript
// hooks/useDocassemble.ts
import { useState, useEffect } from 'react';
import { DocassembleAPI } from '../api/client';

export function useInterviews() {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const api = new DocassembleAPI();

  useEffect(() => {
    api.getInterviews()
      .then(setInterviews)
      .finally(() => setLoading(false));
  }, []);

  return { interviews, loading };
}

export function useInterviewSession(filename: string) {
  const [session, setSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const api = new DocassembleAPI();

  const startInterview = async () => {
    const sessionData = await api.createSession(filename);
    setSession(sessionData);
    const question = await api.getCurrentQuestion(filename, sessionData.session_id);
    setCurrentQuestion(question);
  };

  const submitAnswer = async (variables: any) => {
    if (!session) return;
    
    const result = await api.submitAnswer(filename, session.session_id, variables);
    setCurrentQuestion(result);
  };

  return { session, currentQuestion, startInterview, submitAnswer };
}
```

### 4. React Components
```tsx
// components/InterviewRunner.tsx
import React from 'react';
import { useInterviewSession } from '../hooks/useDocassemble';

interface Props {
  filename: string;
}

export function InterviewRunner({ filename }: Props) {
  const { session, currentQuestion, startInterview, submitAnswer } = useInterviewSession(filename);

  if (!session) {
    return (
      <button onClick={startInterview}>
        Start Interview
      </button>
    );
  }

  if (!currentQuestion) {
    return <div>Loading...</div>;
  }

  return (
    <div className="interview-container">
      <h2>{currentQuestion.question_text}</h2>
      {/* Render form fields based on currentQuestion.field_type */}
      {/* Handle form submission with submitAnswer */}
    </div>
  );
}
```

## 🔐 Authentication

### API Key Authentication
```typescript
// For API access, you'll need API keys
const api = new DocassembleAPI('your-api-key');
```

### Session-based Authentication
```typescript
// For web interface, use session-based auth
const api = new DocassembleAPI(); // No API key needed
// Make sure credentials: 'include' is set in fetch requests
```

## 🧪 Testing the Integration

### 1. Verify Swagger UI
Visit: `http://localhost:5000/api/docs/`

### 2. Test API Endpoints
```bash
# Get OpenAPI spec
curl http://localhost:5000/api/spec

# Get users (requires authentication)
curl -X GET http://localhost:5000/api/users \
  -H "Cookie: session=your-session-cookie"

# Create new interview session
curl -X POST http://localhost:5000/api/session/new \
  -H "Content-Type: application/json" \
  -d '{"i": "interview-filename.yml"}'
```

## 📝 Key Features for Your CMS

### 1. **Interview Management**
- Create, list, and manage interview sessions
- Real-time question/answer flow
- Progress tracking and completion status

### 2. **User Management**
- User CRUD operations with role-based access
- Authentication and authorization
- User activity tracking

### 3. **Content Management**
- Playground file management (CRUD operations)
- Package installation and management
- Template and static file handling

### 4. **Real-time Integration**
- WebSocket support for real-time updates
- Session state management
- Progress tracking

## 🚀 Next Steps

1. **Install Dependencies**: Update your Docker container with the new requirements
2. **Test Endpoints**: Use the Swagger UI to test API endpoints
3. **Implement React Client**: Use the provided TypeScript examples
4. **Add Authentication**: Configure API keys or session management
5. **Customize UI**: Build your Figma design around the API structure

## 📚 Additional Resources

- **OpenAPI Spec**: Available at `/api/swagger.json`
- **Interactive Docs**: Available at `/api/docs/`
- **Existing API Endpoints**: Over 30 endpoints already available
- **CORS**: Already configured for cross-origin requests

Your docassemble instance is now ready to serve as a powerful CMS backend for your React application! 🎉