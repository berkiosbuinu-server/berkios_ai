from berkios.approval import ApprovalManager, ApprovalDecision


def test_approval_lifecycle():
    manager = ApprovalManager()
    request = manager.create(
        title="Modifier app.py",
        capability="changes.propose",
        targets=["app.py"],
        risk="medium",
    )
    assert request.decision == ApprovalDecision.PENDING
    assert len(manager.pending()) == 1

    approved = manager.approve(request.approval_id)
    assert approved.decision == ApprovalDecision.APPROVED
    assert not manager.pending()


def test_rejection():
    manager = ApprovalManager()
    request = manager.create(title="Action sensible")
    rejected = manager.reject(request.approval_id)
    assert rejected.decision == ApprovalDecision.REJECTED
