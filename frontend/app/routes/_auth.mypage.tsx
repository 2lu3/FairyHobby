import { Link } from "react-router";
import type { Route } from "./+types/_auth.mypage";
import Container from "~/component/Container";
import { backendFetch } from "~/lib/fetcher.server";

export const meta: Route.MetaFunction = () => [
    { title: "マイページ | 妖精からの招待状" },
];

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
    description: string;
    price: number;
    duration_minutes: number;
    image_urls: string[];
    address: string | null;
};

type ExperiencedActivity = {
    id: string;
    name: string;
    image_urls: string[];
    planId: string;
};

export async function loader({ request }: Route.LoaderArgs) {
    // これまで体験した体験 (プラン履歴に含まれる体験を集約)
    const historyRes = await backendFetch(request, "/plan-histories");
    const planHistories = historyRes.ok
        ? ((await historyRes.json()) as PlanHistory[])
        : [];

    const experiencedLists = await Promise.all(
        planHistories.map(async (history) => {
            const planRes = await backendFetch(
                request,
                `/plans/${history.plan_id}`,
            );
            if (!planRes.ok) {
                return [] as ExperiencedActivity[];
            }
            const plan = (await planRes.json()) as Plan;

            const activities = await Promise.all(
                plan.details.map(async (item) => {
                    const activityRes = await backendFetch(
                        request,
                        `/activities/${item.activity_id}`,
                    );
                    if (!activityRes.ok) {
                        return null;
                    }
                    const activity = (await activityRes.json()) as Activity;
                    return {
                        id: activity.id,
                        name: activity.name,
                        image_urls: activity.image_urls,
                        planId: plan.id,
                    } satisfies ExperiencedActivity;
                }),
            );
            return activities.filter(
                (activity): activity is ExperiencedActivity => activity !== null,
            );
        }),
    );

    // 体験を重複排除 (同じ体験が複数プランに含まれる場合は最初の1件を残す)
    const experiencedMap = new Map<string, ExperiencedActivity>();
    for (const activity of experiencedLists.flat()) {
        if (!experiencedMap.has(activity.id)) {
            experiencedMap.set(activity.id, activity);
        }
    }
    const experienced = Array.from(experiencedMap.values());

    // 打った体験 (自分が作成した体験)
    const ownedRes = await backendFetch(request, "/activities/me");
    const owned = ownedRes.ok ? ((await ownedRes.json()) as Activity[]) : [];

    return {
        experienced,
        owned,
        historyError: historyRes.ok ? null : "体験履歴の取得に失敗しました",
        ownedError: ownedRes.ok ? null : "作成した体験の取得に失敗しました",
    };
}

export default function MyPage({ loaderData }: Route.ComponentProps) {
    const { experienced, owned, historyError, ownedError } = loaderData;

    return (
        <Container className="flex-1">
            <section className="mt-24">
                <h1 className="text-2xl font-bold">マイページ</h1>

                {/* これまで体験した体験 */}
                <div className="mt-10">
                    <h2 className="text-xl font-semibold">
                        これまで体験した体験
                    </h2>
                    {historyError && (
                        <p className="mt-4 text-error">{historyError}</p>
                    )}
                    {!historyError && experienced.length === 0 && (
                        <p className="mt-4 text-base-content/60">
                            まだ体験した体験がありません
                        </p>
                    )}
                    <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
                        {experienced.map((activity) => (
                            <div
                                key={activity.id}
                                className="card bg-base-100 shadow-md"
                            >
                                {activity.image_urls.length > 0 && (
                                    <figure>
                                        <img
                                            src={activity.image_urls[0]}
                                            alt={activity.name}
                                            className="h-40 w-full object-cover"
                                        />
                                    </figure>
                                )}
                                <div className="card-body">
                                    <h3 className="card-title">
                                        {activity.name}
                                    </h3>
                                    <div className="card-actions mt-2 justify-end">
                                        <Link
                                            to={`/review/${activity.planId}`}
                                            className="btn btn-primary btn-sm"
                                        >
                                            レビューを編集する
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* シェアした体験 (自分が作成した体験) */}
                <div className="mt-14">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-semibold">シェアした体験</h2>
                        <Link to="/activity" className="btn btn-secondary btn-sm">
                            体験をシェアする
                        </Link>
                    </div>
                    {ownedError && (
                        <p className="mt-4 text-error">{ownedError}</p>
                    )}
                    {!ownedError && owned.length === 0 && (
                        <p className="mt-4 text-base-content/60">
                            まだ作成した体験がありません
                        </p>
                    )}
                    <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
                        {owned.map((activity) => (
                            <div
                                key={activity.id}
                                className="card bg-base-100 shadow-md"
                            >
                                {activity.image_urls.length > 0 && (
                                    <figure>
                                        <img
                                            src={activity.image_urls[0]}
                                            alt={activity.name}
                                            className="h-40 w-full object-cover"
                                        />
                                    </figure>
                                )}
                                <div className="card-body">
                                    <h3 className="card-title">
                                        {activity.name}
                                    </h3>
                                    {activity.description && (
                                        <p className="line-clamp-2 text-base-content/80">
                                            {activity.description}
                                        </p>
                                    )}
                                    <div className="mt-2 flex flex-wrap gap-2">
                                        <span className="badge badge-outline">
                                            ¥{activity.price.toLocaleString()}
                                        </span>
                                        <span className="badge badge-outline">
                                            {activity.duration_minutes}分
                                        </span>
                                    </div>
                                    <div className="card-actions mt-2 justify-end">
                                        <Link
                                            to={`/activity/${activity.id}`}
                                            className="btn btn-primary btn-sm"
                                        >
                                            編集する
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>
        </Container>
    );
}
