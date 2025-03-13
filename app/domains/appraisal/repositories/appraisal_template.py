from crud.base import CRUDBase
from domains.appraisal.models.appraisal_template import AppraisalTemplate
from domains.appraisal.schemas.appraisal_template import (
    AppraisalTemplateCreate, AppraisalTemplateUpdate
)


class CRUDAppraisalTemplate(CRUDBase[AppraisalTemplate, AppraisalTemplateCreate, AppraisalTemplateUpdate]):
    pass


appraisal_template_actions = CRUDAppraisalTemplate(AppraisalTemplate)
