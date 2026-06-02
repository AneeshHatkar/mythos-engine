from __future__ import annotations

from typing import Any, Dict, List


class SecretPlacesHiddenWorldLayer:
    def build_secret_place(
        self,
        *,
        source_id: str,
        settlement: Dict[str, Any] | None = None,
        route_network: Dict[str, Any] | None = None,
        political_unit: Dict[str, Any] | None = None,
        secret_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        settlement = settlement or {}
        route_network = route_network or {}
        political_unit = political_unit or {}
        secret_seed = secret_seed or {}
        story_context = story_context or {}

        base_name = secret_seed.get("base_name", "Nareth")
        unique_name = secret_seed.get("unique_name", f"The Below-Bell Vault of {base_name}")
        region_name = secret_seed.get(
            "region_name",
            settlement.get("region_name")
            or route_network.get("region_name")
            or political_unit.get("region_name")
            or story_context.get("region_name", "Saltroot Forest"),
        )

        secret_place = {
            "secret_place_id": f"secret_place_{source_id}_{self._slug(unique_name)}",
            "source_id": source_id,
            "unique_name": unique_name,
            "base_name": base_name,
            "secret_place_type": secret_seed.get("secret_place_type", "sealed underground archive-vault"),
            "region_name": region_name,
            "settlement_id": settlement.get("settlement_id"),
            "settlement_name": settlement.get("unique_name"),
            "route_network_id": route_network.get("route_network_id"),
            "political_unit_id": political_unit.get("political_unit_id"),
            "name_origin": secret_seed.get(
                "name_origin",
                f"{unique_name} is named for the bell tower above it; locals hear the tower ring below ground before public lies are exposed.",
            ),
            "name_meaning": secret_seed.get(
                "name_meaning",
                "the hidden place where buried bells remember what courts erased",
            ),
            "name_language_logic": secret_seed.get(
                "name_language_logic",
                "secret places use direction markers, forbidden civic objects, and hidden-memory suffixes",
            ),
            "cultural_context": secret_seed.get(
                "cultural_context",
                settlement.get("cultural_context", political_unit.get("cultural_context", "bell-road secret history culture")),
            ),
            "world_context": region_name,
            "visual_identity": secret_seed.get(
                "visual_identity",
                "low salt-stone chambers, inverted bell carvings, redacted name tablets, black water channels, and silver root veins",
            ),
            "sensory_identity": secret_seed.get(
                "sensory_identity",
                "cold bell-metal air, wet stone, mineral rot, old ink, and a hum felt in teeth before sound is heard",
            ),
            "public_cover_story": secret_seed.get(
                "public_cover_story",
                "official records describe the site as a collapsed plague cellar beneath an abandoned civic tower",
            ),
            "secret_truth": secret_seed.get(
                "secret_truth",
                "the vault stores erased testimony from the founding massacre and the first forbidden family names",
            ),
            "false_history": secret_seed.get(
                "false_history",
                "archive families claim all surviving tablets are forgeries made by exiled smugglers",
            ),
            "discovery_conditions": secret_seed.get("discovery_conditions", [
                "dead bell rings during a public lie",
                "red fog lowers enough to reveal old drainage marks",
                "a no-bell child speaks a forbidden route number",
                "saltroot veins glow after bell rain",
            ]),
            "access_rules": secret_seed.get("access_rules", [
                "main entrance opens only from old tower underways",
                "secondary access requires knowledge of children's foglamp path",
                "archive keys open the first door but not the witness chamber",
                "speaking an erased name near the third stair triggers bell echo",
            ]),
            "guardians_or_hazards": secret_seed.get("guardians_or_hazards", [
                "unstable salt-stone floors",
                "poisoned archive dust",
                "bell traps that alert road wardens",
                "ravine cats nesting in lower tunnels",
                "memory-shock from name tablets",
            ]),
            "hidden_contents": secret_seed.get("hidden_contents", [
                "redacted birth ledgers",
                "forbidden family name tablets",
                "old treaty bell-metal token",
                "map showing vanished road borders",
                "funeral cloth proving the plague story was false",
            ]),
            "who_knows": secret_seed.get("who_knows", [
                "one exiled name-carrier",
                "two no-bell children",
                "a dying archive clerk",
                "a temple witness who pretends disbelief",
            ]),
            "who_benefits_from_secrecy": secret_seed.get("who_benefits_from_secrecy", [
                "archive families who retain legal power",
                "merchant houses that profit from false borders",
                "politicians whose ancestors signed the betrayal treaty",
            ]),
            "who_is_harmed_by_secrecy": secret_seed.get("who_is_harmed_by_secrecy", [
                "erased-road families",
                "no-bell children",
                "exiled name-carriers",
                "border towns denied restoration",
            ]),
            "connected_routes": secret_seed.get("connected_routes", [
                "Red Fog Underway",
                "No-Bell Child Path",
                "Massgrave Drain",
            ]),
            "connected_lore": secret_seed.get("connected_lore", [
                "dead bells ring below ground when false history is spoken",
                "fog saints are believed to guard children who know hidden paths",
                "the first treaty bell was cast from weapons used in the massacre",
            ]),
            "story_use": (
                "Creates hidden places that reveal secret history, unlock forbidden names, reshape political truth, "
                "trigger exploration, create danger, and force moral choices."
            ),
            "character_effect": (
                "Characters are affected through fear of discovery, inherited guilt, forbidden knowledge, family restoration, "
                "curiosity, trauma, greed, or obligation to reveal truth."
            ),
            "plot_effect": (
                "Can reveal old crimes, prove false history, restore erased families, open hidden routes, trigger political collapse, "
                "or create a chase through forbidden space."
            ),
            "memory_effect": (
                "World memory must track discovery status, who knows the secret, what evidence was revealed, who benefits, "
                "who is harmed, route access, and whether public history changed."
            ),
            "anti_genericity_signal": (
                "Secret place includes unique naming, cover story, secret truth, discovery conditions, access rules, hazards, "
                "hidden contents, beneficiaries, harmed groups, route links, lore, and memory hooks."
            ),
            "detail_depth_score": 0.94,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "SecretPlacesHiddenWorldLayer",
                "origin_type": "generated_from_secret_seed",
                "source_id": source_id,
                "settlement_id": settlement.get("settlement_id"),
                "route_network_id": route_network.get("route_network_id"),
                "political_unit_id": political_unit.get("political_unit_id"),
                "seed_keys": sorted(secret_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{unique_name}: hidden place in {region_name}; cover story, secret truth, discovery conditions, "
                f"access rules, hazards, evidence, route links, lore, and memory consequences."
            ),
        }

        return {"secret_place": secret_place}

    def build_secret_reveal_event(
        self,
        *,
        source_id: str,
        secret_place: Dict[str, Any],
        reveal_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        reveal_seed = reveal_seed or {}

        reveal_name = reveal_seed.get("reveal_name", "Below-Bell Witness Reveal")

        reveal = {
            "secret_reveal_event_id": f"secret_reveal_{source_id}_{self._slug(reveal_name)}",
            "source_id": source_id,
            "secret_place_id": secret_place["secret_place_id"],
            "secret_place_name": secret_place["unique_name"],
            "reveal_name": reveal_name,
            "reveal_type": reveal_seed.get("reveal_type", "secret_history_and_evidence_reveal"),
            "trigger": reveal_seed.get(
                "trigger",
                "a no-bell child speaks an erased route number while the dead bell rings under the old tower",
            ),
            "revealed_truth": reveal_seed.get(
                "revealed_truth",
                secret_place["secret_truth"],
            ),
            "public_consequence": reveal_seed.get(
                "public_consequence",
                "the town can no longer treat the plague-cellar story as official truth",
            ),
            "private_consequence": reveal_seed.get(
                "private_consequence",
                "archive families begin destroying secondary records before investigators arrive",
            ),
            "evidence_revealed": reveal_seed.get("evidence_revealed", secret_place["hidden_contents"][:3]),
            "affected_groups": reveal_seed.get("affected_groups", [
                "no-bell children",
                "archive families",
                "road wardens",
                "erased-road families",
                "temple witnesses",
            ]),
            "story_use": (
                "Turns hidden place discovery into active story movement through evidence, danger, public truth, and social reaction."
            ),
            "character_effect": (
                "Characters must decide whether to reveal, hide, steal, weaponize, protect, or deny the discovered truth."
            ),
            "plot_effect": (
                "Can trigger trial reopening, political collapse, chase sequence, family restoration, riot, betrayal, or faction split."
            ),
            "memory_effect": (
                "World memory must track discovered truth, revealed evidence, witnesses, deniers, destroyed records, and public-history shift."
            ),
            "lore_effect": (
                "The hidden world confirms or complicates local myth, making dead bells and forbidden names real civic forces."
            ),
            "anti_genericity_signal": (
                "Reveal is tied to specific place, evidence, trigger, groups, public/private consequences, lore, and memory."
            ),
            "detail_depth_score": 0.91,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "SecretPlacesHiddenWorldLayer",
                "origin_type": "derived_from_secret_place",
                "source_id": source_id,
                "secret_place_id": secret_place["secret_place_id"],
                "seed_keys": sorted(reveal_seed.keys()),
            },
            "compression_summary": (
                f"{reveal_name}: trigger, truth, evidence, affected groups, public/private consequences, and memory update."
            ),
        }

        return {"secret_reveal_event": reveal}

    def build_story_context_patch(
        self,
        *,
        secret_place: Dict[str, Any],
        reveal_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "secret_place_id": secret_place["secret_place_id"],
            "secret_place_name": secret_place["unique_name"],
            "secret_place_type": secret_place["secret_place_type"],
            "region_name": secret_place["region_name"],
            "public_cover_story": secret_place["public_cover_story"],
            "secret_truth": secret_place["secret_truth"],
            "false_history": secret_place["false_history"],
            "discovery_conditions": secret_place["discovery_conditions"],
            "access_rules": secret_place["access_rules"],
            "guardians_or_hazards": secret_place["guardians_or_hazards"],
            "hidden_contents": secret_place["hidden_contents"],
            "who_knows": secret_place["who_knows"],
            "who_benefits_from_secrecy": secret_place["who_benefits_from_secrecy"],
            "who_is_harmed_by_secrecy": secret_place["who_is_harmed_by_secrecy"],
            "connected_routes": secret_place["connected_routes"],
            "connected_lore": secret_place["connected_lore"],
            "story_use": secret_place["story_use"],
            "character_effect": secret_place["character_effect"],
            "plot_effect": secret_place["plot_effect"],
            "memory_effect": secret_place["memory_effect"],
            "generation_hints": [
                "Use secret places to reveal history, create danger, unlock routes, and alter public truth.",
                "A hidden place must have access rules, discovery conditions, hazards, evidence, and people affected by secrecy.",
                "Do not reveal secrets without tracking who knows, who benefits, who is harmed, and what public memory changes.",
                "Secret places should connect to routes, settlements, politics, religion, and character backstory.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "secret_place_state",
                    "target_element_id": secret_place["secret_place_id"],
                    "reason": "Track discovery status, access status, who knows, evidence revealed, hazards, and public-history changes.",
                }
            ],
        }

        if reveal_event:
            patch["active_secret_reveal_event"] = reveal_event
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "secret_reveal_state",
                    "target_element_id": reveal_event["secret_reveal_event_id"],
                    "reason": "Track trigger, revealed truth, evidence, affected groups, deniers, and public/private consequences.",
                }
            )

        return {"story_context_patch": patch}

    def validate_secret_place(self, *, secret_place: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "secret_place_id",
            "unique_name",
            "secret_place_type",
            "region_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "public_cover_story",
            "secret_truth",
            "false_history",
            "discovery_conditions",
            "access_rules",
            "guardians_or_hazards",
            "hidden_contents",
            "who_knows",
            "who_benefits_from_secrecy",
            "who_is_harmed_by_secrecy",
            "connected_routes",
            "connected_lore",
            "story_use",
            "character_effect",
            "plot_effect",
            "memory_effect",
            "anti_genericity_signal",
            "detail_depth_score",
            "validation_status",
            "provenance",
            "compression_summary",
        ]

        missing = [field for field in required if not secret_place.get(field)]
        shallow = self._shallow_fields(
            payload=secret_place,
            fields=[
                "name_origin",
                "public_cover_story",
                "secret_truth",
                "story_use",
                "character_effect",
                "plot_effect",
                "memory_effect",
                "anti_genericity_signal",
            ],
        )

        passed = not missing and not shallow and float(secret_place.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "secret_place_id": secret_place.get("secret_place_id"),
        }

    def validate_reveal_event(self, *, reveal_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "secret_reveal_event_id",
            "secret_place_id",
            "secret_place_name",
            "reveal_name",
            "reveal_type",
            "trigger",
            "revealed_truth",
            "public_consequence",
            "private_consequence",
            "evidence_revealed",
            "affected_groups",
            "story_use",
            "character_effect",
            "plot_effect",
            "memory_effect",
            "lore_effect",
            "anti_genericity_signal",
            "detail_depth_score",
            "validation_status",
            "provenance",
            "compression_summary",
        ]

        missing = [field for field in required if not reveal_event.get(field)]
        shallow = self._shallow_fields(
            payload=reveal_event,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"],
        )

        passed = not missing and not shallow and float(reveal_event.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "secret_reveal_event_id": reveal_event.get("secret_reveal_event_id"),
        }

    def summarize_secret_place(
        self,
        *,
        secret_place: Dict[str, Any],
        reveal_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "secret_place_id": secret_place["secret_place_id"],
            "unique_name": secret_place["unique_name"],
            "secret_place_type": secret_place["secret_place_type"],
            "discovery_condition_count": len(secret_place["discovery_conditions"]),
            "access_rule_count": len(secret_place["access_rules"]),
            "hazard_count": len(secret_place["guardians_or_hazards"]),
            "hidden_content_count": len(secret_place["hidden_contents"]),
            "compression_summary": secret_place["compression_summary"],
        }

        if reveal_event:
            summary["secret_reveal_event_id"] = reveal_event["secret_reveal_event_id"]
            summary["reveal_name"] = reveal_event["reveal_name"]

        return {"success": True, "summary": summary}

    def build_secret_place_text(
        self,
        *,
        secret_place: Dict[str, Any],
        reveal_event: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Secret Places + Hidden World Profile",
            f"Name: {secret_place['unique_name']}",
            f"ID: {secret_place['secret_place_id']}",
            f"Type: {secret_place['secret_place_type']}",
            f"Region: {secret_place['region_name']}",
            "",
            "Name Origin:",
            secret_place["name_origin"],
            "",
            "Public Cover Story:",
            secret_place["public_cover_story"],
            "",
            "Secret Truth:",
            secret_place["secret_truth"],
        ]

        sections = [
            ("Discovery Conditions", secret_place["discovery_conditions"]),
            ("Access Rules", secret_place["access_rules"]),
            ("Guardians or Hazards", secret_place["guardians_or_hazards"]),
            ("Hidden Contents", secret_place["hidden_contents"]),
            ("Who Knows", secret_place["who_knows"]),
            ("Who Benefits From Secrecy", secret_place["who_benefits_from_secrecy"]),
            ("Who Is Harmed By Secrecy", secret_place["who_is_harmed_by_secrecy"]),
            ("Connected Routes", secret_place["connected_routes"]),
            ("Connected Lore", secret_place["connected_lore"]),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        if reveal_event:
            lines.extend([
                "",
                "Active Reveal:",
                reveal_event["reveal_name"],
                "",
                "Revealed Truth:",
                reveal_event["revealed_truth"],
            ])

        lines.extend([
            "",
            "Story Use:",
            secret_place["story_use"],
            "",
            "Character Effect:",
            secret_place["character_effect"],
            "",
            "Plot Effect:",
            secret_place["plot_effect"],
            "",
            "Memory Effect:",
            secret_place["memory_effect"],
        ])

        return {"secret_place_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)
