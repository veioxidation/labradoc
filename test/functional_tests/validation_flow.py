import functions.metrics
from functions.metrics import compare_labels_and_predictions, db, model_id, document_ids, doc_results, predictions, \
    field_accuracy, overall_accuracy, metrics

from services.metrics import create_or_update_metric

if __name__ == "__main__":
    # You would need to provide actual document ID and extraction model ID

    for document_id in document_ids:

        for pred in [p for p in predictions if functions.metrics.model_id == model_id]:
            print(pred.field_name, pred.value)

        doc_results.append(compare_labels_and_predictions(db, document_id, model_id))

    # Add to Metrics database - overall_accuracy, field_accuracy, perc_of_full_correct

    for metric in metrics:
        create_or_update_metric(db, metric["name"], metric["value"], len(doc_results), model_id)

    print(doc_results)
    print(f"Overall accuracy: {overall_accuracy}")
    print(f"Accuracy for each field: {field_accuracy}")
