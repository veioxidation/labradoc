import requests
from app.config import settings

def upload_document_to_nucleus(file_path: str):
    """Example function to upload a document file to Nucleus."""
    # This is a stub: actual API endpoints and request format will differ
    url = f"{settings.NUCLEUS_API_URL}/documents"
    headers = {"Authorization": f"Bearer {settings.NUCLEUS_API_KEY}"}
    files = {"file": open(file_path, "rb")}
    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    return response.json().get("document_id")

def run_extraction_workflow(doc_id: str, workflow_id: str):
    """Trigger an extraction workflow in Nucleus."""
    url = f"{settings.NUCLEUS_API_URL}/workflow/{workflow_id}/run"
    headers = {"Authorization": f"Bearer {settings.NUCLEUS_API_KEY}"}
    payload = {"document_id": doc_id}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()  # might contain job_id or status

def fetch_extraction_results(job_id: str):
    """Retrieve extraction results once the workflow completes."""
    url = f"{settings.NUCLEUS_API_URL}/workflow/results/{job_id}"
    headers = {"Authorization": f"Bearer {settings.NUCLEUS_API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
