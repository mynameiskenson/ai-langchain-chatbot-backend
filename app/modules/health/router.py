from fastapi import APIRouter, Depends

from app.schemas.response import ApiResponse

from app.core.dependencies import get_health_service

from app.modules.health.service import HealthService
from app.modules.health.schemas import HealthCheckResponse, DatabaseHealthCheckResponse

health_router = APIRouter()

@health_router.get("/health", response_model=ApiResponse[HealthCheckResponse], summary="Health Check", description="Check the health status of the backend service.")
async def health_check(
    service: HealthService = Depends(
            get_health_service
        )
    
    ):
    result = service.check_health()

    return ApiResponse(
        data=HealthCheckResponse(**result)
    )

@health_router.get("/health/database", response_model=ApiResponse[DatabaseHealthCheckResponse], summary="Database Health Check", description="Check the health status of the database.")
async def database_health_check(
    service: HealthService = Depends(get_health_service)
):
    result = await service.check_database_health()
    return ApiResponse(
        data=DatabaseHealthCheckResponse(**result)
    )