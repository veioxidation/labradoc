labels_to_assign = [
    {"document_id": 1, "labels": {"document_type": "Invoice",
                                    "issue_date": "2021-01-15",
                                    "reference_number": "INV-001"}},
    {"document_id": 2, "labels": {"document_type":"Receipt",
                                    "issue_date": "2021-02-20",
                                    "reference_number": "REC-002"}},
]

extractions_to_assign = [
    {"document_id": 1, "labels": {"document_type": "Invoice    ",
                                  "issue_date": "2021-01-16",
                                  "reference_number": "INV-001"}},
    {"document_id": 2, "labels": {"document_type": "Receipt     ",
                                  "issue_date": "2021-02-20",
                                  "reference_number": "REC-002"}},
]

postprocessing_operations = {
    'document_type': [lambda x: x.strip()],
    'issue_date': [lambda x: x[:10]]
}