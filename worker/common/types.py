from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Engine(str, Enum):
    GOOGLE = "google"
    YANDEX = "yandex"


@dataclass
class Issue:
    code: str
    title: str
    description: str
    severity: Severity
    source_module: str
    fix_snippet: Optional[str] = None
    cms_hint: Optional[str] = None
    meta: dict = field(default_factory=dict)


@dataclass
class WeightedIssue:
    issue: Issue
    engine: Engine
    weight: float
    effort: float
    impact_effort_ratio: float = field(init=False)

    def __post_init__(self):
        self.impact_effort_ratio = self.weight / self.effort if self.effort else self.weight
