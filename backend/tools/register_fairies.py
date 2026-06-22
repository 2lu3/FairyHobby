import glob
import logging
import os

from sqlmodel import Session

from backend.database import engine
from backend.fairies.service import create, delete, generate_embeddings, get_all
from backend.fairies.models import Fairy  # noqa: F401
from backend.activities.models import Activity, ActivityImage  # noqa: F401
from backend.activity_reviews.models import ActivityReview  # noqa: F401
from backend.stores.models import Store  # noqa: F401
from backend.users.models import User  # noqa: F401
from backend.recommendation_job.models import RecommendationJob  # noqa: F401
from backend.storage import init_storage_client

logger = logging.getLogger(__name__)


fairy_personalities = {
    "careful": """
慎重で計画的な妖精。
新しいことを始める前によく調べる。
無理をせず着実に成長することを大切にしている。
安定して続けられる趣味に魅力を感じる。
""",
    "cozy": """
心地よさを何より大切にする妖精。
忙しさよりも穏やかな時間を好む。
日常の小さな幸せを見つけるのが得意。
リラックスできる趣味に惹かれる。
""",
    "gentle": """
優しく穏やかな妖精。
争いや競争を好まない。
自然や静かな空間に安心感を覚える。
心が落ち着く体験を大切にする。
""",
    "kind": """
誰かを喜ばせることが好きな妖精。
人とのつながりを大切にしている。
困っている人を見ると手を差し伸べたくなる。
誰かの役に立てる活動にやりがいを感じる。
""",
    "nostalgic": """
昔からあるものを愛する妖精。
歴史や思い出のあるものに強く惹かれる。
流行よりも長く受け継がれてきた価値を大切にする。
懐かしさを感じる体験を好む。
""",
    "passionate": """
情熱的な妖精。
興味を持ったことには全力で取り組む。
難しい挑戦にも積極的に飛び込む。
成長や達成感を強く求めている。
""",
    "reflective": """
考えることが好きな妖精。
物事の意味や背景を知りたがる。
経験したことを振り返り、自分なりの解釈を楽しむ。
知識や洞察を深められる活動を好む。
""",
    "sentimental": """
感受性豊かな妖精。
景色や音楽、人との思い出に深く心を動かされる。
結果よりも感情の豊かさを大切にする。
物語や表現に触れられる活動を好む。
""",
    "shy": """
控えめな妖精。
初めての場所や大勢の集まりは少し苦手。
安心できる環境では自分らしさを発揮できる。
一人または少人数で楽しめる活動を好む。
""",
    "warm_hearted": """
明るく親しみやすい妖精。
人と一緒に過ごす時間が好き。
周囲を元気づけたり盛り上げたりするのが得意。
楽しさを共有できる活動に魅力を感じる。
""",
}


fairy_names = {
    "careful": "ミルフィ",
    "cozy": "ココリ",
    "gentle": "リュミナ",
    "kind": "メルシア",
    "nostalgic": "ノエル",
    "passionate": "ルビエル",
    "reflective": "シエラ",
    "sentimental": "セレフィ",
    "shy": "ミュリエ",
    "warm_hearted": "レーナ",
}


def glob_fairy_images():
    files = glob.glob("data/fairies/*.png")
    return list(files)


def main():
    init_storage_client()

    with Session(engine) as db_session:
        faries = get_all(db_session)
        for fairy in faries:
            delete(fairy.id, db_session)
            logger.info(f"Deleted fairy: {fairy.id}")

        for name, prompt in fairy_personalities.items():
            image_path = f"tools/data/fairies/output_{name} fairy.png"
            if not os.path.exists(image_path):
                logger.warning(f"Image not found: {image_path}")
                continue

            image_bytes = open(image_path, "rb").read()
            image_content_type = "image/png"

            fairy = create(
                fairy_names[name], prompt, image_bytes, image_content_type, db_session
            )
            logger.info(f"Created fairy: {fairy.id}")

            generate_embeddings(fairy.id)
            logger.info(f"Generated embeddings for fairy: {fairy.id}")


if __name__ == "__main__":
    main()
