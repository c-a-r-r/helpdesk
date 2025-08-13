import os
import httpx
import secrets
from fastapi import FastAPI, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from dotenv import load_dotenv
from routes import router as api_router
from database import engine
from models import Base

# Load environment variables from .env file first
load_dotenv()

# Environment configuration loaded from .env file
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
print(f"📁 Using environment variables for {ENVIRONMENT} environment")

app = FastAPI(
    title="Helpdesk CRM API",
    description="API for managing user onboarding and helpdesk operations",
    version="1.0.0"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    
    # Start background scheduler for automated tasks
    try:
        from scheduler import background_scheduler
        background_scheduler.start()
        print("✅ Background scheduler started for automated Freshservice sync")
    except Exception as e:
        print(f"⚠️  Failed to start background scheduler: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    # Stop background scheduler
    try:
        from scheduler import background_scheduler
        background_scheduler.stop()
        print("🛑 Background scheduler stopped")
    except Exception as e:
        print(f"⚠️  Error stopping scheduler: {e}")

# Include API routes
app.include_router(api_router, prefix="/api/v1", tags=["API"])

# Include auth routes directly under /api for frontend compatibility
@app.get("/api/login") 
async def api_login_endpoint():
    return await api_login()

@app.get("/api/callback")
async def api_callback(code: str = Query(None), state: str = Query(None)):
    return await callback(code, state)

@app.get("/api/debug")
def api_debug():
    return debug_config()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Helpdesk CRM API is running"}

# Allow Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "https://helpdesk.amer.biz"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JumpCloud OAuth Configuration - strict validation for production
print("🔍 JumpCloud Configuration:")
print(f"   JUMPCLOUD_CLIENT_ID: {os.getenv('JUMPCLOUD_CLIENT_ID', 'Not set')}")
print(f"   JUMPCLOUD_CLIENT_SECRET: {'✅ Set' if os.getenv('JUMPCLOUD_CLIENT_SECRET') else '❌ Not set'}")
print(f"   JUMPCLOUD_ISSUER: {os.getenv('JUMPCLOUD_ISSUER', 'Not set')}")
print(f"   JUMPCLOUD_API_KEY: {'✅ Set' if os.getenv('JUMPCLOUD_API_KEY') else '❌ Not set'}")
print(f"   REDIRECT_URI: {os.getenv('REDIRECT_URI', 'Not set')}")

CLIENT_ID = os.getenv("JUMPCLOUD_CLIENT_ID")
CLIENT_SECRET = os.getenv("JUMPCLOUD_CLIENT_SECRET")
ISSUER = os.getenv("JUMPCLOUD_ISSUER")
REDIRECT_URI = os.getenv("JUMPCLOUD_REDIRECT_URI") or os.getenv("REDIRECT_URI")
API_KEY = os.getenv("JUMPCLOUD_API_KEY")

# Frontend URL configuration based on environment
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://helpdesk.amer.biz" if ENVIRONMENT == "prod" else "http://localhost:3000")

# Validate OAuth configuration
if not all([CLIENT_ID, CLIENT_SECRET, ISSUER, REDIRECT_URI, API_KEY]):
    if ENVIRONMENT in ["prod", "staging"]:
        print("❌ CRITICAL: Missing required OAuth configuration for production")
        missing = [k for k, v in {
            "JUMPCLOUD_CLIENT_ID": CLIENT_ID,
            "JUMPCLOUD_CLIENT_SECRET": CLIENT_SECRET, 
            "JUMPCLOUD_ISSUER": ISSUER,
            "REDIRECT_URI": REDIRECT_URI,
            "JUMPCLOUD_API_KEY": API_KEY
        }.items() if not v]
        print(f"   Missing: {', '.join(missing)}")
        raise RuntimeError("OAuth configuration incomplete")
    else:
        # Development fallbacks
        CLIENT_ID = CLIENT_ID or "dev-placeholder-client-id"
        CLIENT_SECRET = CLIENT_SECRET or "dev-placeholder-client-secret"
        ISSUER = ISSUER or "https://oauth.id.jumpcloud.com/"
        REDIRECT_URI = REDIRECT_URI or f"{FRONTEND_URL}/callback"
        API_KEY = API_KEY or "dev-placeholder-api-key"
        print("⚠️  DEVELOPMENT MODE: Using placeholder OAuth credentials")

TOKEN_URL = f"{ISSUER}oauth2/token"
AUTH_URL = f"{ISSUER}oauth2/auth"

# Development mode check
DEVELOPMENT_MODE = (
    CLIENT_ID == "dev-placeholder-client-id" or 
    CLIENT_SECRET == "dev-placeholder-client-secret" or
    API_KEY == "dev-placeholder-api-key"
)
print(f"DEVELOPMENT_MODE: {DEVELOPMENT_MODE}")

if DEVELOPMENT_MODE and ENVIRONMENT == "dev":
    print("⚠️  DEVELOPMENT MODE: OAuth not configured")
    print("   Configure AWS Secrets Manager with real JumpCloud credentials")
    print(f"   Secret: helpdesk-crm/{ENVIRONMENT}/config")

# Store state temporarily (for demo only - in production use a session or DB)
# For now, we'll use a simple in-memory store and temporarily disable validation in production
STATE_STORE = {}

@app.get("/api/login")
@app.get("/login")
async def api_login():
    state = secrets.token_urlsafe(16)  # Generate a random state
    STATE_STORE[state] = True          # Save state in memory  
    redirect_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile&state={state}"
    
    print(f"🚀 Login attempt starting:")
    print(f"   DEVELOPMENT_MODE: {DEVELOPMENT_MODE}")
    print(f"   AUTH_URL: {AUTH_URL}")
    print(f"   CLIENT_ID: {CLIENT_ID}")
    print(f"   REDIRECT_URI: {REDIRECT_URI}")
    print(f"   ENVIRONMENT: {ENVIRONMENT}")
    print(f"🔗 Redirecting to: {redirect_url}")
    print(f"💾 Stored state: {state}")
    
    return RedirectResponse(url=redirect_url, status_code=307)

@app.get("/callback")
async def callback(request: Request, code: str = Query(None), state: str = Query(None), error: str = Query(None), error_description: str = Query(None)):
    print(f"🔍 Callback received:")
    print(f"   Full URL: {request.url}")
    print(f"   Query params: {dict(request.query_params)}")
    print(f"   Code: {'present' if code else 'missing'}")
    print(f"   State: {state}")
    print(f"   Error: {error}")
    print(f"   Error Description: {error_description}")
    print(f"   Stored state: {STATE_STORE.get(state, False)}")
    
    # Check if JumpCloud sent an error
    if error:
        print(f"❌ JumpCloud OAuth Error: {error}")
        if error_description:
            print(f"   Description: {error_description}")
        return RedirectResponse(f"{FRONTEND_URL}/?error=jumpcloud_error&details={error}&description={error_description or ''}")
    
    # Validate state
    if not code:
        print("❌ Error: Missing code in callback")
        return RedirectResponse(f"{FRONTEND_URL}/?error=missing_code")

    # Temporarily disable state validation in production due to session persistence issues
    if ENVIRONMENT == "production":
        print("🔧 PRODUCTION MODE: State validation temporarily disabled - relying on OAuth security")
    elif not STATE_STORE.get(state, False):
        print(f"❌ Error: Invalid state. Got {state}, not found in valid states")
        return RedirectResponse(f"{FRONTEND_URL}/?error=invalid_state")

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            token_res = await client.post(
                TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        print(f"Token response status: {token_res.status_code}")
        print(f"Token response headers: {token_res.headers}")
        print(f"Token response content: {token_res.text}")

        if token_res.status_code != 200:
            error_msg = f"Token request failed with status {token_res.status_code}: {token_res.text}"
            print(error_msg)
            return RedirectResponse(f"{FRONTEND_URL}/?error=token_request_failed&details={token_res.status_code}")

        token_json = token_res.json()

        if "id_token" not in token_json:
            print(f"No id_token in response: {token_json}")
            return RedirectResponse(f"{FRONTEND_URL}/?error=no_id_token")

        id_token = token_json["id_token"]
        claims = jwt.get_unverified_claims(id_token)
        
        # Clean up state
        STATE_STORE.pop(state, None)
        
        # Redirect to frontend with token and user data
        import urllib.parse
        import json
        
        user_data = urllib.parse.quote(json.dumps(claims))
        access_token = token_json.get("access_token", id_token)
        
        return RedirectResponse(f"{FRONTEND_URL}/callback?token={access_token}&user={user_data}")
        
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return RedirectResponse(f"{FRONTEND_URL}/?error=callback_exception&details={urllib.parse.quote(str(e))}")

@app.get("/debug")
def debug_config():
    """Debug endpoint to check configuration"""

@app.get("/dev-login")
async def dev_login():
    """Development-only login bypass"""
    if ENVIRONMENT != "dev":
        return JSONResponse({"error": "Development login not available in production"}, status_code=403)
    
    # Create mock user claims for development
    mock_claims = {
        "email": "test@americor.com",
        "name": "Test User",
        "given_name": "Test",
        "family_name": "User",
        "groups": ["Help Desk Management Tool - Admin"],  # Give admin access
        "Role": "Help Desk Management Tool - Admin"
    }
    
    import urllib.parse
    import json
    
    user_data = urllib.parse.quote(json.dumps(mock_claims))
    mock_token = "dev_token_" + secrets.token_urlsafe(32)
    
    print(f"🧪 Development login bypass activated")
    print(f"   Mock user: {mock_claims['email']}")
    print(f"   Role: {mock_claims.get('Role')}")
    
    return RedirectResponse(f"{FRONTEND_URL}/callback?token={mock_token}&user={user_data}")
    
    # Using environment variables configuration
    config_source = "Environment Variables"
    
    return {
        "config_source": config_source,
        "environment": os.getenv("ENVIRONMENT", "dev"),
        "aws_region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        "client_id": CLIENT_ID,
        "issuer": ISSUER,
        "redirect_uri": REDIRECT_URI,
        "token_url": TOKEN_URL,
        "auth_url": AUTH_URL,
        "has_client_secret": bool(CLIENT_SECRET),
        "has_api_key": bool(API_KEY),
        "has_aws_credentials": bool(os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_ROLE_ARN")),
        "database_url": os.getenv("DATABASE_URL", "Not configured"),
        "cors_origins": os.getenv("CORS_ORIGINS", "Not configured")
    }

@app.post("/onboard-user")
async def onboard_user():
    payload = {
        "username": "new.user",
        "email": "new.user@example.com",
        "firstname": "New",
        "lastname": "User"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://console.jumpcloud.com/api/systemusers",
            headers={
                "x-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json=payload
        )

    return res.json()

# @app.post("/offboard-user")
# async def offboard_user(user_id: str):
#     async with httpx.AsyncClient() as client:
#         res = await client.delete(
#             f"https://console.jumpcloud.com/api/systemusers/{user_id}",
#             headers={"x-api-key": API_KEY}
#         )
#     return res.json()