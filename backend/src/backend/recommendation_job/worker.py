import itertools
from uuid import UUID

import geopy.distance
import numpy as np
from ortools.sat.python import cp_model
from sqlmodel import Session, select

from backend.activities.models import Activity
from backend.fairies.models import Fairy
from backend.recommendation_job.models import RecommendationJob


class Optimizer:
    def __init__(self, job: RecommendationJob, db_session: Session):
        self.job: RecommendationJob = job
        self.db_session: Session = db_session
        self.fairy: Fairy | None = None
        self.activities: list[Activity] = []
        self.model = cp_model.CpModel()
        self.x: dict[UUID, cp_model.IntVar] = {}

    def build_model(self) -> None:
        self.fairy = self.db_session.get(Fairy, self.job.fairy_id)
        if not self.fairy:
            raise ValueError("Fairy not found")

        self.activities = list(self.db_session.exec(select(Activity)).all())

        for activity in self.activities:
            self.x[activity.id] = self.model.NewBoolVar(f"x_{activity.id}")

        self.model.Add(
            sum(self.x[activity.id] * activity.price for activity in self.activities)
            <= self.job.budget
        )

        self.model.Add(
            sum(
                self.x[activity.id] * activity.duration_minutes
                for activity in self.activities
            )
            <= 6 * 60
        )
        self.model.Add(sum(self.x[activity.id] for activity in self.activities) <= 3)

        for activity1, activity2 in itertools.combinations(self.activities, 2):
            if (
                activity1.latitude is None
                or activity1.longitude is None
                or activity2.latitude is None
                or activity2.longitude is None
            ):
                continue
            distance = self.calc_distance(
                activity1.latitude,
                activity1.longitude,
                activity2.latitude,
                activity2.longitude,
            )
            if distance > 5:
                self.model.Add(self.x[activity1.id] + self.x[activity2.id] <= 1)

        self.model.Maximize(
            sum(
                self.x[activity.id]
                * self.cosine_similarity(self.fairy.embeddings, activity.embeddings)
                for activity in self.activities
            )
        )

    def run(self) -> list[Activity]:
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            raise RuntimeError("Failed to solve the model")

        return [
            activity
            for activity in self.activities
            if solver.Value(self.x[activity.id]) == 1
        ]

    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        a_np = np.array(a)
        b_np = np.array(b)
        norm_a = np.linalg.norm(a_np)
        norm_b = np.linalg.norm(b_np)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a_np, b_np) / (norm_a * norm_b))

    def calc_distance(
        self, latitude1: float, longitude1: float, latitude2: float, longitude2: float
    ) -> float:
        return geopy.distance.distance(
            (latitude1, longitude1), (latitude2, longitude2)
        ).km
