from uuid import uuid4
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from domains.auth.models.users import User
from passlib.context import CryptContext
from domains.auth.models.role_permissions import Role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SystemAdmin:
    System_ADMIN_NAME: str =
    System_ADMIN_EMAIL: str = 
    System_ADMIN_PASSWORD: str = 


    Super_ADMIN_NAME: str = 
    Super_ADMIN_EMAIL: str = 
    Super_ADMIN_PASSWORD: str =



async def create_system_admin(db: AsyncSession):

    existing_role = await db.execute(select(Role).where(Role.name == "System Administrator"))
    existing_role = existing_role.scalars().first()
    if not existing_role:
        system_admin_role = Role(id=uuid4(), name="System Administrator")
        db.add(system_admin_role)
        await db.commit()
        await db.refresh(system_admin_role)
    else:
        system_admin_role = existing_role


    # Check if System Admin already exists
    result = await db.execute(select(User).filter(User.email == SystemAdmin.System_ADMIN_EMAIL))
    system_admin = result.scalars().first()

    # Check if Super Admin already exists
    result = await db.execute(select(User).filter(User.email == SystemAdmin.Super_ADMIN_EMAIL))
    super_admin = result.scalars().first()


    if super_admin:
        return

    # system_admin_in = User(
    #     username=SystemAdmin.System_ADMIN_NAME,
    #     email=SystemAdmin.System_ADMIN_EMAIL,
    #     password=pwd_context.hash(SystemAdmin.System_ADMIN_PASSWORD),
    #     organization_id=None,
    #     role_id = system_admin_role.id
    # )

    # db.add(system_admin_in)
    # await db.commit()
    # await db.refresh(system_admin_in)



    super_admin_in = User(
        username=SystemAdmin.Super_ADMIN_NAME,
        email=SystemAdmin.Super_ADMIN_EMAIL,
        password=pwd_context.hash(SystemAdmin.Super_ADMIN_PASSWORD),
        organization_id=None,
        role_id = system_admin_role.id
    )

    db.add(super_admin_in)
    await db.commit()
    await db.refresh(super_admin_in)














# from fastapi import FastAPI, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from pydantic import UUID4
# from uuid import uuid4
# from sqlalchemy.exc import SQLAlchemyError
# # Assuming the correct import for Role and Permission models
# # from domains.appraisal.models.roles import Role
# # from domains.appraisal.models.permissions import Permission
# from domains.appraisal.models.staff_role_permissions import Role, Permission
# from domains.auth.models.users import User
# from domains.auth.schemas.user_account import UserCreate
# from utils.security import pwd_context


# SUPER_ADMIN_NAME: str = "Super Administrator"
# SUPER_ADMIN_PHONE_NUMBER: str = "9876543210"
# SUPER_ADMIN_EMAIL: str = "superadmin@admin.com"
# SUPER_ADMIN_PASSWORD: str = "openforme"
# SUPER_ADMIN_ROLE: str = "Super Admin"

# Staff_NAME: str = "Staff"
# Staff_PHONE_NUMBER: str = "9876543211"
# Staff_EMAIL: str = "staff@admin.com"
# Staff_PASSWORD: str = "openforme"
# Staff_ROLE: str = "Staff"

# Supervisor_NAME: str = "Supervisor"
# Supervisor_PHONE_NUMBER: str = "9876543212"
# Supervisor_EMAIL: str = "supervisor@admin.com"
# Supervisor_PASSWORD: str = "openforme"
# Supervisor_ROLE: str = "Supervisor"

# HR_NAME: str = "Human Resource"
# HR_PHONE_NUMBER: str = "9876543213"
# HR_EMAIL: str = "hr@admin.com"
# HR_PASSWORD: str = "openforme"
# HR_ROLE: str = "HR"

# SUPER_ADMIN_STATUS: bool = True


# def init_db(db: Session):
#     """
#     Initialize the database with predefined roles and permissions.
#     """
#     roles_permissions = {
#         "Super Admin": [
#             "createDepartment", "readDepartment", "updateDepartment", "deleteDepartment", 
#              "readAllStaffUnderDepartment", "createStaff", "readStaff",
#             "updateStaff", "deleteStaff",  "uploadStaff", "readAppraisalCycle",
#              "readAppraisalConfiguration", "searchAppraisalConfigurationByKeyword", 
#              "readAppraisalSection",  
#             "readCompetencyBank",  "readStaffDeadline",  
#             "readKRABank",  "readRolePermission",  
#             "readRoles",  "updateRole", "addPermissionToRole", "readPermissions", 
#             "updatePermission"
#         ],
#         "HR": [
#         "createDepartment","readDepartment","updateDepartment", "deleteDepartment",
#         "readAllStaffUnderDepartment","createStaff","readStaff","updateStaff","deleteStaff",
#         "uploadStaff","createAppraisalCycle","readAppraisalCycle", "updateAppraisalCycle",
#         "deleteAppraisalCycle","readAppraisalConfiguration","updateAppraisalConfiguration",
#         "searchAppraisalConfigurationByKeyword","deleteAppraisalConfiguration",
#         "readAppraisalSection","readCompetencyBank","submitAppraisalForm",
#         "readAppraisalForm","createAppraisalSubmission","readAppraisalSubmission",
#         "updateAppraisalSubmission","readStaffPermission","updateStaffPermission",
#         "deleteStaffPermission","readStaffDeadline",
#         "readKRABank", "readRolePermission","removeRolePermission",
#         "readRoles","updateRole","addPermissionToRole","readPermissions",
#         "updatePermission", "approveAppraisal","commentAppraisal"
#         ],
#         "Staff": [
#            "readDepartment", "readAppraisalCycle", "readAppraisalConfiguration",
#            "eadAppraisalSection","readCompetencyBank",
#            "readAppraisalForm","updateAppraisalForm",
#            "submitAppraisalForm","readAppraisalSubmission","updateAppraisalSubmission",
#            "createStaffDeadline"
#         ],
#         "Supervisor": [
#         "readDepartment", "readAllStaffUnderDepartment", "readStaff",
#         "readAppraisalCycle","createAppraisalConfiguration","readAppraisalConfiguration",
#         "updateAppraisalConfiguration","searchAppraisalConfigurationByKeyword","deleteAppraisalConfiguration",
#         "createAppraisalSection","readAppraisalSection","upateAppraisalSection","deleteAppraisalSection",
#         "createCompetencyBank","readCompetencyBank","updateCompetencyBank","deletCompetencyBank",
#         "createAppraisalForm","readAppraisalForm","updateAppraisalForm",
#         "createAppraisalSubmission","readAppraisalSubmission","updateAppraisalSubmission",
#         "createStaffDeadline","readStaffDeadline","updateStaffDeadline",
#         "createKRABank","readKRABank","updateKRABank","submitAppraisalForm",
#         "deleteKRABank","approveAppraisal","commentAppraisal"
#         ]
#     }

