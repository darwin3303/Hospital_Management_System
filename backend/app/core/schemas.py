import uuid

from pydantic import BaseModel, ConfigDict, model_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def _stringify_uuids(cls, data):
        if isinstance(data, dict):
            return data
        result = {}
        for field_name in cls.model_fields:
            if hasattr(data, field_name):
                value = getattr(data, field_name)
                result[field_name] = str(value) if isinstance(value, uuid.UUID) else value
        return result