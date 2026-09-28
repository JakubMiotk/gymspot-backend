from fastapi import APIRouter, Depends
from app.api.routes import auth, users, persons, relations, trainings, measurements, payments, scan, debts, excess_payments, documentation, notifications, exercises
from app.core.deps import get_current_user

api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
authenticated = [Depends(get_current_user)]

# Logowanie i rejestracja pozostają publiczne; pozostałe endpointy wymagają tokenu.
api_router.include_router(users.router, prefix="/users", tags=["users"], dependencies=authenticated)
api_router.include_router(persons.router, prefix="/persons", tags=["persons"], dependencies=authenticated)
api_router.include_router(relations.router, prefix="/relations", tags=["relations"], dependencies=authenticated)
api_router.include_router(trainings.router, prefix="/trainings", tags=["trainings"], dependencies=authenticated)
api_router.include_router(measurements.router, prefix="/measurements", tags=["measurements"], dependencies=authenticated)
api_router.include_router(payments.router, prefix="/payments", tags=["payments"], dependencies=authenticated)
api_router.include_router(scan.router, prefix="/scan", tags=["scan"], dependencies=authenticated)
api_router.include_router(debts.router, prefix="/debts", tags=["debts"], dependencies=authenticated)
api_router.include_router(excess_payments.router, prefix="/excess-payments", tags=["excess_payments"], dependencies=authenticated)
api_router.include_router(documentation.router, tags=["documentation"], dependencies=authenticated)
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"], dependencies=authenticated)
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"], dependencies=authenticated)
