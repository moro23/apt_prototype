from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, DateTime, JSON, String, Boolean
from sqlalchemy.orm import relationship

from db.base_class import APIBase, UUID
from domains.appraisal.models.appraisal_comment import appraisal_submission_comments


class AppraisalSubmission(APIBase):
    appraisal_input_id = Column(UUID, ForeignKey('appraisal_inputs.id'), nullable=False)
    appraisal_id = Column(UUID, ForeignKey('appraisals.id'), nullable=False)
    staff_id = Column(UUID, ForeignKey("staffs.id"))

    data = Column(JSON, nullable=False)  # JSON field to store submitted data

    status = Column(String, default="STARTED")  # COMPLETED, SUBMITTED, REVIEWED
    started_at = Column(DateTime, default=datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    submitted_at = Column(DateTime, nullable=True)
    submitted = Column(Boolean, default=False)
    reviewed_at = Column(DateTime, nullable=True)

    comments = relationship(
        "AppraisalComment", secondary=appraisal_submission_comments, back_populates="submissions"
    )
    appraisal_input = relationship(
        "AppraisalInput", foreign_keys="AppraisalSubmission.appraisal_input_id", back_populates="submissions"
    )
    appraisal = relationship(
        "Appraisal", foreign_keys="AppraisalSubmission.appraisal_id", back_populates="submissions"
    )
    staff = relationship(
        "Staff", foreign_keys="AppraisalSubmission.staff_id", back_populates="appraisal_submissions"
    )
