"""Data models used across the Smart Task Platform."""

from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    email: str


@dataclass
class Task:
    id: int
    user_id: int
    title: str
    description: str | None = None
    status: str = "open"
    priority: str = "medium"


@dataclass
class BacklogItem:
    id: int
    title: str
    impact: int
    effort: int
    status: str = "planned"

    def priority_score(self):
        if self.effort == 0:
            return self.impact

        return round(self.impact / self.effort, 2)