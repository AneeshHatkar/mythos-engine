from typing import Any, Dict, List, Optional


class CausalChainExplanationEngine:
    """Builds causal graphs and why-explanations for simulation outcomes.

    This prevents MythOS from saying "it happened because plot."
    Every major event, choice, betrayal, reveal, relationship shift, or consequence
    should be explainable through prior causes.
    """

    engine_name = "simulation.causal_chain_explanation_engine"

    NODE_TYPES = {
        "event",
        "choice",
        "knowledge",
        "evidence",
        "rumor",
        "obligation",
        "leverage",
        "bargain",
        "relationship",
        "reputation",
        "resource",
        "faction",
        "consequence",
        "delta",
        "state",
        "user_intent",
        "plot_hook",
    }

    EDGE_TYPES = {
        "causes",
        "enables",
        "blocks",
        "pressures",
        "reveals",
        "distorts",
        "motivates",
        "damages",
        "repairs",
        "creates_debt",
        "creates_risk",
        "triggers",
        "resolves",
        "branches",
    }

    def create_causal_node(
        self,
        *,
        node_id: str,
        node_type: str,
        label: str,
        summary: str,
        entity_ids: List[str] | None = None,
        source_id: Optional[str] = None,
        confidence: float = 0.75,
        importance: float = 0.5,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if node_type not in self.NODE_TYPES:
            node_type = "state"

        return {
            "node_id": node_id,
            "node_type": node_type,
            "label": label,
            "summary": summary,
            "entity_ids": entity_ids or [],
            "source_id": source_id,
            "confidence": self._bounded(confidence),
            "importance": self._bounded(importance),
            "metadata": metadata or {},
        }

    def create_causal_edge(
        self,
        *,
        edge_id: str,
        source_node_id: str,
        target_node_id: str,
        edge_type: str,
        explanation: str,
        strength: float = 0.5,
        evidence_ids: List[str] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if edge_type not in self.EDGE_TYPES:
            edge_type = "causes"

        return {
            "edge_id": edge_id,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "edge_type": edge_type,
            "explanation": explanation,
            "strength": self._bounded(strength),
            "evidence_ids": evidence_ids or [],
            "metadata": metadata or {},
        }

    def register_causal_graph_on_state(
        self,
        *,
        state: Any,
        graph_id: str,
        nodes: List[Dict[str, Any]] | None = None,
        edges: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        graph = {
            "graph_id": graph_id,
            "nodes": {node["node_id"]: node for node in nodes or []},
            "edges": {edge["edge_id"]: edge for edge in edges or []},
            "created_from_engine": self.engine_name,
        }

        state.metadata.setdefault("causal_graphs", {})[graph_id] = graph
        state.metadata.setdefault("causal_graph_history", []).append(
            {
                "action": "register_causal_graph",
                "graph_id": graph_id,
                "node_count": len(graph["nodes"]),
                "edge_count": len(graph["edges"]),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "graph_id": graph_id,
            "updated_state": state,
        }

    def add_node_to_graph(
        self,
        *,
        state: Any,
        graph_id: str,
        node: Dict[str, Any],
    ) -> Dict[str, Any]:
        graph = self._get_or_create_graph(state, graph_id)
        graph["nodes"][node["node_id"]] = node

        state.metadata.setdefault("causal_graph_history", []).append(
            {
                "action": "add_node",
                "graph_id": graph_id,
                "node_id": node["node_id"],
                "node_type": node["node_type"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "graph_id": graph_id,
            "node_id": node["node_id"],
            "updated_state": state,
        }

    def add_edge_to_graph(
        self,
        *,
        state: Any,
        graph_id: str,
        edge: Dict[str, Any],
    ) -> Dict[str, Any]:
        graph = self._get_or_create_graph(state, graph_id)
        blockers = []

        if edge["source_node_id"] not in graph["nodes"]:
            blockers.append(f"source node {edge['source_node_id']} missing")
        if edge["target_node_id"] not in graph["nodes"]:
            blockers.append(f"target node {edge['target_node_id']} missing")

        if blockers:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "graph_id": graph_id,
                "edge_id": edge["edge_id"],
                "blockers": blockers,
                "updated_state": state,
            }

        graph["edges"][edge["edge_id"]] = edge

        state.metadata.setdefault("causal_graph_history", []).append(
            {
                "action": "add_edge",
                "graph_id": graph_id,
                "edge_id": edge["edge_id"],
                "edge_type": edge["edge_type"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "graph_id": graph_id,
            "edge_id": edge["edge_id"],
            "updated_state": state,
        }

    def build_graph_from_consequence_batch(
        self,
        *,
        state: Any,
        graph_id: str,
        consequence_id: str,
        delta_batch: Any,
    ) -> Dict[str, Any]:
        consequence = state.metadata.get("consequence_queue", {}).get(consequence_id, {})

        nodes = []
        edges = []

        consequence_node = self.create_causal_node(
            node_id=f"node_consequence_{consequence_id}",
            node_type="consequence",
            label=f"Consequence: {consequence_id}",
            summary=consequence.get("summary", "Queued consequence."),
            entity_ids=consequence.get("affected_entity_ids", []),
            source_id=consequence_id,
            confidence=0.9,
            importance=consequence.get("severity", 0.5),
        )
        nodes.append(consequence_node)

        source_choice_id = consequence.get("source_choice_id")
        if source_choice_id:
            choice_node = self.create_causal_node(
                node_id=f"node_choice_{source_choice_id}",
                node_type="choice",
                label=f"Choice: {source_choice_id}",
                summary=f"Choice {source_choice_id} created consequence {consequence_id}.",
                source_id=source_choice_id,
                confidence=0.85,
                importance=0.65,
            )
            nodes.append(choice_node)
            edges.append(
                self.create_causal_edge(
                    edge_id=f"edge_{source_choice_id}_causes_{consequence_id}",
                    source_node_id=choice_node["node_id"],
                    target_node_id=consequence_node["node_id"],
                    edge_type="causes",
                    explanation=f"Choice {source_choice_id} caused consequence {consequence_id}.",
                    strength=0.8,
                )
            )

        source_event_id = consequence.get("source_event_id")
        if source_event_id:
            event_node = self.create_causal_node(
                node_id=f"node_event_{source_event_id}",
                node_type="event",
                label=f"Event: {source_event_id}",
                summary=f"Event {source_event_id} contributed to consequence {consequence_id}.",
                source_id=source_event_id,
                confidence=0.8,
                importance=0.6,
            )
            nodes.append(event_node)
            edges.append(
                self.create_causal_edge(
                    edge_id=f"edge_{source_event_id}_triggers_{consequence_id}",
                    source_node_id=event_node["node_id"],
                    target_node_id=consequence_node["node_id"],
                    edge_type="triggers",
                    explanation=f"Event {source_event_id} triggered consequence {consequence_id}.",
                    strength=0.7,
                )
            )

        delta_nodes = self._nodes_from_delta_batch(delta_batch)
        nodes.extend(delta_nodes)

        for delta_node in delta_nodes:
            edges.append(
                self.create_causal_edge(
                    edge_id=f"edge_{consequence_node['node_id']}_creates_{delta_node['node_id']}",
                    source_node_id=consequence_node["node_id"],
                    target_node_id=delta_node["node_id"],
                    edge_type="triggers",
                    explanation=f"Consequence {consequence_id} generated {delta_node['node_type']} delta.",
                    strength=0.75,
                )
            )

        result = self.register_causal_graph_on_state(
            state=state,
            graph_id=graph_id,
            nodes=nodes,
            edges=edges,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "graph_id": graph_id,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "registered": result,
            "updated_state": state,
        }

    def build_graph_from_choice_report(
        self,
        *,
        state: Any,
        graph_id: str,
        choice_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        choice_id = choice_report.get("choice_id")
        actor_id = choice_report.get("actor_id")
        target_id = choice_report.get("target_id")
        action_type = choice_report.get("action_type")
        agency = choice_report.get("agency_report", {})
        score_components = agency.get("score_components", {})

        nodes = []
        edges = []

        choice_node = self.create_causal_node(
            node_id=f"node_choice_{choice_id}",
            node_type="choice",
            label=f"Choice: {choice_id}",
            summary=choice_report.get("summary", "Character choice."),
            entity_ids=[entity for entity in [actor_id, target_id] if entity],
            source_id=choice_id,
            confidence=choice_report.get("feasibility_score", 0.5),
            importance=choice_report.get("risk_profile", {}).get("overall_risk", 0.5),
            metadata={"action_type": action_type},
        )
        nodes.append(choice_node)

        actor_node = self.create_causal_node(
            node_id=f"node_actor_{actor_id}",
            node_type="state",
            label=f"Actor: {actor_id}",
            summary=f"{actor_id} is the actor making choice {choice_id}.",
            entity_ids=[actor_id],
            source_id=actor_id,
            confidence=0.9,
            importance=0.5,
        )
        nodes.append(actor_node)
        edges.append(
            self.create_causal_edge(
                edge_id=f"edge_actor_{actor_id}_motivates_{choice_id}",
                source_node_id=actor_node["node_id"],
                target_node_id=choice_node["node_id"],
                edge_type="motivates",
                explanation=f"{actor_id}'s state and motives shape the choice.",
                strength=0.6,
            )
        )

        for component, value in score_components.items():
            if isinstance(value, (int, float)) and float(value) >= 0.35:
                component_node = self.create_causal_node(
                    node_id=f"node_{choice_id}_{component}",
                    node_type="state",
                    label=component,
                    summary=f"{component} contributed {round(float(value), 3)} to this choice.",
                    entity_ids=[actor_id],
                    source_id=choice_id,
                    confidence=float(value),
                    importance=float(value),
                    metadata={"score_component": component},
                )
                nodes.append(component_node)
                edges.append(
                    self.create_causal_edge(
                        edge_id=f"edge_{component}_enables_{choice_id}",
                        source_node_id=component_node["node_id"],
                        target_node_id=choice_node["node_id"],
                        edge_type="enables" if component != "coercion_pressure" else "pressures",
                        explanation=f"{component} influenced the choice.",
                        strength=float(value),
                    )
                )

        for blocker in choice_report.get("blockers", []):
            blocker_node = self.create_causal_node(
                node_id=f"node_blocker_{self._safe_id(blocker)}",
                node_type="state",
                label="Blocker",
                summary=blocker,
                entity_ids=[actor_id],
                source_id=choice_id,
                confidence=0.9,
                importance=0.8,
            )
            nodes.append(blocker_node)
            edges.append(
                self.create_causal_edge(
                    edge_id=f"edge_blocker_{self._safe_id(blocker)}_blocks_{choice_id}",
                    source_node_id=blocker_node["node_id"],
                    target_node_id=choice_node["node_id"],
                    edge_type="blocks",
                    explanation=blocker,
                    strength=0.9,
                )
            )

        result = self.register_causal_graph_on_state(
            state=state,
            graph_id=graph_id,
            nodes=nodes,
            edges=edges,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "graph_id": graph_id,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "updated_state": state,
            "registered": result,
        }

    def explain_why(
        self,
        *,
        state: Any,
        graph_id: str,
        target_node_id: str,
        max_depth: int = 4,
    ) -> Dict[str, Any]:
        graph = state.metadata.get("causal_graphs", {}).get(graph_id)
        if not graph:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "graph_id": graph_id,
                "target_node_id": target_node_id,
                "errors": [f"causal graph {graph_id} not found"],
            }

        if target_node_id not in graph["nodes"]:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "graph_id": graph_id,
                "target_node_id": target_node_id,
                "errors": [f"target node {target_node_id} not found"],
            }

        causal_paths = self._backward_paths(graph, target_node_id, max_depth=max_depth)
        ranked_causes = self._rank_causes(graph, target_node_id)

        explanation = self._plain_language_explanation(
            graph=graph,
            target_node_id=target_node_id,
            causal_paths=causal_paths,
            ranked_causes=ranked_causes,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "graph_id": graph_id,
            "target_node_id": target_node_id,
            "target_node": graph["nodes"][target_node_id],
            "causal_paths": causal_paths,
            "ranked_causes": ranked_causes,
            "why_explanation": explanation,
            "confidence": self._explanation_confidence(graph, causal_paths),
            "warnings": self._explanation_warnings(causal_paths, ranked_causes),
        }

    def audit_causal_graph(self, *, state: Any, graph_id: str) -> Dict[str, Any]:
        graph = state.metadata.get("causal_graphs", {}).get(graph_id)
        if not graph:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "graph_id": graph_id,
                "errors": [f"causal graph {graph_id} not found"],
            }

        nodes = graph.get("nodes", {})
        edges = graph.get("edges", {})

        orphan_nodes = []
        invalid_edges = []
        weak_edges = []

        connected = set()
        for edge_id, edge in edges.items():
            source = edge.get("source_node_id")
            target = edge.get("target_node_id")

            if source not in nodes or target not in nodes:
                invalid_edges.append(edge_id)
            else:
                connected.add(source)
                connected.add(target)

            if float(edge.get("strength", 0.0)) < 0.25:
                weak_edges.append(edge_id)

        for node_id in nodes:
            if node_id not in connected and len(nodes) > 1:
                orphan_nodes.append(node_id)

        graph_score = self._graph_quality_score(nodes, edges, orphan_nodes, invalid_edges, weak_edges)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "graph_id": graph_id,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "orphan_nodes": orphan_nodes,
            "invalid_edges": invalid_edges,
            "weak_edges": weak_edges,
            "graph_quality_score": graph_score,
            "warnings": self._audit_warnings(orphan_nodes, invalid_edges, weak_edges, graph_score),
        }

    def build_causal_graph_map(self, *, state: Any) -> Dict[str, Any]:
        graphs = state.metadata.get("causal_graphs", {})
        records = {}

        for graph_id, graph in graphs.items():
            audit = self.audit_causal_graph(state=state, graph_id=graph_id)
            records[graph_id] = {
                "graph_id": graph_id,
                "node_count": audit.get("node_count", 0),
                "edge_count": audit.get("edge_count", 0),
                "graph_quality_score": audit.get("graph_quality_score", 0.0),
                "warning_count": len(audit.get("warnings", [])),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "graph_count": len(records),
            "causal_graph_records": records,
            "average_graph_quality": self._average([record["graph_quality_score"] for record in records.values()]),
        }

    def _nodes_from_delta_batch(self, delta_batch: Any) -> List[Dict[str, Any]]:
        nodes = []

        delta_groups = [
            ("relationship", getattr(delta_batch, "relationship_deltas", [])),
            ("reputation", getattr(delta_batch, "reputation_deltas", [])),
            ("knowledge", getattr(delta_batch, "knowledge_deltas", [])),
            ("resource", getattr(delta_batch, "resource_deltas", [])),
            ("faction", getattr(delta_batch, "faction_deltas", [])),
        ]

        for node_type, deltas in delta_groups:
            for delta in deltas:
                delta_id = getattr(delta, "delta_id", f"{node_type}_delta")
                target_entity_id = getattr(delta, "target_entity_id", None)
                reason = getattr(delta, "reason", f"{node_type} state changed.")
                nodes.append(
                    self.create_causal_node(
                        node_id=f"node_delta_{delta_id}",
                        node_type="delta",
                        label=f"{node_type.title()} delta",
                        summary=reason,
                        entity_ids=[target_entity_id] if target_entity_id else [],
                        source_id=delta_id,
                        confidence=0.85,
                        importance=0.6,
                        metadata={"delta_type": node_type},
                    )
                )

        return nodes

    def _get_or_create_graph(self, state: Any, graph_id: str) -> Dict[str, Any]:
        state.metadata.setdefault("causal_graphs", {})
        if graph_id not in state.metadata["causal_graphs"]:
            state.metadata["causal_graphs"][graph_id] = {
                "graph_id": graph_id,
                "nodes": {},
                "edges": {},
                "created_from_engine": self.engine_name,
            }
        return state.metadata["causal_graphs"][graph_id]

    def _backward_paths(self, graph: Dict[str, Any], target_node_id: str, max_depth: int) -> List[List[Dict[str, Any]]]:
        edges = graph.get("edges", {})
        incoming = {}
        for edge in edges.values():
            incoming.setdefault(edge["target_node_id"], []).append(edge)

        paths = []

        def walk(node_id: str, depth: int, path: List[Dict[str, Any]]):
            if depth >= max_depth or node_id not in incoming:
                if path:
                    paths.append(path)
                return

            for edge in incoming.get(node_id, []):
                source_node = graph["nodes"].get(edge["source_node_id"])
                if not source_node:
                    continue

                step = {
                    "from_node_id": edge["source_node_id"],
                    "from_label": source_node.get("label"),
                    "edge_type": edge.get("edge_type"),
                    "explanation": edge.get("explanation"),
                    "strength": edge.get("strength"),
                    "to_node_id": edge["target_node_id"],
                }
                walk(edge["source_node_id"], depth + 1, [step] + path)

        walk(target_node_id, 0, [])
        return paths

    def _rank_causes(self, graph: Dict[str, Any], target_node_id: str) -> List[Dict[str, Any]]:
        ranked = []
        for edge in graph.get("edges", {}).values():
            if edge.get("target_node_id") != target_node_id:
                continue
            source = graph.get("nodes", {}).get(edge.get("source_node_id"), {})
            ranked.append(
                {
                    "node_id": edge.get("source_node_id"),
                    "label": source.get("label"),
                    "node_type": source.get("node_type"),
                    "summary": source.get("summary"),
                    "edge_type": edge.get("edge_type"),
                    "strength": edge.get("strength"),
                    "importance": source.get("importance", 0.5),
                    "combined_score": round(float(edge.get("strength", 0.0)) * 0.6 + float(source.get("importance", 0.5)) * 0.4, 3),
                }
            )

        return sorted(ranked, key=lambda item: item["combined_score"], reverse=True)

    def _plain_language_explanation(
        self,
        *,
        graph: Dict[str, Any],
        target_node_id: str,
        causal_paths: List[List[Dict[str, Any]]],
        ranked_causes: List[Dict[str, Any]],
    ) -> str:
        target = graph["nodes"][target_node_id]
        target_label = target.get("label", target_node_id)

        if not ranked_causes:
            return f"{target_label} has no recorded upstream causes yet."

        main = ranked_causes[0]
        pieces = [
            f"{target_label} happened mainly because {main['label']} {main['edge_type']} it.",
        ]

        if len(ranked_causes) > 1:
            secondary = ", ".join(cause["label"] for cause in ranked_causes[1:3])
            pieces.append(f"Secondary causes include {secondary}.")

        if causal_paths:
            pieces.append(f"The graph contains {len(causal_paths)} causal path(s), so this outcome has traceable prior setup.")

        return " ".join(pieces)

    def _explanation_confidence(self, graph: Dict[str, Any], causal_paths: List[List[Dict[str, Any]]]) -> float:
        if not causal_paths:
            return 0.2

        strengths = []
        for path in causal_paths:
            for step in path:
                strengths.append(float(step.get("strength", 0.0)))

        if not strengths:
            return 0.3

        path_bonus = min(0.2, len(causal_paths) * 0.04)
        return round(min(1.0, self._average(strengths) * 0.8 + path_bonus), 3)

    def _explanation_warnings(self, causal_paths: List[List[Dict[str, Any]]], ranked_causes: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        if not causal_paths:
            warnings.append("no causal paths found")
        if not ranked_causes:
            warnings.append("no direct causes found")
        if ranked_causes and ranked_causes[0]["combined_score"] < 0.35:
            warnings.append("top cause is weak; outcome may feel under-motivated")
        return warnings

    def _graph_quality_score(
        self,
        nodes: Dict[str, Any],
        edges: Dict[str, Any],
        orphan_nodes: List[str],
        invalid_edges: List[str],
        weak_edges: List[str],
    ) -> float:
        if not nodes:
            return 0.0

        density = min(1.0, len(edges) / max(1, len(nodes)))
        penalty = len(orphan_nodes) * 0.08 + len(invalid_edges) * 0.20 + len(weak_edges) * 0.04

        return round(max(0.0, min(1.0, 0.45 + density * 0.45 - penalty)), 3)

    def _audit_warnings(
        self,
        orphan_nodes: List[str],
        invalid_edges: List[str],
        weak_edges: List[str],
        graph_score: float,
    ) -> List[str]:
        warnings = []
        if orphan_nodes:
            warnings.append(f"{len(orphan_nodes)} orphan node(s) found")
        if invalid_edges:
            warnings.append(f"{len(invalid_edges)} invalid edge(s) found")
        if weak_edges:
            warnings.append(f"{len(weak_edges)} weak edge(s) found")
        if graph_score < 0.45:
            warnings.append("causal graph quality is low")
        return warnings

    def _safe_id(self, text: str) -> str:
        cleaned = "".join(char.lower() if char.isalnum() else "_" for char in text)
        return cleaned[:60].strip("_") or "item"

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)
