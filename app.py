# app.py — Adika Marketplace Flask entry (routes registered via api_service.register_routes)
"""
NOTE: Listing feed, FYP, and category endpoints live in api_service.py.
This module is a thin entrypoint so deployments that import `app` keep working.
"""
from __future__ import annotations

import os
import logging

logger = logging.getLogger(__name__)

try:
    from flask import Flask
except ImportError:
    Flask = None  # type: ignore


def create_app():
    if Flask is None:
        raise RuntimeError("Flask is required")
    application = Flask(__name__)
    application.config["JSON_AS_ASCII"] = False  # preserve Amharic UTF-8

    # Register API routes from api_service
    try:
        import api_service
        if hasattr(api_service, "register_routes"):
            api_service.register_routes(application)
        elif hasattr(api_service, "init_app"):
            api_service.init_app(application)
        else:
            # Fallback: many Adika deployments call register_api_routes(web_app)
            for name in ("register_api_routes", "setup_routes", "attach_routes"):
                fn = getattr(api_service, name, None)
                if callable(fn):
                    fn(application)
                    break
    except Exception as e:
        logger.error("Failed to register api_service routes: %s", e)

    @application.get("/health")
    def health():
        return {"ok": True, "service": "adika", "fyp_default": True}

    return application


app = create_app() if Flask is not None else None

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
