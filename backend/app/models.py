from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, func
from pydantic import ConfigDict, Field as PydanticField
from sqlmodel import Field, SQLModel


class FieldType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    DATE = "date"
    EMAIL = "email"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"


class FieldDefinition(SQLModel):
    name: str
    label: str
    field_type: FieldType = PydanticField(alias="type", validation_alias="type", serialization_alias="type")
    required: bool = False
    options: Optional[list[str]] = None
    placeholder: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class FormTemplateBase(SQLModel):
    name: str
    description: Optional[str] = None
    fields: list[FieldDefinition] = Field(sa_column=Column(JSON), default_factory=list)


class FormTemplate(FormTemplateBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    )

    model_config = ConfigDict(populate_by_name=True)


class FormTemplateCreate(FormTemplateBase):
    pass


class FormTemplateUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[list[FieldDefinition]] = None


class FormSubmissionBase(SQLModel):
    data: dict = Field(sa_column=Column(JSON), default_factory=dict)


class FormSubmission(FormSubmissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: int = Field(foreign_key="formtemplate.id")
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))


class FormSubmissionCreate(FormSubmissionBase):
    pass


class FormSubmissionRead(FormSubmissionBase):
    id: int
    template_id: int
    created_at: datetime


class FormTemplateRead(FormTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime


class FormTemplateWithSubmissions(FormTemplateRead):
    submissions: list[FormSubmissionRead]


FieldDefinition.model_rebuild()
FormTemplate.model_rebuild()
FormTemplateCreate.model_rebuild()
FormTemplateUpdate.model_rebuild()
FormTemplateRead.model_rebuild()
FormSubmission.model_rebuild()
FormSubmissionCreate.model_rebuild()
FormSubmissionRead.model_rebuild()
FormTemplateWithSubmissions.model_rebuild()
