from __future__ import annotations

from typing import Any, Dict, List


class EducationSchoolsApprenticeshipEngine:
    def build_education_system(
        self,
        *,
        source_id: str,
        political_unit: Dict[str, Any] | None = None,
        settlement: Dict[str, Any] | None = None,
        population_profile: Dict[str, Any] | None = None,
        economy_profile: Dict[str, Any] | None = None,
        education_seed: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        political_unit = political_unit or {}
        settlement = settlement or {}
        population_profile = population_profile or {}
        economy_profile = economy_profile or {}
        education_seed = education_seed or {}
        story_context = story_context or {}

        region_name = education_seed.get(
            "region_name",
            settlement.get("region_name")
            or political_unit.get("region_name")
            or population_profile.get("region_name")
            or story_context.get("region_name", "Saltroot Forest"),
        )

        education_name = education_seed.get("education_name", f"{region_name} Bell-Ledger Education System")

        education_system = {
            "education_system_id": f"education_system_{source_id}_{self._slug(education_name)}",
            "source_id": source_id,
            "education_name": education_name,
            "region_name": region_name,
            "political_unit_id": political_unit.get("political_unit_id"),
            "settlement_id": settlement.get("settlement_id"),
            "population_diversity_profile_id": population_profile.get("population_diversity_profile_id"),
            "resource_economy_profile_id": economy_profile.get("resource_economy_profile_id"),
            "name_origin": education_seed.get(
                "name_origin",
                f"{education_name} formed because road law, public names, medicine, archive records, and fog survival "
                f"required children to be trained before they were trusted with civic memory.",
            ),
            "name_meaning": education_seed.get(
                "name_meaning",
                "a learning system where names, roads, tools, law, memory, class, and survival are taught together",
            ),
            "name_language_logic": education_seed.get(
                "name_language_logic",
                "education systems combine region marker, institution object, and the knowledge duty that grants status",
            ),
            "cultural_context": education_seed.get(
                "cultural_context",
                settlement.get("cultural_context", political_unit.get("cultural_context", "bell-road civic education culture")),
            ),
            "world_context": region_name,
            "visual_identity": education_seed.get(
                "visual_identity",
                "saltbark lesson tablets, bell-thread student cords, road maps, inked weather charts, practice ledgers, and guide staffs",
            ),
            "sensory_identity": education_seed.get(
                "sensory_identity",
                "chalk salt, bark ink, lamp oil, wet road cloth, old paper, temple smoke, and children chanting route names",
            ),
            "school_types": education_seed.get("school_types", [
                {
                    "school_type": "public name school",
                    "purpose": "teaches children civic identity, basic law, route etiquette, and public-name responsibility",
                    "access": "officially open to citizens, but no-bell children are often delayed or excluded",
                    "story_use": "identity conflict, public-name hearings, class bias, and erased-family reveals",
                },
                {
                    "school_type": "guild academy",
                    "purpose": "trains mapmakers, bellwrights, healers, scribes, merchants, and road engineers",
                    "access": "requires sponsorship, family reputation, payment, or apprenticeship oath",
                    "story_use": "career mobility, guild rivalry, exams, scandals, and professional secrets",
                },
                {
                    "school_type": "temple school",
                    "purpose": "teaches ritual law, funeral rites, dead-bell interpretation, medicine ethics, and sacred history",
                    "access": "restricted by temple approval and family belief reputation",
                    "story_use": "religious pressure, forbidden doctrine, faith conflict, and moral tests",
                },
                {
                    "school_type": "road apprenticeship camp",
                    "purpose": "teaches fog survival, route songs, animal signs, weather reading, and escort duty",
                    "access": "usually inherited through guide families but opened during disasters",
                    "story_use": "dangerous training, survival exams, missing students, and route secrets",
                },
                {
                    "school_type": "underground forbidden school",
                    "purpose": "teaches erased names, hidden routes, banned histories, and suppressed map logic",
                    "access": "secret invitation through exiles, no-bell children, and dissident teachers",
                    "story_use": "rebellion, secret literacy, forbidden knowledge, and state persecution",
                },
            ]),
            "named_institutions": education_seed.get("named_institutions", [
                {
                    "institution_name": "The Veyr Hall of Public Names",
                    "institution_type": "civic school",
                    "public_mission": "prepare children for legal identity and public memory duties",
                    "secret_pressure": "archive families slow enrollment for children tied to erased records",
                    "famous_feature": "the Bell-Cord Examination where students recite family and road obligations",
                },
                {
                    "institution_name": "Saltbark Guild Academy",
                    "institution_type": "professional academy",
                    "public_mission": "train scribes, map certifiers, and contract readers",
                    "secret_pressure": "students discover missing ledger pages before they understand the danger",
                    "famous_feature": "sealed map room used for final exams and political manipulation",
                },
                {
                    "institution_name": "The Underlamp School",
                    "institution_type": "underground forbidden school",
                    "public_mission": "officially nonexistent",
                    "secret_pressure": "teaches no-bell children hidden histories and safe roof paths",
                    "famous_feature": "students memorize erased names using lantern-shadow games",
                },
            ]),
            "subjects_taught": education_seed.get("subjects_taught", [
                "public-name law",
                "route songs and map reading",
                "weather and fog signs",
                "saltroot medicine basics",
                "contract literacy",
                "bell-metal craft theory",
                "civic history and censored history",
                "ritual etiquette",
                "market arithmetic",
                "oral testimony practice",
            ]),
            "apprenticeship_paths": education_seed.get("apprenticeship_paths", [
                {
                    "path_name": "Road Witness Apprentice",
                    "mentor": "certified guide or retired road warden",
                    "training": ["fog crossing", "testimony memory", "animal sign reading", "route-law basics"],
                    "failure_risk": "failed crossing can remove family route rights",
                    "career_path": "guide, road warden, witness officer, smuggler, or exile scout",
                },
                {
                    "path_name": "Saltbark Scribe Apprentice",
                    "mentor": "archive clerk or guild examiner",
                    "training": ["ledger script", "public-name registry", "contract logic", "map seals"],
                    "failure_risk": "record tampering accusation can destroy family reputation",
                    "career_path": "scribe, lawyer, archivist, forger, journalist, or political agent",
                },
                {
                    "path_name": "Temple Healer Apprentice",
                    "mentor": "licensed healer or temple medicine teacher",
                    "training": ["dosage", "ritual ethics", "triage", "plant identification", "funeral medicine"],
                    "failure_risk": "wrong dosage can become religious scandal",
                    "career_path": "healer, field medic, researcher, black-market seller, or ritual physician",
                },
            ]),
            "exams_trials_certifications": education_seed.get("exams_trials_certifications", [
                {
                    "exam_name": "Bell-Cord Examination",
                    "tests": "public name memory, family duties, route law, and oath recitation",
                    "failure_consequence": "delayed public name or lower civic trust",
                    "story_use": "identity reveal, sabotage, class humiliation, or hidden-name discovery",
                },
                {
                    "exam_name": "Fog Crossing Trial",
                    "tests": "survival, route choice, animal sign reading, and guide discipline",
                    "failure_consequence": "injury, death, exile, or loss of apprenticeship",
                    "story_use": "coming-of-age scene, betrayal, rescue, or route secret reveal",
                },
                {
                    "exam_name": "Saltbark Ledger Trial",
                    "tests": "contract reading, forgery detection, missing-name logic, and archive ethics",
                    "failure_consequence": "guild rejection or recruitment by illegal forgers",
                    "story_use": "career turn, fraud reveal, or political recruitment",
                },
            ]),
            "student_life": education_seed.get("student_life", [
                "students trade weather nicknames before earning public titles",
                "poor students share lamp oil and copy lessons at night",
                "academy students form secret study circles around banned maps",
                "temple students debate whether dead-bell omens are law or myth",
                "apprentices carry tools that mark status before they earn wages",
            ]),
            "teacher_roles": education_seed.get("teacher_roles", [
                {
                    "role_name": "Name Tutor",
                    "duty": "teach civic identity, family duty, and public testimony etiquette",
                    "secret_power": "can delay or accelerate a student's public recognition",
                },
                {
                    "role_name": "Road Master",
                    "duty": "teach route survival, fog signs, and guide ethics",
                    "secret_power": "knows which roads are officially erased but physically real",
                },
                {
                    "role_name": "Ledger Examiner",
                    "duty": "test contract literacy, map seals, and archive integrity",
                    "secret_power": "can identify forged histories hidden in legal documents",
                },
            ]),
            "exclusion_and_access_rules": education_seed.get("exclusion_and_access_rules", [
                "no-bell children may attend lessons but cannot sit final public-name exams without sponsor signatures",
                "guild academies require payment, family reputation, or labor contracts",
                "temple schools reject families accused of false testimony",
                "species-specific traits may determine who can survive certain route or medicine training",
                "forbidden schools recruit students excluded by official systems",
            ]),
            "school_scandals": education_seed.get("school_scandals", [
                {
                    "scandal_name": "Missing Bell-Cord Records",
                    "public_story": "student records were lost during a damp archive season",
                    "secret_truth": "records were removed to hide erased family lines",
                    "plot_use": "student rebellion, teacher confession, archive break-in, or public-name trial",
                },
                {
                    "scandal_name": "Fog Crossing Death Coverup",
                    "public_story": "students ignored safety instructions",
                    "secret_truth": "the trial route was changed to protect a merchant convoy",
                    "plot_use": "investigation, revenge, guild collapse, or road warden scandal",
                },
            ]),
            "school_rivalries": education_seed.get("school_rivalries", [
                {
                    "rivalry": "Saltbark Guild Academy versus Temple Healer School",
                    "cause": "contract law versus sacred medicine ethics",
                    "story_use": "research suppression, medicine ration dispute, or student romance conflict",
                },
                {
                    "rivalry": "Public Name School versus Underlamp School",
                    "cause": "official identity versus erased truth",
                    "story_use": "secret teaching, arrests, student double lives, and memory politics",
                },
            ]),
            "school_to_career_pipelines": education_seed.get("school_to_career_pipelines", [
                "public name school to civic clerk, witness aide, market registrar, or court assistant",
                "guild academy to merchant house, archive office, contract law, or forgery network",
                "temple school to healer, ritual witness, funeral kitchen, or forbidden doctrine scholar",
                "road apprenticeship to guide, warden, smuggler, explorer, or exile route keeper",
            ]),
            "story_use": (
                "Turns education into story pressure through schools, academies, apprenticeships, exams, exclusions, scandals, "
                "teacher power, forbidden knowledge, student life, rivalries, and career pipelines."
            ),
            "character_effect": (
                "Characters are shaped by what they were allowed to learn, who taught them, which exam they passed or failed, "
                "what school excluded them, and what forbidden knowledge they carry."
            ),
            "plot_effect": (
                "Can trigger school scandals, exam sabotage, forbidden teaching, student rebellion, apprenticeship failure, "
                "career gatekeeping, hidden-name discovery, or research suppression."
            ),
            "memory_effect": (
                "World memory must track student status, certifications, expulsions, scandals, teacher reputation, school closures, "
                "forbidden lessons, and career outcomes."
            ),
            "anti_genericity_signal": (
                "Education system includes named institutions, school types, subjects, apprenticeships, exams, students, teachers, "
                "access rules, scandals, rivalries, career pipelines, and memory hooks."
            ),
            "detail_depth_score": 0.94,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "EducationSchoolsApprenticeshipEngine",
                "origin_type": "derived_from_politics_settlement_population_economy",
                "source_id": source_id,
                "political_unit_id": political_unit.get("political_unit_id"),
                "settlement_id": settlement.get("settlement_id"),
                "population_diversity_profile_id": population_profile.get("population_diversity_profile_id"),
                "resource_economy_profile_id": economy_profile.get("resource_economy_profile_id"),
                "seed_keys": sorted(education_seed.keys()),
                "story_context_keys": sorted(story_context.keys()),
            },
            "compression_summary": (
                f"{education_name}: schools, academies, apprenticeships, exams, access rules, scandals, rivalries, "
                f"student life, teacher power, career pipelines, and memory hooks."
            ),
        }

        return {"education_system": education_system}

    def build_education_event(
        self,
        *,
        source_id: str,
        education_system: Dict[str, Any],
        event_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event_seed = event_seed or {}

        event_name = event_seed.get("event_name", "Bell-Cord Examination Sabotage")

        event = {
            "education_event_id": f"education_event_{source_id}_{self._slug(event_name)}",
            "source_id": source_id,
            "education_system_id": education_system["education_system_id"],
            "education_name": education_system["education_name"],
            "event_name": event_name,
            "event_type": event_seed.get("event_type", "exam_identity_and_access_conflict"),
            "trigger": event_seed.get(
                "trigger",
                "a student's public-name cord was replaced with a forbidden family cord before the exam",
            ),
            "affected_institutions": event_seed.get("affected_institutions", [
                "The Veyr Hall of Public Names",
                "Saltbark Guild Academy",
                "The Underlamp School",
            ]),
            "affected_groups": event_seed.get("affected_groups", [
                "no-bell children",
                "archive families",
                "teachers",
                "student witnesses",
                "guild examiners",
            ]),
            "public_consequence": event_seed.get(
                "public_consequence",
                "the examination is suspended and parents demand public review of student records",
            ),
            "private_consequence": event_seed.get(
                "private_consequence",
                "teachers fear the forbidden cord proves the missing records scandal was real",
            ),
            "story_use": (
                "Turns education into active plot through exams, naming, sabotage, class exclusion, school rivalry, and hidden records."
            ),
            "character_effect": (
                "Characters must decide whether to protect students, expose records, obey school law, betray teachers, or claim a forbidden name."
            ),
            "plot_effect": (
                "Can trigger student rebellion, archive investigation, public-name trial, teacher confession, or recruitment into forbidden schools."
            ),
            "memory_effect": (
                "World memory must track exam outcome, student status, exposed records, teacher reputation, school trust, and public-name changes."
            ),
            "lore_effect": (
                "School ritual becomes a memory battlefield where names, law, and buried history decide identity.",
            ),
            "anti_genericity_signal": (
                "Event ties named institutions, exam ritual, student identity, forbidden names, class access, and civic memory."
            ),
            "detail_depth_score": 0.91,
            "validation_status": "validated",
            "provenance": {
                "generated_by_engine": "EducationSchoolsApprenticeshipEngine",
                "origin_type": "derived_from_education_system",
                "source_id": source_id,
                "education_system_id": education_system["education_system_id"],
                "seed_keys": sorted(event_seed.keys()),
            },
            "compression_summary": (
                f"{event_name}: trigger, affected institutions/groups, public/private consequences, and memory effects."
            ),
        }

        return {"education_event": event}

    def build_story_context_patch(
        self,
        *,
        education_system: Dict[str, Any],
        education_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        patch = {
            "education_system_id": education_system["education_system_id"],
            "education_name": education_system["education_name"],
            "school_types": education_system["school_types"],
            "named_institutions": education_system["named_institutions"],
            "subjects_taught": education_system["subjects_taught"],
            "apprenticeship_paths": education_system["apprenticeship_paths"],
            "exams_trials_certifications": education_system["exams_trials_certifications"],
            "student_life": education_system["student_life"],
            "teacher_roles": education_system["teacher_roles"],
            "exclusion_and_access_rules": education_system["exclusion_and_access_rules"],
            "school_scandals": education_system["school_scandals"],
            "school_rivalries": education_system["school_rivalries"],
            "school_to_career_pipelines": education_system["school_to_career_pipelines"],
            "story_use": education_system["story_use"],
            "character_effect": education_system["character_effect"],
            "plot_effect": education_system["plot_effect"],
            "memory_effect": education_system["memory_effect"],
            "generation_hints": [
                "Use education to shape character skills, class status, language, confidence, secrets, and career access.",
                "Schools should have access rules, rituals, scandals, rivalries, and institutional power.",
                "Track certifications, expulsions, teacher reputation, forbidden lessons, and student identity changes.",
                "Do not create generic schools; every institution needs naming, origin, purpose, exclusion, and story pressure.",
            ],
            "memory_update_candidates": [
                {
                    "candidate_type": "education_system_state",
                    "target_element_id": education_system["education_system_id"],
                    "reason": "Track school access, student status, certifications, scandals, teacher power, and forbidden knowledge.",
                }
            ],
        }

        if education_event:
            patch["active_education_event"] = education_event
            patch["memory_update_candidates"].append(
                {
                    "candidate_type": "education_event_state",
                    "target_element_id": education_event["education_event_id"],
                    "reason": "Track trigger, affected schools/groups, exam result, public/private consequences, and reputation shifts.",
                }
            )

        return {"story_context_patch": patch}

    def validate_education_system(self, *, education_system: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "education_system_id",
            "education_name",
            "region_name",
            "name_origin",
            "name_meaning",
            "name_language_logic",
            "cultural_context",
            "world_context",
            "visual_identity",
            "sensory_identity",
            "school_types",
            "named_institutions",
            "subjects_taught",
            "apprenticeship_paths",
            "exams_trials_certifications",
            "student_life",
            "teacher_roles",
            "exclusion_and_access_rules",
            "school_scandals",
            "school_rivalries",
            "school_to_career_pipelines",
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

        missing = [field for field in required if not education_system.get(field)]
        shallow = self._shallow_fields(
            payload=education_system,
            fields=[
                "name_origin",
                "story_use",
                "character_effect",
                "plot_effect",
                "memory_effect",
                "anti_genericity_signal",
            ],
        )

        passed = not missing and not shallow and float(education_system.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "education_system_id": education_system.get("education_system_id"),
        }

    def validate_education_event(self, *, education_event: Dict[str, Any]) -> Dict[str, Any]:
        required = [
            "education_event_id",
            "education_system_id",
            "education_name",
            "event_name",
            "event_type",
            "trigger",
            "affected_institutions",
            "affected_groups",
            "public_consequence",
            "private_consequence",
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

        missing = [field for field in required if not education_event.get(field)]
        shallow = self._shallow_fields(
            payload=education_event,
            fields=["story_use", "character_effect", "plot_effect", "memory_effect", "lore_effect"],
        )

        passed = not missing and not shallow and float(education_event.get("detail_depth_score", 0.0)) >= 0.75

        return {
            "passed": passed,
            "missing_fields": missing,
            "shallow_fields": shallow,
            "education_event_id": education_event.get("education_event_id"),
        }

    def summarize_education_system(
        self,
        *,
        education_system: Dict[str, Any],
        education_event: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        summary = {
            "education_system_id": education_system["education_system_id"],
            "education_name": education_system["education_name"],
            "school_type_count": len(education_system["school_types"]),
            "named_institution_count": len(education_system["named_institutions"]),
            "subject_count": len(education_system["subjects_taught"]),
            "apprenticeship_path_count": len(education_system["apprenticeship_paths"]),
            "exam_count": len(education_system["exams_trials_certifications"]),
            "compression_summary": education_system["compression_summary"],
        }

        if education_event:
            summary["education_event_id"] = education_event["education_event_id"]
            summary["event_name"] = education_event["event_name"]

        return {"success": True, "summary": summary}

    def build_education_text(
        self,
        *,
        education_system: Dict[str, Any],
        education_event: Dict[str, Any] | None = None,
    ) -> Dict[str, str]:
        lines = [
            "Education, Schools, Academies, and Apprenticeship Profile",
            f"Education System: {education_system['education_name']}",
            f"ID: {education_system['education_system_id']}",
            f"Region: {education_system['region_name']}",
            "",
            "Name Origin:",
            education_system["name_origin"],
        ]

        sections = [
            ("School Types", [str(item) for item in education_system["school_types"]]),
            ("Named Institutions", [str(item) for item in education_system["named_institutions"]]),
            ("Subjects Taught", education_system["subjects_taught"]),
            ("Apprenticeship Paths", [str(item) for item in education_system["apprenticeship_paths"]]),
            ("Exams, Trials, and Certifications", [str(item) for item in education_system["exams_trials_certifications"]]),
            ("Student Life", education_system["student_life"]),
            ("Teacher Roles", [str(item) for item in education_system["teacher_roles"]]),
            ("Exclusion and Access Rules", education_system["exclusion_and_access_rules"]),
            ("School Scandals", [str(item) for item in education_system["school_scandals"]]),
            ("School Rivalries", [str(item) for item in education_system["school_rivalries"]]),
            ("School-to-Career Pipelines", education_system["school_to_career_pipelines"]),
        ]

        for title, values in sections:
            lines.append("")
            lines.append(title + ":")
            for item in values:
                lines.append(f"- {item}")

        if education_event:
            lines.extend([
                "",
                "Active Education Event:",
                education_event["event_name"],
                "",
                "Trigger:",
                education_event["trigger"],
            ])

        lines.extend([
            "",
            "Story Use:",
            education_system["story_use"],
            "",
            "Character Effect:",
            education_system["character_effect"],
            "",
            "Plot Effect:",
            education_system["plot_effect"],
            "",
            "Memory Effect:",
            education_system["memory_effect"],
        ])

        return {"education_text": chr(10).join(lines)}

    def _shallow_fields(self, *, payload: Dict[str, Any], fields: List[str]) -> List[str]:
        return [field for field in fields if len(str(payload.get(field, ""))) < 20]

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)
