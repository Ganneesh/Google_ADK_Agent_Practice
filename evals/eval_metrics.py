import statistics
from typing import Optional

from google.adk.evaluation.conversation_scenarios import ConversationScenario
from google.adk.evaluation.eval_case import Invocation
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.evaluator import EvaluationResult, PerInvocationResult, EvalStatus


def _check_feature_structure(feature_content: str) -> float:
    required = ["Feature:", "Scenario:", "Given", "When", "Then"]
    missing = [kw for kw in required if kw not in feature_content]
    return 0.0 if missing else 1.0


def _extract_save_feature_args(invocation: Invocation) -> Optional[dict]:
    if not invocation.intermediate_data:
        return None

    events = getattr(invocation.intermediate_data, "invocation_events", None) or []

    for event in events:
        content = getattr(event, "content", None)
        if not content:
            continue
        parts = getattr(content, "parts", None) or []
        for part in parts:
            function_call = getattr(part, "function_call", None)
            if function_call and function_call.name == "save_feature_file":
                return function_call.args

    return None


def _extract_called_tool_names(invocation: Invocation) -> list[str]:
    """Returns the ordered list of tool names called during this invocation,
    ignoring their arguments entirely."""
    if not invocation.intermediate_data:
        return []

    events = getattr(invocation.intermediate_data, "invocation_events", None) or []
    called_tools = []

    for event in events:
        content = getattr(event, "content", None)
        if not content:
            continue
        for part in getattr(content, "parts", None) or []:
            function_call = getattr(part, "function_call", None)
            if function_call:
                called_tools.append(function_call.name)

    return called_tools


def _patch_threshold(eval_metric: EvalMetric, default: float = 1.0) -> None:
    """Patches the deprecated flat threshold field from criterion.threshold,
    since this ADK build leaves eval_metric.threshold as None when the
    value is only set via criteria/criterion, and the framework's own
    pass/fail check reads the deprecated field."""
    if eval_metric.threshold is None:
        criterion_threshold = getattr(getattr(eval_metric, "criterion", None), "threshold", None)
        eval_metric.threshold = criterion_threshold if criterion_threshold is not None else default


def gherkin_structure_metric(
    eval_metric: EvalMetric,
    actual_invocations: list[Invocation],
    expected_invocations: Optional[list[Invocation]],
    conversation_scenario: Optional[ConversationScenario],
) -> EvaluationResult:
    _patch_threshold(eval_metric)

    per_invocation_results = []
    scores = []

    for invocation in actual_invocations:
        args = _extract_save_feature_args(invocation)

        if not args:
            score = 0.0
        else:
            feature_content = args.get("feature_content", "")
            score = _check_feature_structure(feature_content)

        scores.append(score)
        per_invocation_results.append(
            PerInvocationResult(
                actual_invocation=invocation,
                expected_invocation=None,
                score=score,
                eval_status=EvalStatus.PASSED if score >= eval_metric.threshold else EvalStatus.FAILED,
            )
        )

    overall_score = statistics.mean(scores) if scores else 0.0

    return EvaluationResult(
        overall_score=overall_score,
        overall_eval_status=EvalStatus.PASSED if overall_score >= eval_metric.threshold else EvalStatus.FAILED,
        per_invocation_results=per_invocation_results,
    )


def tool_call_sequence_metric(
    eval_metric: EvalMetric,
    actual_invocations: list[Invocation],
    expected_invocations: Optional[list[Invocation]],
    conversation_scenario: Optional[ConversationScenario],
) -> EvaluationResult:
    """Checks that save_feature_file was called exactly once, and no
    unexpected tools were called — ignores argument content entirely,
    since exact-argument matching against a generative agent is unstable."""
    _patch_threshold(eval_metric)

    expected_tool_sequence = ["save_feature_file"]

    per_invocation_results = []
    scores = []

    for invocation in actual_invocations:
        called_tools = _extract_called_tool_names(invocation)
        score = 1.0 if called_tools == expected_tool_sequence else 0.0

        scores.append(score)
        per_invocation_results.append(
            PerInvocationResult(
                actual_invocation=invocation,
                expected_invocation=None,
                score=score,
                eval_status=EvalStatus.PASSED if score >= eval_metric.threshold else EvalStatus.FAILED,
            )
        )

    overall_score = statistics.mean(scores) if scores else 0.0

    return EvaluationResult(
        overall_score=overall_score,
        overall_eval_status=EvalStatus.PASSED if overall_score >= eval_metric.threshold else EvalStatus.FAILED,
        per_invocation_results=per_invocation_results,
    )