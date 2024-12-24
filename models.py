from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class DocumentType(Base):
    __tablename__ = "document_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    # Relationship example
    fields = relationship("TaxonomyField", back_populates="document_type")

class TaxonomyField(Base):
    __tablename__ = "taxonomy"
    id = Column(Integer, primary_key=True, index=True)
    document_type_id = Column(Integer, ForeignKey("document_types.id"))
    field_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)  # 'string', 'float', 'date', etc.
    is_required = Column(Boolean, default=False)
    validation_rules = Column(String)  # Could store JSON with regex, range, etc.

    document_type = relationship("DocumentType", back_populates="fields")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    document_type_id = Column(Integer, ForeignKey("document_types.id"))
    nucleus_doc_id = Column(String, nullable=True)  # If using Nucleus ID
    status = Column(String, default="uploaded")
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class ExtractionResult(Base):
    __tablename__ = "extraction_results"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    taxonomy_field_id = Column(Integer, ForeignKey("taxonomy.id"))
    extracted_value = Column(String)
    confidence = Column(Float, nullable=True)
    validation_status = Column(String, default="extracted")  # extracted, validated, failed
    error_type = Column(String, nullable=True)               # verifiable, unverifiable, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)

class Label(Base):
    __tablename__ = "labels"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    taxonomy_field_id = Column(Integer, ForeignKey("taxonomy.id"))
    correct_value = Column(String)
    labeler = Column(String)  # Could link to a User table if needed
    timestamp = Column(DateTime, default=datetime.utcnow)
