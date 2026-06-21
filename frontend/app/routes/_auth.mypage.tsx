import { Link } from "react-router";
import type { Route } from "./+types/_auth.mypage";
import Container from "~/component/Container";
import { backendFetch } from "~/lib/fetcher.server";

type PlanHistory = {
    id: string;
    user_id: string;
    plan_id: string;
    created_at: string;
};

type PlanItem = {
    activity_id: string;
};

type Plan = {
    id: string;
    name: string;
    description: string;
    details: PlanItem[];
};

type Activity = {
    id: string;
    name: string;
};

type PlanHistoryView = {
    id: string;
    createdAt: string;
    plan: Plan;
    activityTitles: string[];
};

export async function loader({ request }: Route.LoaderArgs) {
    const res = await backendFetch(request, "/plan-histories");
    if (!res.ok) {
        return {
            histories: [] as PlanHistoryView[],
            errorMessage: "プラン履歴の取得に失敗しました",
        };
    }
    const planHistories = (await res.json()) as PlanHistory[];

    const historyResults = await Promise.all(
        planHistories.map(async (history) => {
            const planRes = await backendFetch(
                request,
                `/plans/${history.plan_id}`,
            );
            if (!planRes.ok) {
                return null;
            }
            const plan = (await planRes.json()) as Plan;

            const activityResults = await Promise.all(
                plan.details.map(async (item) => {
                    const activityRes = await backendFetch(
                        request,
                        `/activities/${item.activity_id}`,
                    );
                    if (!activityRes.ok) {
                        return null;
                    }
                    return (await activityRes.json()) as Activity;
                }),
            );
            const activityTitles = activityResults
                .filter((activity): activity is Activity => activity !== null)
                .map((activity) => activity.name);

            return {
                id: history.id,
                createdAt: history.created_at,
                plan,
                activityTitles,
            } satisfies PlanHistoryView;
        }),
    );

    const histories = historyResults.filter(
        (history): history is PlanHistoryView => history !== null,
    );

    return { histories, errorMessage: null };
}

function formatDate(value: string): string {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return value;
    }
    return date.toLocaleDateString("ja-JP", {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
}

export default function MyPage({ loaderData }: Route.ComponentProps) {
    const { histories, errorMessage } = loaderData;

    return (
        <Container className="min-h-screen">
            <section className="mt-24">
                <h1 className="text-2xl font-bold">マイページ</h1>
                <p className="mt-1 text-base-content/70">
                    これまでに体験したプランの一覧です
                </p>

                {errorMessage && (
                    <p className="mt-4 text-error">{errorMessage}</p>
                )}

                {!errorMessage && histories.length === 0 && (
                    <p className="mt-8 text-base-content/60">
                        まだ体験したプランがありません
                    </p>
                )}

                <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
                    {histories.map((history) => (
                        <div
                            key={history.id}
                            className="card bg-base-100 shadow-md"
                        >
                            <div className="card-body">
                                <span className="text-sm text-base-content/60">
                                    {formatDate(history.createdAt)}
                                </span>
                                <h2 className="card-title">{history.plan.name}</h2>
                                {history.plan.description && (
                                    <p className="text-base-content/80">
                                        {history.plan.description}
                                    </p>
                                )}

                                {history.activityTitles.length > 0 && (
                                    <ul className="mt-2 flex flex-col gap-1">
                                        {history.activityTitles.map(
                                            (title, index) => (
                                                <li
                                                    key={`${history.id}-${index}`}
                                                    className="flex items-center gap-2"
                                                >
                                                    <span className="badge badge-primary badge-sm">
                                                        {index + 1}
                                                    </span>
                                                    <span>{title}</span>
                                                </li>
                                            ),
                                        )}
                                    </ul>
                                )}

                                <div className="card-actions mt-4 justify-end">
                                    <Link
                                        to={`/review/${history.plan.id}`}
                                        className="btn btn-primary"
                                    >
                                        レビューを投稿する
                                    </Link>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </Container>
    );
}
