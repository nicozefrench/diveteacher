"""
Sentry Integration

Initialize and configure Sentry for error tracking.
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration

from app.core.config import settings


def init_sentry():
    """
    Initialize Sentry SDK with FastAPI integration
    
    Call this once during app startup (see main.py)
    """
    
    if not settings.SENTRY_DSN_BACKEND:
        print("⚠️  Sentry DSN not configured - error tracking disabled")
        return
    
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN_BACKEND,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
            HttpxIntegration(),
        ],
        # Send personal identifiable information (for debugging)
        send_default_pii=True,
        # Attach stack traces to messages
        attach_stacktrace=True,
    )
    
    print(f"✅ Sentry initialized (environment: {settings.SENTRY_ENVIRONMENT})")

