from sqlmodel import Session
from backend.recommendation_job.models import RecommendationJob
from backend.activities.models import Activity
import numpy as np
from ortools.sat.python import cp_model
import itertools
import geopy.distance
from ortools.sat.python import cp_solver


class RecommendationJobWorker:
    def __init__(self, job: RecommendationJob, db_session: Session):
        self.job: RecommendationJob = job
        self.db_session: Session = db_session

        self.model = cp_model.CpModel()

    def build_model(self):
        self.activities = self.db_session.query(Activity).all()
        self.num_days = (self.job.end_date - self.job.start_date).days + 1

        # 変数の定義
        self.x = {}
        for day in range(self.num_days):
            for activity in self.activities:
                self.x[day, activity] = self.model.NewBoolVar(f"x_{day}_{activity}")

        # 制約の定義

        # 1. activityのpriceの合計がbudget以下
        self.model.Add(
            sum(
                self.x[day, activity] * activity.price
                for day in range(self.num_days)
                for activity in self.activities
            )
            <= self.job.budget
        )

        for day_idx in range(self.num_days):
            # 2. 1日6時間以内
            self.model.Add(
                sum(
                    self.x[day_idx, activity] * activity.duration_minutes
                    for activity in self.activities
                )
                <= 6 * 60
            )
            # 3. 3箇所まで行ける
            self.model.Add(
                sum(self.x[day_idx, activity] for activity in self.activities) <= 3
            )

        # 4. 同じactivityは全体で1回まで
        for activity in self.activities:
            self.model.Add(
                sum(self.x[day_idx, activity] for day_idx in range(self.num_days)) <= 1
            )

        # 5. activity1とactivity2の直線距離が5km以内
        for activity1, activity2 in itertools.combinations(self.activities, 2):
            distance = self.calc_distance(
                activity1.latitude,
                activity1.longitude,
                activity2.latitude,
                activity2.longitude,
            )
            if distance > 5:
                self.model.Add(
                    sum(self.x[day_idx, activity1] for day_idx in range(self.num_days))
                    + sum(
                        self.x[day_idx, activity2] for day_idx in range(self.num_days)
                    )
                    <= 1
                )

        # 目的関数
        # similarityの合計が最大になるように
        self.model.Maximize(
            sum(
                self.x[day_idx, activity]
                * self.cosine_similarity(self.job.fairy.embeddings, activity.embeddings)
                for day_idx in range(self.num_days)
                for activity in self.activities
            )
        )

    def run(self):
        solver = cp_solver.CpSolver()
        status = solver.Solve(self.model)
        if status != cp_solver.OPTIMAL:
            raise Exception("Failed to solve the model")

        result = {day: [] for day in range(self.num_days)}
        for day in range(self.num_days):
            for activity in self.activities:
                if solver.Value(self.x[day, activity]) == 1:
                    result[day].append(activity)
        return result

    def search_similarity_by_embeddings(self, activities: list[Activity]):
        fairy_embedding = self.job.fairy.embeddings

        similarities = []
        for activity in activities:
            activity_embedding = activity.embeddings
            similarity = self.cosine_similarity(fairy_embedding, activity_embedding)
            similarities.append((activity, similarity))

        return similarities

    def cosine_similarity(self, a: list[float], b: list[float]):
        a_np = np.array(a)
        b_np = np.array(b)
        return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))

    def calc_distance(
        self, latitude1: float, longitude1: float, latitude2: float, longitude2: float
    ):
        return geopy.distance.distance(latitude1, longitude1, latitude2, longitude2).km
