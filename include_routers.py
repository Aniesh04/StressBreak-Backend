from fastapi import FastAPI

def include_all_routers(app: FastAPI):
    """Include all API routers in the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Import all routers
    from routers import auth, users, journals, recommendations, analytics
    
    # Include all routers (prefixes and tags are defined in the router files)
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(journals.router)
    app.include_router(recommendations.router)
    app.include_router(analytics.router)
