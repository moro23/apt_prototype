from db.base_class import APIBase, UUID
from sqlalchemy import Column, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

appraisal_submission_comments = Table(
    'appraisal_submission_comments',
    APIBase.metadata,
    Column('comment_id', UUID(as_uuid=True), ForeignKey('appraisal_comments.id'), primary_key=True),
    Column('submission_id', UUID(as_uuid=True), ForeignKey('appraisal_submissions.id'), primary_key=True)
)


class AppraisalComment(APIBase):
    organization_id = Column(UUID(as_uuid=True), ForeignKey("public.organizations.id"))

    content = Column(Text, nullable=False)
    commenter_id = Column(UUID(as_uuid=True), ForeignKey("staffs.id"))

    submissions = relationship(
        "AppraisalSubmission", secondary=appraisal_submission_comments, back_populates="comments"
    )
