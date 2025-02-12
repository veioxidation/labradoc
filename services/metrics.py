from sqlalchemy.orm import Session
from models.DataModels import Metric


def create_metric(db: Session, name: str, value: float, sample_size: int, model_id: int) -> Metric:
    """
    Create a new metric in the database.

    Args:
        db (Session): Database session
        name (str): Name of the metric
        value (float): Value of the metric
        sample_size (int): Sample size used to calculate the metric
        model_id (int): Foreign key to the extraction model that this metric belongs to

    Returns:
        Metric: The created metric object
    """
    new_metric = Metric(name=name, value=value, sample_size=sample_size, model_id=model_id)
    db.add(new_metric)
    db.commit()
    db.refresh(new_metric)
    return new_metric


def update_metric(db: Session, metric_id: int, name: str = None, value: float = None,
                  sample_size: int = None) -> Metric:
    """
    Update an existing metric in the database.

    Args:
        db (Session): Database session
        metric_id (int): ID of the metric to update
        name (str, optional): New name of the metric
        value (float, optional): New value of the metric
        sample_size (int, optional): New sample size used to calculate the metric

    Returns:
        Metric: The updated metric object
    """
    metric = db.query(Metric).filter(Metric.id == metric_id).first()
    if not metric:
        raise ValueError(f"PerformanceMetric with ID '{metric_id}' not found.")

    if name is not None:
        metric.name = name
    if value is not None:
        metric.value = value
    if sample_size is not None:
        metric.sample_size = sample_size

    db.commit()
    db.refresh(metric)
    return metric

def create_or_update_metric(db: Session,
                            name: str,
                            value: float,
                            sample_size: int,
                            model_id: int) -> Metric:
    """
    Create a new metric or update an existing one in the database.

    Args:
        db (Session): Database session
        name (str): Name of the metric
        value (float): Value of the metric
        sample_size (int): Sample size used to calculate the metric
        model_id (int): Foreign key to the extraction model that this metric belongs to

    Returns:
        Metric: The created or updated metric object
    """
    metric = get_metric_by_model_and_name(db, name, model_id)
    if metric:
        return update_metric(db, metric.id, value=value, sample_size=sample_size)
    else:
        return create_metric(db, name, value, sample_size, model_id)

def delete_metric(db: Session,
                  metric_id: int) -> bool:
    """
    Delete a metric from the database.

    Args:
        db (Session): Database session
        metric_id (int): ID of the metric to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    metric = db.query(Metric).filter(Metric.id == metric_id).first()
    if not metric:
        raise ValueError(f"PerformanceMetric with ID '{metric_id}' not found.")

    db.delete(metric)
    db.commit()
    return True


def get_metrics_for_model(db: Session, model_id: int) -> list[Metric]:
    """
    Get all metrics associated with a specific extraction model.

    Args:
        db (Session): Database session
        model_id (int): ID of the extraction model

    Returns:
        list[Metric]: List of metric objects for the specified model
    """
    return db.query(Metric).filter(Metric.model_id == model_id).all()


def get_metric_by_model_and_name(db: Session, metric_name: str, model_id: int) -> Metric:
    """
    Get a metric by its ID.

    Args:
        db (Session): Database session
        metric_id (int): ID of the metric to retrieve

    Returns:
        Metric: The metric object
    """
    return db.query(Metric).filter(Metric.name == metric_name,
                                   Metric.model_id == model_id).first()


