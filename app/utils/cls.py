import datetime
from functools import wraps
from inspect import Parameter, Signature, signature
from typing import List

from fastapi import Query

from utils.constants import DT_X, Q_X


class ContentQueryChecker:
    def __init__(self, cols=None, actions=None, exclude: List[str] = []):
        self._cols = [col for col in cols if col[0] not in exclude]
        self._actions = actions

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        sig = signature(wrapper)
        params = list(sig._parameters.values())
        # Remove the existing **kwargs param from the function signature
        if params:
            del params[-1]

        # Build optional regex strings (if you really need them elsewhere)
        sort_str = "|".join([f"{x[0]}|-{x[0]}" for x in self._cols]) if self._cols else None
        q_str = "|".join([x[0] for x in self._cols if x[0] != 'password']) if self._cols else None

        # Dynamically add query parameters for columns
        if self._cols:
            # Non-datetime columns
            params.extend([
                Parameter(
                    param[0],
                    Parameter.KEYWORD_ONLY,
                    annotation=param[1],
                    default=Query(None)
                ) for param in self._cols if param[1] != datetime.datetime
            ])

            # Datetime columns
            params.extend([
                Parameter(
                    param[0],
                    Parameter.KEYWORD_ONLY,
                    annotation=List[str],
                    default=Query(None, regex=DT_X)
                ) for param in self._cols if param[1] == datetime.datetime
            ])

        # Add shared query parameters
        params.extend([
            Parameter('offset', Parameter.KEYWORD_ONLY, annotation=int, default=Query(0, gte=0)),
            Parameter('limit', Parameter.KEYWORD_ONLY, annotation=int, default=Query(100, gt=0)),

            Parameter(
                'fields',
                Parameter.KEYWORD_ONLY,
                annotation=List[str],
                default=Query(None, regex=f'({q_str})$') if q_str else Query(None)
            ),

            Parameter(
                'q',
                Parameter.KEYWORD_ONLY,
                annotation=List[str],
                default=Query(
                    None,
                    regex=Q_X.format(cols=f'({q_str})') if q_str else '^[\\w]+$|^[\\w]+:[\\w]+$'
                )
            ),

            # IMPORTANT: remove regex here so each item can be validated as a simple string
            Parameter(
                'sort',
                Parameter.KEYWORD_ONLY,
                annotation=List[str],
                default=Query(None)
            ),
        ])

        # Optionally add 'action' if needed
        if self._actions:
            params.append(
                Parameter('action', Parameter.KEYWORD_ONLY, annotation=str, default=Query(None))
            )

        wrapper.__signature__ = Signature(params)
        return wrapper


from config.settings import settings
import sqlalchemy.types as types
# from cls import Upload
import pathlib


class Upload:
    def __init__(self, file, upload_to, size=None):
        self.file = file
        self.upload_to = upload_to
        self.size = size

    def _ext(self):
        return pathlib.Path(self.file.filename).suffix


class File(types.TypeDecorator):
    impl = types.String
    cache_ok = False

    def __init__(self, *args, upload_to, size=None, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.upload_to = upload_to
        self.size = size

    def process_bind_param(self, value, dialect):
        if not value:
            return None
        file = Upload(value, upload_to=self.upload_to, size=self.size)
        url = file.save()
        return url

    def process_result_value(self, value, dialect):
        if value:
            if value[:3] == 'S3:':
                return settings.AWS_S3_CUSTOM_DOMAIN + value[3:]
            return settings.BASE_URL + value[3:]
        else:
            return None
