"""Provider-neutral coordination of pre-execution invocation lifecycle stages.

The coordinator validates requests, declarations, and reported results. It does
not invoke adapters, authorize operations, or verify provider behavior.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from enum import Enum
from types import MappingProxyType

from scripts.provider_adapter import (
    AdapterAvailability,
    AuthorizationGrant,
    ExecutionContext,
    ProviderAdapter,
    ProviderAdapterContractError,
)
from scripts.provider_capability_resolver import (
    CapabilityResolutionStatus,
    ProviderCandidateStatus,
    ProviderCapabilityResolution,
    resolve_provider_capability,
)
from scripts.provider_contract_validator import validate_provider_adapter
from scripts.provider_invocation import (
    ProviderInvocation,
    ProviderInvocationValidationError,
)
from scripts.provider_invocation_result import (
    ProviderInvocationResultRecord,
    ProviderInvocationResultValidationError,
    validate_provider_invocation_result,
)
from scripts.provider_registry import (
    ProviderNotFoundError,
    ProviderRegistry,
)


_IDENTIFIER_PATTERN = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\Z")


class InvocationLifecycleState(str, Enum):
    REQUEST_RECEIVED = "request_received"
    REQUEST_VALIDATED = "request_validated"
    CONTRACT_CONFORMANCE_CHECKED = "contract_conformance_checked"
    CAPABILITY_COMPATIBILITY_RESOLVED = "capability_compatibility_resolved"
    READY_FOR_AUTHORIZED_EXECUTION_LAYER = "ready_for_authorized_execution_layer"
    REJECTED_BEFORE_EXECUTION = "rejected_before_execution"
    RESULT_VALIDATION_FAILED = "result_validation_failed"
    COMPLETED_WITH_VALIDATED_RESULT = "completed_with_validated_result"


class InvocationLifecycleIssueCode(str, Enum):
    INVALID_REQUEST = "invalid_request"
    INVALID_REGISTRY = "invalid_registry"
    PROVIDER_NOT_REGISTERED = "provider_not_registered"
    CONTRACT_NONCONFORMANT = "contract_nonconformant"
    CAPABILITY_NOT_DECLARED = "capability_not_declared"
    OPERATION_NOT_DECLARED = "operation_not_declared"
    AVAILABILITY_NOT_READY = "availability_not_ready"
    CAPABILITY_RESOLUTION_FAILED = "capability_resolution_failed"
    PROVIDER_SELECTION_REQUIRED = "provider_selection_required"
    AUTHORIZATION_NOT_EVALUATED = "authorization_not_evaluated"
    RESULT_VALIDATION_FAILED = "result_validation_failed"


@dataclass(frozen=True, slots=True)
class InvocationLifecycleIssue:
    """Safe, payload-free lifecycle issue."""

    code: InvocationLifecycleIssueCode
    message: str


@dataclass(frozen=True, slots=True)
class InvocationLifecycleResult:
    """Current lifecycle state and deterministic coordination evidence."""

    request_id: str | None
    state: InvocationLifecycleState
    state_history: tuple[InvocationLifecycleState, ...]
    resolution: ProviderCapabilityResolution | None
    compatible_provider_ids: tuple[str, ...]
    issues: tuple[InvocationLifecycleIssue, ...]
    validated_result: ProviderInvocationResultRecord | None = None


_ALLOWED_TRANSITIONS = {
    InvocationLifecycleState.REQUEST_RECEIVED: {
        InvocationLifecycleState.REQUEST_VALIDATED,
        InvocationLifecycleState.REJECTED_BEFORE_EXECUTION,
    },
    InvocationLifecycleState.REQUEST_VALIDATED: {
        InvocationLifecycleState.CONTRACT_CONFORMANCE_CHECKED,
        InvocationLifecycleState.CAPABILITY_COMPATIBILITY_RESOLVED,
        InvocationLifecycleState.REJECTED_BEFORE_EXECUTION,
    },
    InvocationLifecycleState.CONTRACT_CONFORMANCE_CHECKED: {
        InvocationLifecycleState.CAPABILITY_COMPATIBILITY_RESOLVED,
        InvocationLifecycleState.REJECTED_BEFORE_EXECUTION,
    },
    InvocationLifecycleState.CAPABILITY_COMPATIBILITY_RESOLVED: {
        InvocationLifecycleState.READY_FOR_AUTHORIZED_EXECUTION_LAYER,
        InvocationLifecycleState.REJECTED_BEFORE_EXECUTION,
    },
    InvocationLifecycleState.READY_FOR_AUTHORIZED_EXECUTION_LAYER: {
        InvocationLifecycleState.RESULT_VALIDATION_FAILED,
        InvocationLifecycleState.COMPLETED_WITH_VALIDATED_RESULT,
    },
    InvocationLifecycleState.REJECTED_BEFORE_EXECUTION: set(),
    InvocationLifecycleState.RESULT_VALIDATION_FAILED: set(),
    InvocationLifecycleState.COMPLETED_WITH_VALIDATED_RESULT: set(),
}


def is_valid_invocation_lifecycle_transition(
    current_state: object,
    next_state: object,
) -> bool:
    """Return whether two canonical lifecycle states form an allowed transition.

    Unknown values return ``False``. Transition validity describes lifecycle
    ordering only; it does not establish authorization, provider availability,
    execution, or result correctness.
    """
    if (
        type(current_state) is not InvocationLifecycleState
        or type(next_state) is not InvocationLifecycleState
    ):
        return False
    return next_state in _ALLOWED_TRANSITIONS[current_state]


class ProviderInvocationCoordinator:
    """Coordinate canonical validation and resolution without provider execution."""

    def __init__(self, registry: ProviderRegistry) -> None:
        if type(registry) is not ProviderRegistry:
            raise TypeError("registry must be a canonical ProviderRegistry.")
        self._registry = registry

    def coordinate(self, request: ProviderInvocation) -> InvocationLifecycleResult:
        """Validate and resolve a request, stopping before any adapter invocation.

        A ready state is a handoff boundary only: authorization and live provider
        health are not evaluated by this coordinator.
        """
        state = InvocationLifecycleState.REQUEST_RECEIVED
        history = [state]
        issues: list[InvocationLifecycleIssue] = []
        request_id = (
            request.request_id if type(request) is ProviderInvocation else None
        )

        normalized_request = self._validate_request(request)
        if normalized_request is None:
            issues.append(
                InvocationLifecycleIssue(
                    InvocationLifecycleIssueCode.INVALID_REQUEST,
                    "request is not a valid canonical ProviderInvocation.",
                )
            )
            self._transition(history, InvocationLifecycleState.REJECTED_BEFORE_EXECUTION)
            return self._result(request_id, history, None, (), issues)

        request_id = normalized_request.request_id
        self._transition(history, InvocationLifecycleState.REQUEST_VALIDATED)

        if normalized_request.provider_id is not None:
            try:
                registration = ProviderRegistry.get_registration(
                    self._registry, normalized_request.provider_id
                )
            except ProviderNotFoundError:
                issues.append(
                    InvocationLifecycleIssue(
                        InvocationLifecycleIssueCode.PROVIDER_NOT_REGISTERED,
                        "the explicitly requested provider is not registered.",
                    )
                )
                self._transition(
                    history, InvocationLifecycleState.REJECTED_BEFORE_EXECUTION
                )
                return self._result(request_id, history, None, (), issues)
            except Exception:
                issues.append(
                    InvocationLifecycleIssue(
                        InvocationLifecycleIssueCode.INVALID_REGISTRY,
                        "the canonical registry could not retrieve the requested provider.",
                    )
                )
                self._transition(
                    history, InvocationLifecycleState.REJECTED_BEFORE_EXECUTION
                )
                return self._result(request_id, history, None, (), issues)

            conformance = validate_provider_adapter(registration.adapter)
            self._transition(
                history, InvocationLifecycleState.CONTRACT_CONFORMANCE_CHECKED
            )
            if not conformance.conformant or not conformance.registry_compatible:
                issues.append(
                    InvocationLifecycleIssue(
                        InvocationLifecycleIssueCode.CONTRACT_NONCONFORMANT,
                        "the explicitly requested provider failed canonical contract validation.",
                    )
                )
                self._transition(
                    history, InvocationLifecycleState.REJECTED_BEFORE_EXECUTION
                )
                return self._result(request_id, history, None, (), issues)

        try:
            resolution = resolve_provider_capability(
                self._registry,
                normalized_request.capability_id,
                normalized_request.operation_id,
                required_availability=AdapterAvailability.READY,
            )
        except Exception:
            issues.append(
                InvocationLifecycleIssue(
                    InvocationLifecycleIssueCode.INVALID_REGISTRY,
                    "capability resolution could not be completed safely.",
                )
            )
            self._transition(
                history, InvocationLifecycleState.REJECTED_BEFORE_EXECUTION
            )
            return self._result(request_id, history, None, (), issues)

        if normalized_request.provider_id is None and resolution.candidates:
            self._transition(
                history, InvocationLifecycleState.CONTRACT_CONFORMANCE_CHECKED
            )

        self._transition(
            history, InvocationLifecycleState.CAPABILITY_COMPATIBILITY_RESOLVED
        )
        compatible_ids = tuple(
            candidate.provider_id
            for candidate in resolution.compatible_candidates
            if candidate.provider_id is not None
        )

        if normalized_request.provider_id is not None:
            selected_candidate = next(
                (
                    candidate
                    for candidate in resolution.candidates
                    if candidate.provider_id == normalized_request.provider_id
                ),
                None,
            )
            if selected_candidate is None:
                issues.append(
                    InvocationLifecycleIssue(
                        InvocationLifecycleIssueCode.CAPABILITY_NOT_DECLARED,
                        "the explicitly requested provider does not declare the requested capability.",
                    )
                )
                self._transition(
                    history, InvocationLifecycleState.REJECTED_BEFORE_EXECUTION
                )
                return self._result(
                    request_id, history, resolution, compatible_ids, issues
                )

            candidate_failure = self._candidate_issue(selected_candidate.status)
            if candidate_failure is not None:
                issues.append(candidate_failure)
                self._transition(
                    history, InvocationLifecycleState.REJECTED_BEFORE_EXECUTION
                )
                return self._result(
                    request_id, history, resolution, compatible_ids, issues
                )

            if selected_candidate.status is not ProviderCandidateStatus.COMPATIBLE:
                issues.append(
                    InvocationLifecycleIssue(
                        InvocationLifecycleIssueCode.CAPABILITY_RESOLUTION_FAILED,
                        "the explicitly requested provider does not satisfy the request.",
                    )
                )
                self._transition(
                    history, InvocationLifecycleState.REJECTED_BEFORE_EXECUTION
                )
                return self._result(
                    request_id, history, resolution, compatible_ids, issues
                )

            self._transition(
                history,
                InvocationLifecycleState.READY_FOR_AUTHORIZED_EXECUTION_LAYER,
            )
            issues.append(
                InvocationLifecycleIssue(
                    InvocationLifecycleIssueCode.AUTHORIZATION_NOT_EVALUATED,
                    "authorization and live provider health must be evaluated by the "
                    "downstream execution layer.",
                )
            )
            return self._result(
                request_id, history, resolution, compatible_ids, issues
            )

        if resolution.status is CapabilityResolutionStatus.AMBIGUOUS:
            issues.append(
                InvocationLifecycleIssue(
                    InvocationLifecycleIssueCode.PROVIDER_SELECTION_REQUIRED,
                    "multiple providers match; no provider was selected.",
                )
            )
        elif resolution.status is CapabilityResolutionStatus.COMPATIBLE:
            issues.append(
                InvocationLifecycleIssue(
                    InvocationLifecycleIssueCode.PROVIDER_SELECTION_REQUIRED,
                    "a provider identifier is required before execution handoff.",
                )
            )
        else:
            issues.append(self._resolution_issue(resolution.status))
            self._transition(
                history, InvocationLifecycleState.REJECTED_BEFORE_EXECUTION
            )

        return self._result(request_id, history, resolution, compatible_ids, issues)

    def validate_reported_result(
        self,
        request: ProviderInvocation,
        lifecycle: InvocationLifecycleResult,
        reported_result: object,
    ) -> InvocationLifecycleResult:
        """Validate an actually supplied result without changing request or result.

        Only requests already at the authorized-execution-layer handoff can be
        completed through this API. This method validates a report; it does not
        establish that execution or its reported state really occurred.
        """
        if type(lifecycle) is not InvocationLifecycleResult:
            return self._failed_result_validation(
                lifecycle,
                "lifecycle must be a canonical InvocationLifecycleResult.",
            )
        if lifecycle.state is not InvocationLifecycleState.READY_FOR_AUTHORIZED_EXECUTION_LAYER:
            issue = InvocationLifecycleIssue(
                InvocationLifecycleIssueCode.RESULT_VALIDATION_FAILED,
                "a result can only complete a lifecycle at the execution-layer handoff.",
            )
            return InvocationLifecycleResult(
                request_id=lifecycle.request_id,
                state=lifecycle.state,
                state_history=lifecycle.state_history,
                resolution=lifecycle.resolution,
                compatible_provider_ids=lifecycle.compatible_provider_ids,
                issues=lifecycle.issues + (issue,),
                validated_result=lifecycle.validated_result,
            )
        normalized_request = self._validate_request(request)
        if (
            normalized_request is None
            or normalized_request.request_id != lifecycle.request_id
        ):
            return self._failed_result_validation(
                lifecycle,
                "request does not match the lifecycle being completed.",
            )
        try:
            validated_result = validate_provider_invocation_result(
                reported_result,
                normalized_request,
            )
        except (ProviderInvocationResultValidationError, TypeError, ValueError):
            return self._failed_result_validation(
                lifecycle,
                "the supplied provider-reported result failed validation.",
            )

        provider_id = validated_result.outcome.provenance.provider_id
        if provider_id not in lifecycle.compatible_provider_ids:
            return self._failed_result_validation(
                lifecycle,
                "result provider is not among the compatible registered candidates.",
            )
        history = list(lifecycle.state_history)
        try:
            self._transition(
                history, InvocationLifecycleState.COMPLETED_WITH_VALIDATED_RESULT
            )
        except ValueError:
            return self._failed_result_validation(
                lifecycle,
                "lifecycle state does not allow result completion.",
            )
        return InvocationLifecycleResult(
            request_id=lifecycle.request_id,
            state=InvocationLifecycleState.COMPLETED_WITH_VALIDATED_RESULT,
            state_history=tuple(history),
            resolution=lifecycle.resolution,
            compatible_provider_ids=lifecycle.compatible_provider_ids,
            issues=tuple(lifecycle.issues),
            validated_result=validated_result,
        )

    @staticmethod
    def _validate_request(request: object) -> ProviderInvocation | None:
        if type(request) is not ProviderInvocation:
            return None
        try:
            inputs = _thaw_builtin(request.inputs)
            context_values = _thaw_builtin(request.context.values)
            if type(inputs) is not dict or type(context_values) is not dict:
                return None
            grants = request.context.authorization_grants
            if type(grants) is not tuple or any(
                type(grant) is not AuthorizationGrant for grant in grants
            ):
                return None
            copied_grants = tuple(replace(grant) for grant in grants)
            context = ExecutionContext(
                values=context_values,
                authorization_grants=copied_grants,
            )
            return ProviderInvocation(
                capability_id=request.capability_id,
                operation_id=request.operation_id,
                inputs=inputs,
                provider_id=request.provider_id,
                context=context,
                request_id=request.request_id,
                trace_id=request.trace_id,
                timeout_seconds=request.timeout_seconds,
                cancellation=request.cancellation,
            )
        except (
            ProviderInvocationValidationError,
            ProviderAdapterContractError,
            TypeError,
            ValueError,
            AttributeError,
        ):
            return None

    @staticmethod
    def _candidate_issue(
        status: ProviderCandidateStatus,
    ) -> InvocationLifecycleIssue | None:
        if status in (
            ProviderCandidateStatus.DECLARATION_INVALID,
            ProviderCandidateStatus.REGISTRY_INCOMPATIBLE,
            ProviderCandidateStatus.SNAPSHOT_MISMATCH,
        ):
            return InvocationLifecycleIssue(
                InvocationLifecycleIssueCode.CONTRACT_NONCONFORMANT,
                "the explicitly requested provider declaration is invalid or "
                "incompatible with the registry.",
            )
        if status is ProviderCandidateStatus.OPERATION_NOT_DECLARED:
            return InvocationLifecycleIssue(
                InvocationLifecycleIssueCode.OPERATION_NOT_DECLARED,
                "the explicitly requested provider does not declare the requested "
                "operation for this capability.",
            )
        if status is ProviderCandidateStatus.AVAILABILITY_UNSATISFIED:
            return InvocationLifecycleIssue(
                InvocationLifecycleIssueCode.AVAILABILITY_NOT_READY,
                "the provider's declared availability is not READY.",
            )
        return None

    @staticmethod
    def _resolution_issue(
        status: CapabilityResolutionStatus,
    ) -> InvocationLifecycleIssue:
        if status is CapabilityResolutionStatus.CAPABILITY_NOT_DECLARED:
            code = InvocationLifecycleIssueCode.CAPABILITY_NOT_DECLARED
            message = "no registered provider declares the requested capability."
        elif status is CapabilityResolutionStatus.OPERATION_NOT_DECLARED:
            code = InvocationLifecycleIssueCode.OPERATION_NOT_DECLARED
            message = "no matching provider declares the requested operation."
        elif status is CapabilityResolutionStatus.AVAILABILITY_UNSATISFIED:
            code = InvocationLifecycleIssueCode.AVAILABILITY_NOT_READY
            message = "matching providers do not declare READY availability."
        elif status in (
            CapabilityResolutionStatus.DECLARATION_INVALID,
            CapabilityResolutionStatus.REGISTRY_INCOMPATIBLE,
        ):
            code = InvocationLifecycleIssueCode.CONTRACT_NONCONFORMANT
            message = "provider declarations failed contract or registry validation."
        else:
            code = InvocationLifecycleIssueCode.CAPABILITY_RESOLUTION_FAILED
            message = "capability compatibility could not be established."
        return InvocationLifecycleIssue(code, message)

    @staticmethod
    def _transition(
        history: list[InvocationLifecycleState],
        next_state: InvocationLifecycleState,
    ) -> None:
        if not history:
            raise ValueError("lifecycle history must contain a current state.")
        current_state = history[-1]
        if not is_valid_invocation_lifecycle_transition(current_state, next_state):
            current_value = (
                current_state.value
                if type(current_state) is InvocationLifecycleState
                else "<unknown>"
            )
            next_value = (
                next_state.value
                if type(next_state) is InvocationLifecycleState
                else "<unknown>"
            )
            raise ValueError(
                f"invalid lifecycle transition: {current_value} -> {next_value}"
            )
        history.append(next_state)

    @staticmethod
    def _result(
        request_id: str | None,
        history: list[InvocationLifecycleState],
        resolution: ProviderCapabilityResolution | None,
        compatible_provider_ids: tuple[str, ...],
        issues: list[InvocationLifecycleIssue],
    ) -> InvocationLifecycleResult:
        return InvocationLifecycleResult(
            request_id=request_id,
            state=history[-1],
            state_history=tuple(history),
            resolution=resolution,
            compatible_provider_ids=compatible_provider_ids,
            issues=tuple(issues),
        )

    @staticmethod
    def _failed_result_validation(
        lifecycle: object, message: str
    ) -> InvocationLifecycleResult:
        issue = InvocationLifecycleIssue(
            InvocationLifecycleIssueCode.RESULT_VALIDATION_FAILED, message
        )
        if type(lifecycle) is not InvocationLifecycleResult:
            return InvocationLifecycleResult(
                request_id=None,
                state=InvocationLifecycleState.RESULT_VALIDATION_FAILED,
                state_history=(InvocationLifecycleState.RESULT_VALIDATION_FAILED,),
                resolution=None,
                compatible_provider_ids=(),
                issues=(issue,),
            )
        history = list(lifecycle.state_history)
        if (
            history
            and history[-1] is InvocationLifecycleState.READY_FOR_AUTHORIZED_EXECUTION_LAYER
        ):
            try:
                ProviderInvocationCoordinator._transition(
                    history, InvocationLifecycleState.RESULT_VALIDATION_FAILED
                )
            except ValueError:
                history = [InvocationLifecycleState.RESULT_VALIDATION_FAILED]
        else:
            history = [InvocationLifecycleState.RESULT_VALIDATION_FAILED]
        return InvocationLifecycleResult(
            request_id=lifecycle.request_id,
            state=InvocationLifecycleState.RESULT_VALIDATION_FAILED,
            state_history=tuple(history),
            resolution=lifecycle.resolution,
            compatible_provider_ids=lifecycle.compatible_provider_ids,
            issues=tuple(lifecycle.issues) + (issue,),
            validated_result=None,
        )


def _thaw_builtin(value: object) -> object:
    value_type = type(value)
    if value is None or value_type in (str, bool, int, float):
        return value
    if value_type in (dict, MappingProxyType):
        return {key: _thaw_builtin(value[key]) for key in sorted(value)}
    if value_type in (list, tuple):
        return [_thaw_builtin(item) for item in value]
    raise ProviderInvocationValidationError(
        "request contains unsupported payload data."
    )
