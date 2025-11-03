from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_db
from app.models import (
    FieldDefinition,
    FormSubmission,
    FormSubmissionCreate,
    FormSubmissionRead,
    FormTemplate,
    FormTemplateCreate,
    FormTemplateRead,
    FormTemplateUpdate,
    FormTemplateWithSubmissions,
)
from app.services.validation import SubmissionValidator

router = APIRouter()


@router.post("/templates", response_model=FormTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(template_in: FormTemplateCreate, db: Session = Depends(get_db)) -> FormTemplate:
    template = FormTemplate(**template_in.model_dump(by_alias=True))
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/templates", response_model=List[FormTemplateRead])
def list_templates(db: Session = Depends(get_db)) -> List[FormTemplate]:
    return db.exec(select(FormTemplate)).all()


@router.get("/templates/{template_id}", response_model=FormTemplateWithSubmissions)
def get_template(template_id: int, db: Session = Depends(get_db)) -> FormTemplate:
    template = db.get(FormTemplate, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    submissions = db.exec(select(FormSubmission).where(FormSubmission.template_id == template_id)).all()
    normalized_fields = [
        field if isinstance(field, FieldDefinition) else FieldDefinition.model_validate(field)
        for field in template.fields
    ]
    template_data = template.model_dump(by_alias=True)
    template_data["fields"] = [field.model_dump(by_alias=True) for field in normalized_fields]

    return FormTemplateWithSubmissions(
        **template_data,
        submissions=[FormSubmissionRead.model_validate(submission) for submission in submissions],
    )


@router.get("/templates/{template_id}/render")
def render_template(template_id: int, db: Session = Depends(get_db)) -> dict:
    template = db.get(FormTemplate, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    normalized_fields = [
        field if isinstance(field, FieldDefinition) else FieldDefinition.model_validate(field)
        for field in template.fields
    ]

    return {
        "name": template.name,
        "description": template.description,
        "fields": [
            {
                "label": field.label,
                "type": field.field_type.value,
                "required": field.required,
                "placeholder": field.placeholder,
                "options": field.options,
            }
            for field in normalized_fields
        ],
    }


@router.put("/templates/{template_id}", response_model=FormTemplateRead)
def update_template(
    template_id: int,
    template_in: FormTemplateUpdate,
    db: Session = Depends(get_db),
) -> FormTemplate:
    template = db.get(FormTemplate, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    update_data = template_in.model_dump(exclude_unset=True, by_alias=True)
    for key, value in update_data.items():
        setattr(template, key, value)

    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: int, db: Session = Depends(get_db)) -> None:
    template = db.get(FormTemplate, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    db.delete(template)
    db.commit()


@router.post(
    "/templates/{template_id}/submissions",
    response_model=FormSubmissionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_submission(
    template_id: int, submission_in: FormSubmissionCreate, db: Session = Depends(get_db)
) -> FormSubmission:
    template = db.get(FormTemplate, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    validator = SubmissionValidator(template)
    validator.validate(submission_in.data)

    submission = FormSubmission(template_id=template_id, data=submission_in.data)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/templates/{template_id}/submissions", response_model=List[FormSubmissionRead])
def list_submissions(template_id: int, db: Session = Depends(get_db)) -> List[FormSubmission]:
    template = db.get(FormTemplate, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    statement = select(FormSubmission).where(FormSubmission.template_id == template_id)
    return db.exec(statement).all()


@router.get("/submissions/{submission_id}", response_model=FormSubmissionRead)
def get_submission(submission_id: int, db: Session = Depends(get_db)) -> FormSubmission:
    submission = db.get(FormSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return submission
