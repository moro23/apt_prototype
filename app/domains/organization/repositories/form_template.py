from crud.base import CRUDBase
from domains.organization.models.form_template import FormFieldTemplate
from domains.organization.schemas.form_template import (
    FormFieldTemplateCreate, FormFieldTemplateUpdate
)


class CRUDFormFieldTemplate(CRUDBase[FormFieldTemplate, FormFieldTemplateCreate, FormFieldTemplateUpdate]):
    pass


form_field_template_actions = CRUDFormFieldTemplate(FormFieldTemplate)