#     try:
#         # Create roles and permissions
#         for role_name, permission_names in roles_permissions.items():
#             # Check if the role already exists
#             role = db.query(Role).filter(Role.name == role_name).first()
#             if not role:
#                 # Create the role if it doesn't exist
#                 role = Role(id=uuid4(), name=role_name)
#                 db.add(role)

#             # Check and assign permissions
#             for perm_name in permission_names:
#                 try:
#                     permission = db.query(Permission).filter(Permission.name == perm_name).first()
#                     if not permission:
#                         # Create permission if it doesn't exist
#                         permission = Permission(id=uuid4(), name=perm_name)
#                         db.add(permission)
#                         db.flush()  # Flushes the changes to the DB before committing
#                         # return f"Created permission: {perm_name}"  # Debug log
#                     else:
#                         pass
#                         # return f"Permission {perm_name} already exists"  # Debug log
#                         # return f"Permission {perm_name} already exists"  # Debug log

#                     # Assign permission to the role if not already assigned
#                     if permission not in role.permissions:
#                         role.permissions.append(permission)
#                 except IntegrityError:
#                     db.rollback()  # Roll back the transaction in case of duplicate
#                     # return f"IntegrityError: Permission {perm_name} already exists. Skipping."
            
#         # Commit the role-permission association to the database once
#         db.commit()
#         return "Roles and permissions initialized successfully."
    
#     except SQLAlchemyError as e:
#         db.rollback()
#         return f"Error initializing roles and permissions: {str(e)}"

# def create_super_admin(db: Session):
#     """
#     Create the initial super admin user if they don't exist.
    
#     """
    
#     try:
#         # Check if super admin user exists
#         admin = db.query(User).filter(User.email == SUPER_ADMIN_EMAIL).first()
#         staff = db.query(User).filter(User.email == Staff_EMAIL).first()
#         supervisor = db.query(User).filter(User.email == Supervisor_EMAIL).first()
#         hr = db.query(User).filter(User.email == HR_EMAIL).first()
        
#         # Check if super admin role exists
#         role = db.query(Role).filter(Role.name == 'Super Admin').first()
#         staff_role = db.query(Role).filter(Role.name == 'Staff').first()
#         supervisor_role = db.query(Role).filter(Role.name == 'Supervisor').first()
#         hr_role = db.query(Role).filter(Role.name == 'HR').first()
        
#         if not role:
#             raise HTTPException(status_code=400, detail="Super Admin role not found")
        
#         # If the super admin doesn't exist, create it
#         if not admin and not staff and not supervisor and not hr:
#             admin_in = User(
#                 email=SUPER_ADMIN_EMAIL,
#                 password=pwd_context.hash(SUPER_ADMIN_PASSWORD),
#                 reset_password_token=None,
#                 staff_id=None,
#                 role_id=role.id
#             )
#             db.add(admin_in)
#             db.commit()
#             db.refresh(admin_in)
#             print("Super admin user created successfully.")

#             staff_in = User(
#                 email=Staff_EMAIL,
#                 password=pwd_context.hash(Staff_PASSWORD),
#                 reset_password_token=None,
#                 staff_id=None,
#                 role_id=staff_role.id
#             )
#             db.add(staff_in)
#             db.commit()
#             db.refresh(staff_in)


#             supervisor_in = User(
#                 email=Supervisor_EMAIL,
#                 password=pwd_context.hash(Supervisor_PASSWORD),
#                 reset_password_token=None,
#                 staff_id=None,
#                 role_id=supervisor_role.id
#             )
#             db.add(supervisor_in)
#             db.commit()
#             db.refresh(supervisor_in)



#             hr_role = User(
#                 email=HR_EMAIL,
#                 password=pwd_context.hash(Supervisor_PASSWORD),
#                 reset_password_token=None,
#                 staff_id=None,
#                 role_id=hr_role.id
#             )
#             db.add(hr_role)
#             db.commit()
#             db.refresh(hr_role)
    
#     except SQLAlchemyError as e:
#         db.rollback()
#         print(f"Error creating super admin: {str(e)}")
