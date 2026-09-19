"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import auth_routes, admin_routes, plans_routes, payment_routes, subscription_routes, analytics_routes
from src.config import settings

app = FastAPI(
    title="SubSphere Platform API",
    description="High-performance API for managing billing, subscriptions, plans, and subscriber analytics",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(plans_routes.router)
app.include_router(payment_routes.router)
app.include_router(subscription_routes.router)
app.include_router(analytics_routes.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SubSphere Core API",
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "SubSphere Billing & Subscription Engine",
        "version": "2.0.0",
        "docs": "/docs"
    }

