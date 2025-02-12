from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, Enum, Float, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, UTC
from enum import Enum as PyEnum  # Rename to avoid confusion

Base = declarative_base()


class Organization(Base):
    """
    Organization model
    Represents an organization entity in the system.

    Attributes:
        id (int): Unique identifier for the organization
        name (str): Organization name, must be unique
        description (str): Detailed description of the organization
        created_at (datetime): Timestamp when organization was created
        updated_at (datetime): Timestamp when organization was last updated
        is_active (bool): Flag indicating if organization is active
        documents (list): List of documents belonging to this organization
        taxonomies (list): List of taxonomies belonging to this organization
    """
    __tablename__ = 'organizations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    is_active = Column(Boolean, default=True)

    # One-to-many relationships
    documents = relationship("Document", back_populates="organization")
    taxonomies = relationship("Taxonomy", back_populates="organization")

    def __repr__(self):
        return f"<Organization(name='{self.name}')>"


# Add this enum class before your model definitions
class DocumentStatus(PyEnum):
    """
    Enum for document processing status
    """
    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    COMPLETED = "completed"
    FAILED = "failed"


class FieldExtractionStatus(PyEnum):
    """
    Enum for field extraction status
    """
    UNVALIDATED = "unvalidated"
    VALIDATED = "validated"
    FAILED = "failed"
    VALIDATION_FAILED = "validation_failed"


class Document(Base):
    """
    Document model
    Represents a document entity in the system.

    Attributes:
        id (int): Unique identifier for the document
        name (str): Document name
        file_path (str): Path to the document file
        individual_id (str): Unique identifier for the individual associated with the document
        is_labeled (bool): Flag indicating if the document has been labeled
        organization_id (int): Foreign key to the organization that owns this document
        organization (Organization): Relationship to the organization that owns this document
        taxonomy (Taxonomy): Relationship to the taxonomy that this document belongs to
        field_labels (list): List of field labels associated with this document
    """
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    individual_id = Column(String, nullable=False, index=True)
    is_labeled = Column(Boolean, default=False)

    # Add the status field using the enum
    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.PENDING)

    # Add relationship to organization
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    organization = relationship("Organization", back_populates="documents")

    # Add direct foreign key to taxonomy
    taxonomy_id = Column(Integer, ForeignKey('taxonomies.id'), nullable=True)
    # One-to-one relationship
    taxonomy = relationship("Taxonomy", back_populates="document", uselist=False)

    # Add relationship to field labels
    field_labels = relationship("FieldLabel", back_populates="document")

    predictions = relationship("Prediction", back_populates="document")

    def __repr__(self):
        return f"<Document(name='{self.name}', individual_id='{self.individual_id}')>"


class TaxonomyField(Base):
    """
    TaxonomyField model
    Represents a field entity within a taxonomy in the system.

    Attributes:
        id (int): Unique identifier for the field
        name (str): Field name
        data_type (str): Data type of the field (e.g., "string", "number", "date")
        description (str): Detailed description of the field
        is_required (bool): Flag indicating if the field is required
        taxonomy_id (int): Foreign key to the taxonomy that this field belongs to
        taxonomy (Taxonomy): Relationship to the taxonomy that this field belongs to
        field_labels (list): List of field labels associated with this field
    """
    __tablename__ = 'fields'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)  # e.g., "string", "number", "date"
    description = Column(String)
    is_required = Column(Boolean, default=False)
    # Add direct foreign key to taxonomy
    taxonomy_id = Column(Integer, ForeignKey('taxonomies.id'), nullable=True)
    # Add relationship to field labels
    field_labels = relationship("FieldLabel", back_populates="field")

    # Add relationship to taxonomy
    taxonomy = relationship("Taxonomy", back_populates="fields")

    # Add relationship to predictions
    predictions = relationship("Prediction", back_populates="field")

    def __repr__(self):
        return f"<TaxonomyField(name='{self.name}', data_type='{self.data_type}')>"


class Taxonomy(Base):
    """
    Taxonomy model
    Represents a taxonomy entity in the system.

    Attributes:
        id (int): Unique identifier for the taxonomy
        name (str): Taxonomy name, must be unique
        description (str): Detailed description of the taxonomy
        version (str): Version of the taxonomy
        is_active (bool): Flag indicating if the taxonomy is active
        organization_id (int): Foreign key to the organization that owns this taxonomy
        organization (Organization): Relationship to the organization that owns this taxonomy
        document (Document): Relationship to the document that this taxonomy belongs to
        fields (list): List of fields associated with this taxonomy
        extraction_models (list): List of extraction models associated with this taxonomy
    """
    __tablename__ = 'taxonomies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    version = Column(String)
    is_active = Column(Boolean, default=True)

    # Add relationship to organization
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    organization = relationship("Organization", back_populates="taxonomies")

    # One-to-one relationship
    document = relationship("Document", back_populates="taxonomy", uselist=False)

    # Add relationship to fields
    fields = relationship("TaxonomyField", back_populates="taxonomy")

    # Add relationship to extraction models
    extraction_models = relationship("ExtractionModel", back_populates="taxonomy")

    def __repr__(self):
        return f"<Taxonomy(name='{self.name}', version='{self.version}')>"


