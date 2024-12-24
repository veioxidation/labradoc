from pydantic import BaseModel
from typing import Optional

class DocumentTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DocumentTypeOut(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True

class TaxonomyFieldCreate(BaseModel):
    document_type_id: int
    field_name: str
    data_type: str
    is_required: bool = False
    validation_rules: Optional[str] = None

class TaxonomyFieldOut(BaseModel):
    id: int
    document_type_id: int
    field_name: str
    data_type: str
    is_required: bool
    validation_rules: Optional[str]

    class Config:
        orm_mode = True

class DocumentCreate(BaseModel):
    document_type_id: int
    nucleus_doc_id: Optional[str] = None

class DocumentOut(BaseModel):
    id: int
    document_type_id: int
    nucleus_doc_id: Optional[str]
    status: str

    class Config:
        orm_mode = True

# Similarly, create schemas for ExtractionResult, Label, etc.
