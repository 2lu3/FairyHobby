import json
from uuid import UUID

from openai import OpenAI
from sqlmodel import Session

from backend.activities.models import Activity
from backend.config import settings
from backend.database import engine
from backend.exceptions import NotFoundError, PermissionDeniedError
from backend.fairies.models import Fairy
from backend.plans.models import Plan, PlanItem
from backend.recommendation_job.models import RecommendationJob, RecommendationStatus
from backend.recommendation_job.schemas import RecommendationJobCreateRequest
from backend.recommendation_job.worker import Optimizer
from backend.users.models import User


def create_job(
    in_recommendation_job: RecommendationJobCreateRequest,
    current_user: User,
    db_session: Session,
) -> RecommendationJob:
    recommendation_job = RecommendationJob(
        fairy_id=in_recommendation_job.fairy_id,
        user_id=current_user.id,
        date=in_recommendation_job.date,
        budget=in_recommendation_job.budget,
    )
    db_session.add(recommendation_job)
    db_session.commit()
    db_session.refresh(recommendation_job)

    return recommendation_job


def get_job_for_user(
    job_id: UUID, current_user: User, db_session: Session
) -> RecommendationJob:
    recommendation_job = db_session.get(RecommendationJob, job_id)
    if not recommendation_job:
        raise NotFoundError()
    if current_user.id != recommendation_job.user_id:
        raise PermissionDeniedError()
    return recommendation_job


def get_job(job_id: UUID, db_session: Session) -> RecommendationJob:
    recommendation_job = db_session.get(RecommendationJob, job_id)
    if not recommendation_job:
        raise NotFoundError()
    return recommendation_job


def _generate_plan_name_and_description(
    activities: list[Activity],
    fairy: Fairy | None,
) -> tuple[str, str]:
    """選ばれたアクティビティから LLM でプラン名と説明文を生成する。"""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    activity_lines = "\n".join(
        f"- {activity.name}: {activity.description}" for activity in activities
    )
    fairy_name = fairy.name if fairy else "妖精"

    response = client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたは1日の体験プランを提案する妖精です。"
                    "与えられた体験リストをもとに、魅力的なプランの名前と説明文を考えてください。"
                    '出力は {"name": ..., "description": ...} の JSON 形式で返してください。'
                    "name は20文字以内のキャッチーな日本語、description は100文字程度の日本語にしてください。"
                ),
            },
            {
                "role": "user",
                "content": f"妖精の名前: {fairy_name}\n体験リスト:\n{activity_lines}",
            },
        ],
    )

    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    name = data.get("name") or "妖精が選んだプラン"
    description = data.get("description") or "妖精が選んだプランです"
    return name, description


def _create_plan_from_result(
    activities: list[Activity],
    db_session: Session,
    fairy: Fairy | None = None,
) -> UUID:
    name, description = _generate_plan_name_and_description(activities, fairy)
    plan = Plan(
        name=name,
        description=description,
    )
    for position, activity in enumerate(activities):
        plan.items.append(
            PlanItem(
                position=position,
                activity_id=activity.id,
            )
        )
    db_session.add(plan)
    db_session.flush()
    return plan.id


def generate_recommendation(job_id: UUID) -> None:
    # 重い最適化計算 (Optimizer.build_model / run) の間は DB コネクションを
    # 握り続けず、DB アクセスが必要な箇所だけ短命のセッションを開く。
    # モデル構築のためのデータ取得は Optimizer が自前のセッションで行う。
    with Session(engine) as db_session:
        recommendation_job = _start_calculation(job_id, db_session)

    if recommendation_job is None:
        return

    optimizer = Optimizer(recommendation_job)
    try:
        optimizer.build_model()
        activities = optimizer.run()
    except Exception:
        with Session(engine) as db_session:
            _mark_failed(job_id, db_session)
        raise

    with Session(engine) as db_session:
        _save_result(job_id, activities, db_session)


def _start_calculation(job_id: UUID, db_session: Session) -> RecommendationJob | None:
    """ステータスを CALCULATING に更新する。

    再計算対象でない (PENDING 以外の) 場合は何もせず None を返す。
    """
    recommendation_job = get_job(job_id, db_session)
    if recommendation_job.status != RecommendationStatus.PENDING:
        return None

    recommendation_job.status = RecommendationStatus.CALCULATING
    db_session.commit()
    # セッションを閉じた後も Optimizer が job の属性を読めるようにロードし直す。
    db_session.refresh(recommendation_job)

    return recommendation_job


def _save_result(job_id: UUID, activities: list[Activity], db_session: Session) -> None:
    """最適化結果をプランとして保存し、ステータスを確定する。"""
    recommendation_job = get_job(job_id, db_session)
    if activities:
        fairy = db_session.get(Fairy, recommendation_job.fairy_id)
        recommendation_job.plan_id = _create_plan_from_result(
            activities, db_session, fairy
        )
        recommendation_job.status = RecommendationStatus.COMPLETED
    else:
        recommendation_job.status = RecommendationStatus.FAILED
    db_session.commit()


def _mark_failed(job_id: UUID, db_session: Session) -> None:
    """ジョブを FAILED に更新する。"""
    recommendation_job = get_job(job_id, db_session)
    recommendation_job.status = RecommendationStatus.FAILED
    db_session.commit()
