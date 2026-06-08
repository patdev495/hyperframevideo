from hyperframevideo.script_approval import ScriptApprovalGate


def test_script_approval_gate_rejects_draft_script() -> None:
    result = ScriptApprovalGate().evaluate("Status: draft\nLanguage: en\n")

    assert result.is_approved is False
    assert result.status == "draft"
    assert result.diagnostic == "Script is still draft."


def test_script_approval_gate_accepts_approved_script() -> None:
    result = ScriptApprovalGate().evaluate("Status: approved\nLanguage: en\n")

    assert result.is_approved is True
    assert result.status == "approved"
    assert result.diagnostic is None


def test_script_approval_gate_rejects_missing_status() -> None:
    result = ScriptApprovalGate().evaluate("Language: en\n")

    assert result.is_approved is False
    assert result.status is None
    assert result.diagnostic == "Script status is missing."


def test_script_approval_gate_rejects_unknown_status_with_diagnostic() -> None:
    result = ScriptApprovalGate().evaluate("Status: reviewed\nLanguage: en\n")

    assert result.is_approved is False
    assert result.status == "reviewed"
    assert result.diagnostic == "Unsupported script status: reviewed."


def test_script_approval_gate_supports_status_case_and_spacing() -> None:
    result = ScriptApprovalGate().evaluate("  Status : APPROVED  \nLanguage: en\n")

    assert result.is_approved is True
    assert result.status == "approved"
