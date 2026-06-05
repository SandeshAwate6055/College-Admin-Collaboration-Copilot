from app.datasets.service import list_datasets, read_dataset_rows, student_profile


def test_all_configured_datasets_are_readable():
    datasets = list_datasets()

    assert {dataset["id"] for dataset in datasets} == {
        "industry_projects",
        "academic_projects",
        "internships",
        "hackathons",
        "certifications",
        "research_papers",
    }
    assert all(read_dataset_rows(dataset) for dataset in datasets)


def test_student_profile_groups_records_by_dataset():
    dataset = next(item for item in list_datasets() if item["id"] == "industry_projects")
    first_row = read_dataset_rows(dataset)[0]

    profile = student_profile(first_row["PRN_or_Roll_No"])

    assert profile["prn_or_roll_no"] == first_row["PRN_or_Roll_No"]
    assert profile["total_records"] >= 1
    assert "industry_projects" in profile["datasets"]
