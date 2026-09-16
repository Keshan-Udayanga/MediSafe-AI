from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.auth import SECRET_KEY
from app.database import get_db
from app.models import DrugInformationDocument, SafetyDocument, User


router = APIRouter(prefix="/api/admin/drug-information-documents", tags=["Drug Information Documents"])
bearer_scheme = HTTPBearer(auto_error=False)


def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if user is None or user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    return user


@router.get("")
def list_documents(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    documents = (
        db.query(DrugInformationDocument)
        .order_by(DrugInformationDocument.id.desc())
        .all()
    )
    return [{"id": document.id, "title": document.title} for document in documents]


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted")

    pdf_bytes = await file.read()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The selected file is not a valid PDF")

    document = DrugInformationDocument(title=filename, pdf_file=pdf_bytes)
    db.add(document)
    db.commit()
    db.refresh(document)
    return {"id": document.id, "title": document.title}


@router.delete("/safety/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_safety_document(
    document_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    document = db.query(SafetyDocument).filter(SafetyDocument.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    db.delete(document)
    db.commit()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    document = (
        db.query(DrugInformationDocument)
        .filter(DrugInformationDocument.id == document_id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    db.delete(document)
    db.commit()


@router.get("/safety")
def list_safety_documents(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    documents = db.query(SafetyDocument).order_by(SafetyDocument.id.desc()).all()
    return [{"id": document.id, "title": document.title} for document in documents]


@router.post("/safety", status_code=status.HTTP_201_CREATED)
async def upload_safety_document(
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted")

    pdf_bytes = await file.read()
    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The selected file is not a valid PDF")

    document = SafetyDocument(title=filename, pdf_file=pdf_bytes)
    db.add(document)
    db.commit()
    db.refresh(document)
    return {"id": document.id, "title": document.title}


