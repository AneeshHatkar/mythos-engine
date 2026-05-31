from typing import Any, Dict, List, Optional, Set, Tuple


class SocialNetworkInfluenceEngine:
    """Analyzes social influence, reputation pressure, rumor reach, and coalition dynamics.

    This engine connects relationships, factions, rumors, reputation, and public
    events into a social graph. It helps MythOS decide who can influence whom,
    who can spread information, who is socially isolated, and which characters
    are powerful bridges in the story network.
    """

    engine_name = "simulation.social_network_influence_engine"

    EDGE_TYPES = {
        "relationship",
        "faction",
        "rumor_channel",
        "obligation",
        "leverage",
        "bargain",
        "witness",
        "location",
    }

    def build_social_graph(
        self,
        *,
        state: Any,
        include_factions: bool = True,
        include_locations: bool = True,
    ) -> Dict[str, Any]:
        nodes: Dict[str, Dict[str, Any]] = {}
        edges: Dict[str, Dict[str, Any]] = {}

        for character_id, character in state.character_states.items():
            nodes[character_id] = {
                "node_id": character_id,
                "node_type": "character",
                "label": character_id,
                "location_id": character.current_location_id,
                "status_flags": character.metadata.get("status_flags", []),
                "metadata": character.metadata,
            }

        if include_factions:
            faction_ids = self._faction_ids_from_state(state)
            for faction_id in faction_ids:
                nodes[faction_id] = {
                    "node_id": faction_id,
                    "node_type": "faction",
                    "label": faction_id,
                    "metadata": {},
                }

        if include_locations:
            location_ids = self._location_ids_from_state(state)
            for location_id in location_ids:
                nodes[location_id] = {
                    "node_id": location_id,
                    "node_type": "location",
                    "label": location_id,
                    "metadata": {},
                }

        # Relationship edges.
        for relationship_id, rel in state.relationship_states.items():
            strength = self._relationship_influence_strength(rel)
            edges[relationship_id] = {
                "edge_id": relationship_id,
                "edge_type": "relationship",
                "source_id": rel.character_a_id,
                "target_id": rel.character_b_id,
                "bidirectional": True,
                "strength": strength,
                "trust": rel.trust,
                "respect": rel.respect,
                "affection": rel.affection,
                "rivalry": rel.rivalry,
                "resentment": rel.resentment,
                "fear": rel.fear,
                "metadata": {"relationship_id": relationship_id},
            }

        # Faction membership/influence edges from character metadata.
        if include_factions:
            for character_id, character in state.character_states.items():
                faction_ids = character.metadata.get("faction_ids", []) + character.metadata.get("affiliation_ids", [])
                for faction_id in faction_ids:
                    edge_id = f"edge_faction_{character_id}_{faction_id}"
                    edges[edge_id] = {
                        "edge_id": edge_id,
                        "edge_type": "faction",
                        "source_id": character_id,
                        "target_id": faction_id,
                        "bidirectional": True,
                        "strength": float(character.metadata.get("faction_influence", 0.45)),
                        "metadata": {"membership": True},
                    }

        # Same-location weak social visibility edges.
        if include_locations:
            for character_id, character in state.character_states.items():
                if character.current_location_id:
                    edge_id = f"edge_location_{character_id}_{character.current_location_id}"
                    edges[edge_id] = {
                        "edge_id": edge_id,
                        "edge_type": "location",
                        "source_id": character_id,
                        "target_id": character.current_location_id,
                        "bidirectional": True,
                        "strength": 0.25,
                        "metadata": {"current_location": True},
                    }

        # Obligation edges.
        for obligation_id, obligation in state.metadata.get("obligation_registry", {}).items():
            promiser = obligation.get("promiser_id")
            promisee = obligation.get("promisee_id")
            if promiser and promisee:
                pressure = float(obligation.get("pressure_score", 0.5))
                edges[f"edge_obligation_{obligation_id}"] = {
                    "edge_id": f"edge_obligation_{obligation_id}",
                    "edge_type": "obligation",
                    "source_id": promiser,
                    "target_id": promisee,
                    "bidirectional": False,
                    "strength": self._bounded(pressure),
                    "metadata": {"obligation_id": obligation_id, "status": obligation.get("status")},
                }

        # Leverage edges.
        for leverage_id, leverage in state.metadata.get("leverage_registry", {}).items():
            holder = leverage.get("holder_id")
            target = leverage.get("target_id")
            if holder and target:
                pressure = float(leverage.get("pressure_level", 0.5))
                edges[f"edge_leverage_{leverage_id}"] = {
                    "edge_id": f"edge_leverage_{leverage_id}",
                    "edge_type": "leverage",
                    "source_id": holder,
                    "target_id": target,
                    "bidirectional": False,
                    "strength": self._bounded(pressure),
                    "metadata": {"leverage_id": leverage_id, "status": leverage.get("status")},
                }

        # Rumor channel edges from world metadata.
        for idx, edge in enumerate(state.world_state.metadata.get("rumor_edges", [])):
            source = edge.get("from_location_id")
            target = edge.get("to_location_id")
            if source and target:
                edge_id = f"edge_rumor_channel_{idx}_{source}_{target}"
                edges[edge_id] = {
                    "edge_id": edge_id,
                    "edge_type": "rumor_channel",
                    "source_id": source,
                    "target_id": target,
                    "bidirectional": bool(edge.get("bidirectional", True)),
                    "strength": self._bounded(float(edge.get("strength", 0.45))),
                    "metadata": dict(edge),
                }

        graph = {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }

        state.metadata.setdefault("social_graphs", {})["latest_social_graph"] = graph

        return {
            "success": True,
            "engine_name": self.engine_name,
            "social_graph": graph,
            "warnings": self._graph_warnings(graph),
        }

    def calculate_character_influence(
        self,
        *,
        state: Any,
        character_id: str,
        graph: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        graph = graph or self.build_social_graph(state=state)["social_graph"]

        if character_id not in graph["nodes"]:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "character_id": character_id,
                "errors": [f"character {character_id} missing from social graph"],
            }

        connected_edges = self._connected_edges(graph, character_id)
        outgoing = [edge for edge in connected_edges if edge["source_id"] == character_id]
        incoming = [edge for edge in connected_edges if edge["target_id"] == character_id or edge.get("bidirectional")]

        relationship_power = sum(edge["strength"] for edge in connected_edges if edge["edge_type"] == "relationship")
        faction_power = sum(edge["strength"] for edge in connected_edges if edge["edge_type"] == "faction")
        leverage_power = sum(edge["strength"] for edge in outgoing if edge["edge_type"] == "leverage")
        obligation_pressure = sum(edge["strength"] for edge in incoming if edge["edge_type"] == "obligation")
        location_visibility = sum(edge["strength"] for edge in connected_edges if edge["edge_type"] == "location")

        centrality = self._degree_centrality(graph, character_id)
        bridge_score = self._bridge_score(graph, character_id)

        reputation = state.character_states.get(character_id).metadata.get("reputation_state", {}) if character_id in state.character_states else {}
        public_reputation = float(reputation.get("public", reputation.get("general", 0.0)) or 0.0)

        influence_score = round(
            min(
                1.0,
                centrality * 0.22
                + bridge_score * 0.18
                + min(1.0, relationship_power) * 0.18
                + min(1.0, faction_power) * 0.14
                + min(1.0, leverage_power) * 0.10
                + min(1.0, location_visibility) * 0.08
                + max(0.0, public_reputation) * 0.10
                - min(0.30, obligation_pressure * 0.05),
            ),
            3,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_id": character_id,
            "influence_score": influence_score,
            "centrality": centrality,
            "bridge_score": bridge_score,
            "relationship_power": round(min(1.0, relationship_power), 3),
            "faction_power": round(min(1.0, faction_power), 3),
            "leverage_power": round(min(1.0, leverage_power), 3),
            "obligation_pressure": round(min(1.0, obligation_pressure), 3),
            "location_visibility": round(min(1.0, location_visibility), 3),
            "public_reputation": round(public_reputation, 3),
            "connected_edge_count": len(connected_edges),
            "warnings": self._character_influence_warnings(character_id, influence_score, centrality, bridge_score),
        }

    def calculate_influence_path(
        self,
        *,
        state: Any,
        source_id: str,
        target_id: str,
        graph: Optional[Dict[str, Any]] = None,
        max_depth: int = 4,
    ) -> Dict[str, Any]:
        graph = graph or self.build_social_graph(state=state)["social_graph"]

        if source_id not in graph["nodes"]:
            return self._path_error(source_id, target_id, f"source {source_id} missing from graph")
        if target_id not in graph["nodes"]:
            return self._path_error(source_id, target_id, f"target {target_id} missing from graph")

        paths = self._find_paths(graph, source_id, target_id, max_depth=max_depth)
        scored_paths = [self._score_path(graph, path) for path in paths]
        ranked = sorted(scored_paths, key=lambda item: item["path_strength"], reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "source_id": source_id,
            "target_id": target_id,
            "path_count": len(ranked),
            "best_path": ranked[0] if ranked else None,
            "ranked_paths": ranked,
            "can_influence": bool(ranked and ranked[0]["path_strength"] >= 0.25),
            "warnings": [] if ranked else [f"no influence path from {source_id} to {target_id}"],
        }

    def evaluate_rumor_reach(
        self,
        *,
        state: Any,
        origin_id: str,
        rumor_id: Optional[str] = None,
        max_depth: int = 3,
    ) -> Dict[str, Any]:
        graph = self.build_social_graph(state=state)["social_graph"]

        if origin_id not in graph["nodes"]:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "origin_id": origin_id,
                "errors": [f"origin {origin_id} missing from graph"],
            }

        reachable = {}
        frontier = [(origin_id, 0, 1.0)]
        visited = {origin_id}

        while frontier:
            node_id, depth, strength = frontier.pop(0)
            if depth >= max_depth:
                continue

            neighbors = self._neighbors(graph, node_id)
            for neighbor_id, edge in neighbors:
                if neighbor_id in visited:
                    continue
                edge_strength = float(edge.get("strength", 0.3))
                new_strength = round(strength * edge_strength * self._rumor_edge_multiplier(edge), 3)
                if new_strength < 0.05:
                    continue
                visited.add(neighbor_id)
                reachable[neighbor_id] = {
                    "node_id": neighbor_id,
                    "node_type": graph["nodes"].get(neighbor_id, {}).get("node_type"),
                    "depth": depth + 1,
                    "rumor_reach_strength": new_strength,
                    "via_edge_type": edge.get("edge_type"),
                }
                frontier.append((neighbor_id, depth + 1, new_strength))

        character_reach = {
            node_id: data
            for node_id, data in reachable.items()
            if data.get("node_type") == "character"
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "origin_id": origin_id,
            "rumor_id": rumor_id,
            "reachable_count": len(reachable),
            "reachable_character_count": len(character_reach),
            "reachable_nodes": reachable,
            "reachable_characters": character_reach,
            "reach_score": round(min(1.0, sum(item["rumor_reach_strength"] for item in character_reach.values()) / max(1, len(graph["nodes"]))), 3),
        }

    def detect_coalitions(
        self,
        *,
        state: Any,
        graph: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        graph = graph or self.build_social_graph(state=state)["social_graph"]
        character_ids = [node_id for node_id, node in graph["nodes"].items() if node["node_type"] == "character"]

        visited: Set[str] = set()
        coalitions = []

        for character_id in character_ids:
            if character_id in visited:
                continue

            component = self._positive_relationship_component(graph, character_id, visited)
            if component:
                coalition_id = f"coalition_{len(coalitions) + 1}"
                cohesion = self._coalition_cohesion(graph, component)
                coalitions.append(
                    {
                        "coalition_id": coalition_id,
                        "member_ids": sorted(component),
                        "member_count": len(component),
                        "cohesion_score": cohesion,
                        "dominant_member_id": self._dominant_member(state, graph, component),
                        "coalition_type": self._coalition_type(cohesion, len(component)),
                    }
                )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "coalition_count": len(coalitions),
            "coalitions": coalitions,
            "warnings": self._coalition_warnings(coalitions),
        }

    def detect_isolated_characters(
        self,
        *,
        state: Any,
        graph: Optional[Dict[str, Any]] = None,
        isolation_threshold: float = 0.18,
    ) -> Dict[str, Any]:
        graph = graph or self.build_social_graph(state=state)["social_graph"]
        isolated = []

        for node_id, node in graph["nodes"].items():
            if node["node_type"] != "character":
                continue

            influence = self.calculate_character_influence(state=state, character_id=node_id, graph=graph)
            if influence["centrality"] <= isolation_threshold and influence["relationship_power"] <= isolation_threshold:
                isolated.append(
                    {
                        "character_id": node_id,
                        "centrality": influence["centrality"],
                        "relationship_power": influence["relationship_power"],
                        "influence_score": influence["influence_score"],
                    }
                )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "isolated_count": len(isolated),
            "isolated_characters": isolated,
            "warnings": [f"{item['character_id']} is socially isolated" for item in isolated],
        }

    def build_social_influence_map(self, *, state: Any) -> Dict[str, Any]:
        graph_result = self.build_social_graph(state=state)
        graph = graph_result["social_graph"]

        character_influence = {}
        for node_id, node in graph["nodes"].items():
            if node["node_type"] == "character":
                character_influence[node_id] = self.calculate_character_influence(
                    state=state,
                    character_id=node_id,
                    graph=graph,
                )

        coalitions = self.detect_coalitions(state=state, graph=graph)
        isolated = self.detect_isolated_characters(state=state, graph=graph)

        ranked_characters = sorted(
            [
                {
                    "character_id": character_id,
                    "influence_score": report["influence_score"],
                    "centrality": report["centrality"],
                    "bridge_score": report["bridge_score"],
                }
                for character_id, report in character_influence.items()
            ],
            key=lambda item: item["influence_score"],
            reverse=True,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "graph": graph,
            "ranked_characters": ranked_characters,
            "character_influence": character_influence,
            "coalitions": coalitions["coalitions"],
            "isolated_characters": isolated["isolated_characters"],
            "warnings": graph_result["warnings"] + coalitions["warnings"] + isolated["warnings"],
            "chunk5_handoff": self._chunk5_handoff(ranked_characters, coalitions["coalitions"], isolated["isolated_characters"]),
        }

    def _relationship_influence_strength(self, rel: Any) -> float:
        positive = rel.trust * 0.25 + rel.respect * 0.20 + rel.affection * 0.18 + rel.loyalty * 0.18
        negative = rel.fear * 0.08 + rel.rivalry * 0.06 + rel.resentment * 0.05
        asymmetry = rel.power_imbalance * 0.10 + rel.knowledge_asymmetry * 0.08
        return round(min(1.0, max(0.05, positive + negative + asymmetry)), 3)

    def _connected_edges(self, graph: Dict[str, Any], node_id: str) -> List[Dict[str, Any]]:
        connected = []
        for edge in graph["edges"].values():
            if edge["source_id"] == node_id or edge["target_id"] == node_id:
                connected.append(edge)
        return connected

    def _degree_centrality(self, graph: Dict[str, Any], node_id: str) -> float:
        node_count = max(1, len(graph["nodes"]) - 1)
        connected_nodes = set()
        for edge in self._connected_edges(graph, node_id):
            connected_nodes.add(edge["source_id"])
            connected_nodes.add(edge["target_id"])
        connected_nodes.discard(node_id)
        return round(min(1.0, len(connected_nodes) / node_count), 3)

    def _bridge_score(self, graph: Dict[str, Any], node_id: str) -> float:
        neighbors = {neighbor for neighbor, _ in self._neighbors(graph, node_id)}
        if len(neighbors) < 2:
            return 0.0

        neighbor_types = {graph["nodes"].get(neighbor, {}).get("node_type") for neighbor in neighbors}
        edge_types = {edge["edge_type"] for edge in self._connected_edges(graph, node_id)}

        return round(min(1.0, len(neighbor_types) * 0.18 + len(edge_types) * 0.12 + len(neighbors) * 0.04), 3)

    def _neighbors(self, graph: Dict[str, Any], node_id: str) -> List[Tuple[str, Dict[str, Any]]]:
        neighbors = []
        for edge in graph["edges"].values():
            if edge["source_id"] == node_id:
                neighbors.append((edge["target_id"], edge))
            if edge.get("bidirectional") and edge["target_id"] == node_id:
                neighbors.append((edge["source_id"], edge))
        return neighbors

    def _find_paths(self, graph: Dict[str, Any], source_id: str, target_id: str, max_depth: int) -> List[List[str]]:
        paths = []

        def walk(current: str, target: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            if current == target:
                paths.append(path[:])
                return
            for neighbor, _edge in self._neighbors(graph, current):
                if neighbor in path:
                    continue
                walk(neighbor, target, path + [neighbor], depth + 1)

        walk(source_id, target_id, [source_id], 0)
        return paths

    def _score_path(self, graph: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
        if len(path) <= 1:
            return {
                "path": path,
                "path_strength": 1.0,
                "edge_types": [],
                "hop_count": 0,
            }

        strengths = []
        edge_types = []
        for idx in range(len(path) - 1):
            edge = self._edge_between(graph, path[idx], path[idx + 1])
            if edge:
                strengths.append(float(edge.get("strength", 0.25)))
                edge_types.append(edge.get("edge_type"))

        strength = 1.0
        for item in strengths:
            strength *= item

        hop_penalty = max(0.2, 1.0 - (len(path) - 2) * 0.12)

        return {
            "path": path,
            "path_strength": round(strength * hop_penalty, 3),
            "edge_types": edge_types,
            "hop_count": len(path) - 1,
        }

    def _edge_between(self, graph: Dict[str, Any], source: str, target: str) -> Optional[Dict[str, Any]]:
        for edge in graph["edges"].values():
            if edge["source_id"] == source and edge["target_id"] == target:
                return edge
            if edge.get("bidirectional") and edge["source_id"] == target and edge["target_id"] == source:
                return edge
        return None

    def _rumor_edge_multiplier(self, edge: Dict[str, Any]) -> float:
        if edge["edge_type"] == "rumor_channel":
            return 1.15
        if edge["edge_type"] == "relationship":
            return 0.95
        if edge["edge_type"] == "location":
            return 0.70
        if edge["edge_type"] == "faction":
            return 0.85
        if edge["edge_type"] == "leverage":
            return 0.45
        return 0.75

    def _positive_relationship_component(self, graph: Dict[str, Any], start: str, visited: Set[str]) -> Set[str]:
        component = set()
        stack = [start]

        while stack:
            node_id = stack.pop()
            if node_id in visited:
                continue
            visited.add(node_id)
            component.add(node_id)

            for neighbor, edge in self._neighbors(graph, node_id):
                if graph["nodes"].get(neighbor, {}).get("node_type") != "character":
                    continue
                if edge["edge_type"] == "relationship" and edge.get("strength", 0.0) >= 0.35:
                    stack.append(neighbor)

        return component

    def _coalition_cohesion(self, graph: Dict[str, Any], members: Set[str]) -> float:
        if len(members) <= 1:
            return 0.0

        possible = len(members) * (len(members) - 1) / 2
        actual_strength = 0.0

        members_list = list(members)
        for i in range(len(members_list)):
            for j in range(i + 1, len(members_list)):
                edge = self._edge_between(graph, members_list[i], members_list[j])
                if edge and edge["edge_type"] == "relationship":
                    actual_strength += float(edge.get("strength", 0.0))

        return round(min(1.0, actual_strength / max(1.0, possible)), 3)

    def _dominant_member(self, state: Any, graph: Dict[str, Any], members: Set[str]) -> Optional[str]:
        if not members:
            return None
        ranked = [
            self.calculate_character_influence(state=state, character_id=member, graph=graph)
            for member in members
        ]
        ranked = [item for item in ranked if item.get("success")]
        if not ranked:
            return None
        return max(ranked, key=lambda item: item["influence_score"])["character_id"]

    def _coalition_type(self, cohesion: float, size: int) -> str:
        if size <= 1:
            return "isolated_character"
        if cohesion >= 0.65:
            return "tight_coalition"
        if cohesion >= 0.35:
            return "loose_coalition"
        return "fragile_cluster"

    def _faction_ids_from_state(self, state: Any) -> List[str]:
        faction_ids = set()
        for character in state.character_states.values():
            faction_ids.update(character.metadata.get("faction_ids", []))
            faction_ids.update(character.metadata.get("affiliation_ids", []))
        for obligation in state.metadata.get("obligation_registry", {}).values():
            faction_ids.update(obligation.get("involved_faction_ids", []))
        for bargain in state.metadata.get("bargain_registry", {}).values():
            faction_ids.update(bargain.get("linked_faction_ids", []))
        return sorted(faction_ids)

    def _location_ids_from_state(self, state: Any) -> List[str]:
        ids = set()
        for character in state.character_states.values():
            if character.current_location_id:
                ids.add(character.current_location_id)
        for edge in state.world_state.metadata.get("rumor_edges", []):
            if edge.get("from_location_id"):
                ids.add(edge["from_location_id"])
            if edge.get("to_location_id"):
                ids.add(edge["to_location_id"])
        return sorted(ids)

    def _graph_warnings(self, graph: Dict[str, Any]) -> List[str]:
        warnings = []
        if graph["node_count"] == 0:
            warnings.append("social graph has no nodes")
        if graph["edge_count"] == 0 and graph["node_count"] > 1:
            warnings.append("social graph has nodes but no edges")
        return warnings

    def _character_influence_warnings(self, character_id: str, influence: float, centrality: float, bridge: float) -> List[str]:
        warnings = []
        if influence < 0.15:
            warnings.append(f"{character_id} has very low social influence")
        if centrality < 0.10:
            warnings.append(f"{character_id} is socially peripheral")
        if bridge >= 0.65:
            warnings.append(f"{character_id} is a major bridge character")
        return warnings

    def _coalition_warnings(self, coalitions: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        for coalition in coalitions:
            if coalition["coalition_type"] == "tight_coalition" and coalition["member_count"] >= 3:
                warnings.append(f"{coalition['coalition_id']} is a strong social bloc")
            if coalition["coalition_type"] == "isolated_character":
                warnings.append(f"{coalition['member_ids'][0]} has no strong coalition")
        return warnings

    def _chunk5_handoff(
        self,
        ranked_characters: List[Dict[str, Any]],
        coalitions: List[Dict[str, Any]],
        isolated: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "social_center_character_id": ranked_characters[0]["character_id"] if ranked_characters else None,
            "major_bridge_character_ids": [
                item["character_id"] for item in ranked_characters if item["bridge_score"] >= 0.55
            ],
            "coalition_scene_hooks": [
                {
                    "coalition_id": coalition["coalition_id"],
                    "member_ids": coalition["member_ids"],
                    "scene_type": "coalition_pressure_scene",
                }
                for coalition in coalitions if coalition["member_count"] > 1
            ],
            "isolation_scene_hooks": [
                {
                    "character_id": item["character_id"],
                    "scene_type": "isolation_or_exclusion_scene",
                }
                for item in isolated
            ],
        }

    def _path_error(self, source_id: str, target_id: str, error: str) -> Dict[str, Any]:
        return {
            "success": False,
            "engine_name": self.engine_name,
            "source_id": source_id,
            "target_id": target_id,
            "errors": [error],
        }

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)
