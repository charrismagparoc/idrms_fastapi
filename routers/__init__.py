from routers.auth_router                import router as auth_router
from routers.incidents_router           import router as incidents_router
from routers.alerts_router              import router as alerts_router
from routers.evacuation_centers_router  import router as evacuation_centers_router
from routers.residents_router           import router as residents_router
from routers.resources_router           import router as resources_router
from routers.users_router               import router as users_router
from routers.activity_log_router        import router as activity_log_router
from routers.dashboard_router           import router as dashboard_router
from routers.reports_router             import router as reports_router
from routers.map_router                 import router as map_router
from routers.risk_router                import router as risk_router
from routers.predict_router             import router as predict_router

__all__ = [
    "auth_router",
    "incidents_router",
    "alerts_router",
    "evacuation_centers_router",
    "residents_router",
    "resources_router",
    "users_router",
    "activity_log_router",
    "dashboard_router",
    "reports_router",
    "map_router",
    "risk_router",
    "predict_router",
]