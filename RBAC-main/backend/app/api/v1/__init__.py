from fastapi import APIRouter
from app.api.v1 import auth, users, departments, roles, scopes, records, edit_requests, audit, topiclens

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(scopes.router, prefix="/scopes", tags=["scopes"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(records.router, prefix="/records", tags=["records"])
api_router.include_router(edit_requests.router, prefix="/edit-requests", tags=["edit-requests"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(topiclens.router, prefix="/topiclens", tags=["topiclens"])