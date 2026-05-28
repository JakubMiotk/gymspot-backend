import os
from fastapi import APIRouter
from app.api.routes import auth, users, persons, relations, trainings, measurements, payments, scan, debts, excess_payments, documentation, notifications

api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(persons.router, prefix="/persons", tags=["persons"])
api_router.include_router(relations.router, prefix="/relations", tags=["relations"])
api_router.include_router(trainings.router, prefix="/trainings", tags=["trainings"])
api_router.include_router(measurements.router, prefix="/measurements", tags=["measurements"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(scan.router, prefix="/scan", tags=["scan"])
api_router.include_router(debts.router, prefix="/debts", tags=["debts"])
api_router.include_router(excess_payments.router, prefix="/excess-payments", tags=["excess_payments"])
api_router.include_router(documentation.router, tags=["documentation"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
