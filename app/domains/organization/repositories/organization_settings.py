from crud.base import CRUDBase
from domains.organization.models.organization_settings import OrganizationSettings
from domains.organization.schemas.organization_settings import OrganizationSettingsCreate, OrganizationSettingsUpdate


class CRUDOrganizationSettings(CRUDBase[OrganizationSettings, OrganizationSettingsCreate, OrganizationSettingsUpdate]):
    pass


organization_settings_actions = CRUDOrganizationSettings(OrganizationSettings)
