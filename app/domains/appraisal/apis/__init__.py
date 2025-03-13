from fastapi import APIRouter

from .appraisal import appraisal_router
from .appraisal_comment import appraisal_comment_router
from .appraisal_input import appraisal_input_router
from .appraisal_submission import appraisal_submission_router, appraisal_summary_router
from .appraisal_template import appraisal_template_router
from .department_group import department_group_router

appraisal_routers = APIRouter(prefix='/appraisals')
appraisal_routers.include_router(appraisal_router, tags=["APPRAISAL"])
appraisal_routers.include_router(appraisal_comment_router, tags=["APPRAISAL COMMENTS"])
appraisal_routers.include_router(appraisal_input_router, tags=["APPRAISAL INPUTS"])
appraisal_routers.include_router(appraisal_submission_router, tags=["APPRAISAL SUBMISSIONS"])
appraisal_routers.include_router(appraisal_template_router, tags=["APPRAISAL TEMPLATES"])
appraisal_routers.include_router(appraisal_summary_router, tags=["APPRAISAL SUMMARIES"])
appraisal_routers.include_router(department_group_router, tags=["DEPARTMENT GROUPS"])