class FieldLabel(Base):
    """
    FieldLabel model
    Represents a field label entity in the system.

    Attributes:
        id (int): Unique identifier for the field label
        value (str): Value of the field label
        document_id (int): Foreign key to the document that this field label belongs to
        field_id (int): Foreign key to the field that this field label belongs to
        document (Document): Relationship to the document that this field label belongs to
        field (TaxonomyField): Relationship to the field that this field label belongs to
    """
    __tablename__ = 'field_labels'

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Text, nullable=False)  # Using Text instead of String for potentially large values

    # Foreign keys
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    field_id = Column(Integer, ForeignKey('fields.id'), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="field_labels")
    field = relationship("TaxonomyField", back_populates="field_labels")
    field_name = Column(String, nullable=False)
    occurrence = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint('document_id', 'field_id', name='uq_document_field'),
    )


    def __repr__(self):
        return f"<FieldLabel(field_id={self.field_id}, document_id={self.document_id}, value='{self.value[:50]}...'>"


class ExtractionModel(Base):
    """
    ExtractionModel model
    Represents an extraction model entity in the system.

    Attributes:
        id (int): Unique identifier for the extraction model
        name (str): Extraction model name
        description (str): Detailed description of the extraction model
        created_at (datetime): Timestamp when extraction model was created
        updated_at (datetime): Timestamp when extraction model was last updated
        is_active (bool): Flag indicating if the extraction model is active
        taxonomy_id (int): Foreign key to the taxonomy that this extraction model belongs to
        taxonomy (Taxonomy): Relationship to the taxonomy that this extraction model belongs to
        predictions (list): List of predictions associated with this extraction model
    """
    __tablename__ = 'extraction_models'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Fix: Change backref to back_populates to match the explicit relationship in Taxonomy
    taxonomy_id = Column(Integer, ForeignKey('taxonomies.id'), nullable=False)
    taxonomy = relationship("Taxonomy", back_populates="extraction_models")

    predictions = relationship("Prediction", back_populates="model")

    metrics = relationship("Metric", back_populates="model")

    def __repr__(self):
        return f"<ExtractionModel(name='{self.name}')>"


class Prediction(Base):
    """
    Prediction model
    Represents a prediction entity in the system.

    Attributes:
        id (int): Unique identifier for the prediction
        document_id (int): Foreign key to the document that this prediction belongs to
        prediction (str): The prediction value
        created_at (datetime): Timestamp when prediction was created
        model_id (int): Foreign key to the extraction model that this prediction belongs to
        model (ExtractionModel): Relationship to the extraction model that this prediction belongs to
    """
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Add relationship to extraction model
    model_id = Column(Integer, ForeignKey('extraction_models.id'), nullable=False)
    model = relationship("ExtractionModel", back_populates="predictions")

    field_id = Column(Integer, ForeignKey('fields.id'), nullable=False)
    field = relationship("TaxonomyField", back_populates="predictions")
    field_name = Column(String, nullable=False)
    value = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint('document_id', 'model_id', 'field_id', name='uq_document_model_field'),
    )


    occurrence = Column(Integer, nullable=False, default=1)
    document = relationship("Document", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction(document_id={self.document_id}, model_id={self.model_id})>"

class Metric(Base):
    """
    PerformanceMetric model
    Represents a metric entity in the system.

    Attributes:
        id (int): Unique identifier for the metric
        name (str): PerformanceMetric name
        value (float): PerformanceMetric value
        sample_size (int): Sample size used to calculate the metric
        created_at (datetime): Timestamp when metric was created
        updated_at (datetime): Timestamp when metric was last updated
        model_id (int): Foreign key to the extraction model that this metric belongs to
        model (ExtractionModel): Relationship to the extraction model that this metric belongs"""
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    model_id = Column(Integer, ForeignKey('extraction_models.id'), nullable=False)
    model = relationship("ExtractionModel", back_populates="metrics")

    __table_args__ = (
        UniqueConstraint('model_id', 'name', name='uq_model_id_name'),
        CheckConstraint('sample_size > 0', name='check_sample_size_positive'),
    )


    def __repr__(self):
        return f"<Metric(name='{self.name}')>"