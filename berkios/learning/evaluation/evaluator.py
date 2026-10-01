from __future__ import annotations
from typing import Callable, Iterable
from .models import EvaluationCase, EvaluationResult

class CodixEvaluator:
    """Provider/model-neutral evaluation harness."""

    def evaluate(
        self,
        *,
        model_version: str,
        cases: Iterable[EvaluationCase],
        predict: Callable[[EvaluationCase], str],
        score_fn: Callable[[EvaluationCase,str], float] | None = None,
        min_score: float = .80,
    ) -> EvaluationResult:
        cases=list(cases)
        score_fn=score_fn or self._default_score
        values=[]; failures=[]
        for case in cases:
            try:
                output=predict(case)
                value=max(0.0,min(1.0,float(score_fn(case,output))))
                values.append(value)
                if value < min_score: failures.append(case.case_id)
            except Exception as exc:
                values.append(0.0); failures.append(f"{case.case_id}: {exc}")
        avg=sum(values)/len(values) if values else 0.0
        passed=bool(values) and avg >= min_score
        return EvaluationResult(
            model_version=model_version, score=avg, passed=passed,
            cases_total=len(cases), cases_passed=sum(v>=min_score for v in values),
            metrics={"mean_score":avg}, failures=failures)

    def compare(self, candidate: EvaluationResult, baseline: EvaluationResult, max_drop=.03):
        delta=candidate.score-baseline.score
        return {
            "candidate":candidate.model_version,
            "baseline":baseline.model_version,
            "candidate_score":candidate.score,
            "baseline_score":baseline.score,
            "delta":delta,
            "passed":candidate.passed and delta >= -max_drop,
        }

    def _default_score(self, case, output):
        if case.expected is None:
            return 1.0 if output.strip() else 0.0
        return 1.0 if output.strip()==case.expected.strip() else 0.0
