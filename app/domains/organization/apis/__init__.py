from domains.organization.apis.bill import bill_router
from domains.organization.apis.organization import organization_router
from domains.organization.apis.organization_branch import organization_branch_router
from domains.organization.apis.organization_settings import organization_settings_router
from domains.organization.apis.payment import payment_router
from domains.organization.apis.tenancy import tenancy_router
from domains.organization.apis.terms_and_conditions import terms_and_conditions_router
from fastapi import APIRouter

organization_routers = APIRouter(prefix="/organizations")
organization_routers.include_router(organization_router, tags=['ORGANIZATIONS'])
organization_routers.include_router(bill_router, tags=['ORGANIZATION BILLS'])
organization_routers.include_router(organization_branch_router, tags=['ORGANIZATION BRANCH'])
organization_routers.include_router(payment_router, tags=['ORGANIZATION PAYMENTS'])
organization_routers.include_router(tenancy_router, tags=['ORGANIZATION TENANTS'])
organization_routers.include_router(terms_and_conditions_router, tags=['ORGANIZATION TERMS AND CONDITIONS'])
organization_routers.include_router(organization_settings_router, tags=['ORGANIZATION SETTINGS'])
