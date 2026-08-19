from app.ingestion.pipeline import deduplicate_jobs, normalize_job


def test_deduplication_same_external_id():
    job1 = normalize_job({"id": "x1", "title": "Engineer", "company": "A", "location": "Remote", "url": "https://example.com/1"}, "sandbox")
    job2 = normalize_job({"id": "x1", "title": "Engineer", "company": "A", "location": "Remote", "url": "https://example.com/1"}, "sandbox")
    accepted, duplicates, invalid = deduplicate_jobs([job1, job2], set(), set())
    assert accepted[0].external_id == "x1"
    assert duplicates == 1


def test_deduplication_same_content_hash_distinct_ids():
    job1 = normalize_job({"id": "x1", "title": "Engineer", "company": "A", "location": "Remote", "url": "https://example.com/1"}, "sandbox")
    job2 = normalize_job({"id": "x2", "title": "Engineer", "company": "A", "location": "Remote", "url": "https://example.com/1"}, "sandbox")
    accepted, duplicates, invalid = deduplicate_jobs([job1, job2], set(), set())
    assert len(accepted) == 1
    assert duplicates == 1


def test_deduplication_distinct_jobs():
    job1 = normalize_job({"id": "x1", "title": "Engineer", "company": "A", "location": "Remote", "url": "https://example.com/1"}, "sandbox")
    job2 = normalize_job({"id": "x2", "title": "Product Manager", "company": "B", "location": "Paris", "url": "https://example.com/2"}, "sandbox")
    accepted, duplicates, invalid = deduplicate_jobs([job1, job2], set(), set())
    assert len(accepted) == 2
    assert duplicates == 0
