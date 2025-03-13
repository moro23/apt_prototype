from fastapi import APIRouter

from domains.appraisal.apis import appraisal_routers
from domains.auth.apis import auth_routers
from domains.organization.apis import organization_routers
from domains.staff.apis import staff_routers

router = APIRouter()
router.include_router(auth_routers)
router.include_router(organization_routers)
router.include_router(staff_routers)
router.include_router(appraisal_routers)
