from typing import Any, Dict, List

from fastapi import HTTPException, status

from app.models import FieldDefinition, FormTemplate


class SubmissionValidator:
    """Validate submission payloads against template field definitions."""

    def __init__(self, template: FormTemplate):
        self.template = template
        self.fields = [
            field if isinstance(field, FieldDefinition) else FieldDefinition.model_validate(field)
            for field in template.fields
        ]
        self.field_map = {field.name: field for field in self.fields}

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []

        for field in self.fields:
            if field.required and field.name not in data:
                errors.append(f"Missing required field '{field.name}'")
                continue

            if field.name not in data:
                continue

            value = data[field.name]
            validator = getattr(self, f"_validate_{field.field_type.value}", None)
            if validator and not validator(value, field):
                errors.append(f"Invalid value for field '{field.name}'")

        extra_fields = set(data.keys()) - set(self.field_map.keys())
        if extra_fields:
            errors.append(f"Unknown fields supplied: {', '.join(sorted(extra_fields))}")

        if errors:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=errors)

        return data

    @staticmethod
    def _validate_text(value: Any, field: FieldDefinition) -> bool:
        return isinstance(value, str)

    @staticmethod
    def _validate_textarea(value: Any, field: FieldDefinition) -> bool:
        return isinstance(value, str)

    @staticmethod
    def _validate_email(value: Any, field: FieldDefinition) -> bool:
        return isinstance(value, str) and "@" in value

    @staticmethod
    def _validate_number(value: Any, field: FieldDefinition) -> bool:
        return isinstance(value, (int, float))

    @staticmethod
    def _validate_date(value: Any, field: FieldDefinition) -> bool:
        return isinstance(value, str)

    @staticmethod
    def _validate_select(value: Any, field: FieldDefinition) -> bool:
        return isinstance(value, str) and (field.options is None or value in field.options)

    @staticmethod
    def _validate_checkbox(value: Any, field: FieldDefinition) -> bool:
        return isinstance(value, bool)
