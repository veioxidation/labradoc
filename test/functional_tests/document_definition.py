document_mapping = [
    {"file_name": "sample1.txt", "document_id": 1, 'labels': {"document_type": "Invoice",
                                                              "issue_date": "2023-01-01",
                                                              "reference_number": "INV-001"}},
    {"file_name": "sample2.txt", "document_id": 2, 'labels': {"document_type": "Report",
                                                              "issue_date": "2023-01-02",
                                                              "reference_number": "RPT-002"}},
]

labels_to_assign = [
    {"document_id": 1, "labels": {"document_type": "Invoice",
                                    "issue_date": "2021-01-15",
                                    "reference_number": "INV-001"}},
    {"document_id": 2, "labels": {"document_type":"Receipt",
                                    "issue_date": "2021-02-20",
                                    "reference_number": "REC-002"}},
]
