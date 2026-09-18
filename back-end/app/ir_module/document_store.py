from sqlalchemy.orm import Session, load_only

from app.models import (
    DrugInformationDocument,
    SafetyDocument,
)


def get_all_documents(db: Session, include_pdf: bool = False):
    drug_documents = (
        db.query(DrugInformationDocument)
        .options(*([] if include_pdf else [load_only(DrugInformationDocument.id, DrugInformationDocument.title)]))
        .all()
    )

    safety_documents = (
        db.query(SafetyDocument)
        .options(*([] if include_pdf else [load_only(SafetyDocument.id, SafetyDocument.title)]))
        .all()
    )

    documents = []

    for document in drug_documents:
        documents.append(
            {
                "id": document.id,
                "title": document.title,
                "document_type": "drug_information",
            }
        )
        if include_pdf:
            documents[-1]["pdf_file"] = document.pdf_file

    for document in safety_documents:
        documents.append(
            {
                "id": document.id,
                "title": document.title,
                "document_type": "safety",
            }
        )
        if include_pdf:
            documents[-1]["pdf_file"] = document.pdf_file

    return documents