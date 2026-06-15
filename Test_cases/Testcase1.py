def generate_rca_report(title, timeline, logs, diff):
    if not title or not timeline or not logs or not diff:
        return None

    return {
        "title": title,
        "timeline": timeline,
        "root_cause": "Configuration timeout issue",
        "status": "Generated"
    }


def test_generate_rca_report_success():
    result = generate_rca_report(
        "Payment API Failure",
        "02:15 Alert received",
        "Connection timeout error",
        "Updated timeout from 5s to 30s"
    )

    assert result is not None
    assert result["status"] == "Generated"
    assert result["title"] == "Payment API Failure"