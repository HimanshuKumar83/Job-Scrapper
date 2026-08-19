from app.ingestion.pipeline import normalize_job, parse_raw_jobs, validate_response


def test_validate_response_accepts_job_list():
    payload = {"jobs": [{"id": "1", "title": "Engineer"}]}
    assert validate_response(payload, "jobs") is True


def test_parse_raw_jobs_handles_list():
    payload = {"jobs": [{"id": "1", "title": "Engineer"}, {"id": "2", "title": "Tester"}]}
    jobs = parse_raw_jobs(payload)
    assert len(jobs) == 2


def test_normalize_job_sets_required_values():
    normalized = normalize_job({"id": "42", "title": "AI Engineer", "company": "Acedyon", "url": "https://example.com"}, "sandbox")
    assert normalized.source == "sandbox"
    assert normalized.external_id == "42"
    assert normalized.title == "AI Engineer"
    assert normalized.content_hash
