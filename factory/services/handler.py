"""The factory's protocol address.

Serves `build_agent` only. The constitutional check is repeated here rather than
delegated: a request that reaches the factory over the protocol must name a human
authoriser, exactly as a direct call must. Article II is not weakened by the
message travelling over a bus.
"""

from __future__ import annotations

from typing import Callable, Dict, Iterable

from factory.runtime.factory import AgentFactory, ConstructionError
from factory.schemas.agent_spec import AgentSpec, SpecificationError
from protocols.institution.requests.request import (
    ACTION_BUILD_AGENT,
    InstitutionRequest,
    InstitutionResponse,
)

INSTITUTION = "factory"


class FactoryService:
    def __init__(self, factory: AgentFactory, input_source: Callable[[Dict], Iterable]):
        self.factory = factory
        self.input_source = input_source
        self.built: Dict[str, object] = {}

    def _refuse(self, request: InstitutionRequest, reason: str) -> InstitutionResponse:
        return InstitutionResponse(
            request_id=request.request_id,
            responder=INSTITUTION,
            accepted=False,
            result=None,
            reason=reason,
        )

    def __call__(self, request: InstitutionRequest) -> InstitutionResponse:
        if request.action != ACTION_BUILD_AGENT:
            return self._refuse(request, f"'{request.action}' is not served by {INSTITUTION}")

        if request.authorised_by.startswith("agent:"):
            return self._refuse(
                request,
                "refused under ARTICLE-002: an agent may not cause an agent to be created, "
                "including by asking an institution to do it",
            )

        spec_data = request.payload.get("spec")
        if not isinstance(spec_data, dict):
            return self._refuse(request, "build_agent requires a 'spec' mapping in the payload")

        try:
            spec = AgentSpec.from_dict(spec_data)
        except SpecificationError as error:
            return self._refuse(request, f"invalid specification: {error}")

        try:
            agent = self.factory.create_and_register(spec, self.input_source(request.payload))
        except (ConstructionError, RuntimeError) as error:
            return self._refuse(request, f"construction failed: {error}")

        self.built[spec.agent_id] = agent
        return InstitutionResponse(
            request_id=request.request_id,
            responder=INSTITUTION,
            accepted=True,
            result={"agent_id": spec.agent_id, "resumed_from": agent.resumed_from},
            reason="agent built and registered",
        )
