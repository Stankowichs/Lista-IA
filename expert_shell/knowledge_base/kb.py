"""
Módulo da Base de Conhecimento.
Define Condition, Rule e KnowledgeBase com persistência JSON.
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Condition:
    attribute: str
    value: Any

    def matches(self, facts: dict) -> bool:
        return facts.get(self.attribute) == self.value

    def to_dict(self) -> dict:
        return {"attribute": self.attribute, "value": self.value}

    @classmethod
    def from_dict(cls, d: dict) -> "Condition":
        return cls(attribute=d["attribute"], value=d["value"])

    def __str__(self) -> str:
        return f"{self.attribute} = {self.value}"


@dataclass
class Rule:
    id: str
    name: str
    conditions: list[Condition]
    conclusion: Condition
    description: str = ""

    def can_fire(self, facts: dict) -> bool:
        return all(c.matches(facts) for c in self.conditions)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "conditions": [c.to_dict() for c in self.conditions],
            "conclusion": self.conclusion.to_dict(),
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Rule":
        return cls(
            id=d["id"],
            name=d["name"],
            conditions=[Condition.from_dict(c) for c in d["conditions"]],
            conclusion=Condition.from_dict(d["conclusion"]),
            description=d.get("description", ""),
        )

    def __str__(self) -> str:
        conds = " E ".join(str(c) for c in self.conditions)
        return f"[{self.id}] SE {conds} ENTÃO {self.conclusion}"


class KnowledgeBase:
    def __init__(self) -> None:
        self.facts: dict[str, Any] = {}
        self.initial_facts: dict[str, Any] = {}
        self.inferred_facts: dict[str, Any] = {}
        self.rules: list[Rule] = []
        self.hypotheses: list[str] = []
        self.possible_values: dict[str, list] = {}
        self.domain_name: str = ""
        self.domain_description: str = ""

    # ── Facts ──────────────────────────────────────────────────────────────

    def add_fact(self, attribute: str, value: Any, inferred: bool = False) -> None:
        self.facts[attribute] = value
        if inferred:
            self.inferred_facts[attribute] = value
        else:
            self.initial_facts[attribute] = value

    def remove_fact(self, attribute: str) -> bool:
        if attribute not in self.facts:
            return False
        del self.facts[attribute]
        self.initial_facts.pop(attribute, None)
        self.inferred_facts.pop(attribute, None)
        return True

    def get_fact(self, attribute: str) -> Any:
        return self.facts.get(attribute)

    def reset_session(self) -> None:
        """Limpa todos os fatos para uma nova consulta."""
        self.facts.clear()
        self.initial_facts.clear()
        self.inferred_facts.clear()

    # ── Rules ──────────────────────────────────────────────────────────────

    def add_rule(self, rule: Rule) -> None:
        existing_ids = {r.id for r in self.rules}
        if rule.id in existing_ids:
            raise ValueError(f"Regra com ID '{rule.id}' já existe.")
        self.rules.append(rule)

    def remove_rule(self, rule_id: str) -> bool:
        before = len(self.rules)
        self.rules = [r for r in self.rules if r.id != rule_id]
        return len(self.rules) < before

    def update_rule(self, rule_id: str, new_rule: Rule) -> bool:
        for i, r in enumerate(self.rules):
            if r.id == rule_id:
                new_rule.id = rule_id
                self.rules[i] = new_rule
                return True
        return False

    def get_rule(self, rule_id: str) -> Rule | None:
        for r in self.rules:
            if r.id == rule_id:
                return r
        return None

    def rules_that_conclude(self, attribute: str, value: Any = None) -> list[Rule]:
        """Regras cuja conclusão é attribute=value (ou qualquer valor se value=None)."""
        result = []
        for r in self.rules:
            if r.conclusion.attribute == attribute:
                if value is None or r.conclusion.value == value:
                    result.append(r)
        return result

    def rules_that_need(self, attribute: str) -> list[Rule]:
        """Regras que têm attribute como condição."""
        return [r for r in self.rules if any(c.attribute == attribute for c in r.conditions)]

    # ── Persistence ────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "domain_name": self.domain_name,
            "domain_description": self.domain_description,
            "hypotheses": self.hypotheses,
            "possible_values": self.possible_values,
            "rules": [r.to_dict() for r in self.rules],
            "initial_facts": self.initial_facts,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "KnowledgeBase":
        kb = cls()
        kb.domain_name = d.get("domain_name", "")
        kb.domain_description = d.get("domain_description", "")
        kb.hypotheses = d.get("hypotheses", [])
        kb.possible_values = d.get("possible_values", {})
        kb.rules = [Rule.from_dict(r) for r in d.get("rules", [])]
        for attr, val in d.get("initial_facts", {}).items():
            kb.add_fact(attr, val, inferred=False)
        return kb

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "KnowledgeBase":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
