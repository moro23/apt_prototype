from crud.base import CRUDBase
from domains.appraisal.models.appraisal_comment import AppraisalComment
from domains.appraisal.schemas.appraisal_comment import (
    AppraisalCommentCreate, AppraisalCommentUpdate
)


class CRUDAppraisalComment(CRUDBase[AppraisalComment, AppraisalCommentCreate, AppraisalCommentUpdate]):
    pass


appraisal_comment_actions = CRUDAppraisalComment(AppraisalComment)
