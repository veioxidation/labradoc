org_name = "Demo Organization"
taxonomy_name = "Document Classification"
model_name = "Demo Extraction Model"
model_description = "Model description dummy"
org_description = "This is a demo organization for testing purposes."
test_folder = "test/samples"



fields = [
    {
        "name": "document_type",
        "data_type": "string",
        "description": "Type of document",
        "is_required": True
    },
    {
        "name": "issue_date",
        "data_type": "date",
        "description": "Date document was issued",
        "is_required": True
    },
    {
        "name": "reference_number",
        "data_type": "string",
        "description": "Document reference number",
        "is_required": False
    }
]
