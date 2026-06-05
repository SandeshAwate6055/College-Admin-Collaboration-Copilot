from fastapi import APIRouter, HTTPException, Query

from app.datasets.service import (
    dataset_analytics,
    get_dataset,
    ingest_all_datasets,
    ingest_dataset,
    list_datasets,
    search_dataset,
    student_profile,
)

router = APIRouter()


@router.get("/datasets")
def datasets():
    return {
        "datasets": [
            {
                "id": dataset["id"],
                "label": dataset["label"],
                "csv_path": dataset["csv_path"],
                "searchable_columns": dataset.get("searchable_columns", []),
            }
            for dataset in list_datasets()
        ]
    }


@router.post("/datasets/ingest")
def ingest_all():
    return {"results": ingest_all_datasets()}


@router.post("/datasets/{dataset_id}/ingest")
def ingest_one(dataset_id: str):
    try:
        return ingest_dataset(dataset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/search/datasets/{dataset_id}")
def search_one_dataset(
    dataset_id: str,
    q: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=25),
):
    try:
        get_dataset(dataset_id)
        return search_dataset(dataset_id, q, top_k=top_k)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.get("/student/{prn_or_roll_no}/profile")
def profile(prn_or_roll_no: str):
    return student_profile(prn_or_roll_no)


@router.get("/analytics/datasets")
def analytics():
    return dataset_analytics()
