import { useEffect } from "react";
import { useNavigate, useRevalidator } from "react-router";
import type { Route } from "./+types/_auth.selection.$jobId";
import { backendFetch } from "~/lib/fetcher.server";
import Container from "~/component/Container";

type RecommendationStatus = "pending" | "calculating" | "completed" | "failed";

type RecommendationJobStatus = {
    status: RecommendationStatus;
    plan_id: string | null;
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

export async function loader({ request, params }: Route.LoaderArgs) {
    const { jobId } = params;

    const res = await backendFetch(request, `/recommendation/jobs/${jobId}/status`);
    if (!res.ok) {
        return {
            job: null,
            plan: null,
            activities: [],
            errorMessage: "Recommendation job not found",
        };
    }
    const job = (await res.json()) as RecommendationJobStatus;

    let plan: Plan | null = null;
    let activities: Activity[] = [];
    if (job.status === "completed" && job.plan_id) {
        const planRes = await backendFetch(request, `/plans/${job.plan_id}`);
        if (planRes.ok) {
            plan = (await planRes.json()) as Plan;

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
            activities = activityResults.filter(
                (activity): activity is Activity => activity !== null,
            );
        }
    }

    return { job, plan, activities, errorMessage: null };
}

export default function FairySelection({ loaderData }: Route.ComponentProps) {
    const { job, plan, activities, errorMessage } = loaderData;
    const revalidator = useRevalidator();
    const navigate = useNavigate();

    const isFinished = job?.status === "completed" || job?.status === "failed";

    useEffect(() => {
        if (isFinished) {
            return;
        }
        const intervalId = setInterval(() => {
            revalidator.revalidate();
        }, 1000);
        return () => clearInterval(intervalId);
    }, [isFinished, revalidator]);

    return (
            <Container className="flex-1">
                <h1 className="text-xl font-semibold">プランを選ぶ</h1>
            {errorMessage && <p className="mt-4 text-error">{errorMessage}</p>}
            {job && <p className="mt-4">ステータス: {job.status}</p>}
            {job?.status === "completed" && !plan && (
                <p className="mt-4">条件に合うものが見つかりませんでした。</p>
            )}
            {plan && (
                <div className="mt-4">
                    <h2 className="text-2xl font-bold">{plan.name}</h2>
                    {plan.description && (
                        <p className="mt-1 text-base-content/70">{plan.description}</p>
                    )}
                    <div className="mt-6 flex flex-col gap-4">
                        {activities.map((activity, index) => (
                            <div
                                key={activity.id}
                                className="card bg-base-100 shadow-md"
                            >
                                {activity.image_urls.length > 0 && (
                                    <figure>
                                        <img
                                            src={activity.image_urls[0]}
                                            alt={activity.name}
                                            className="h-48 w-full object-cover"
                                        />
                                    </figure>
                                )}
                                <div className="card-body">
                                    <h3 className="card-title">
                                        <span className="badge badge-primary">
                                            {index + 1}
                                        </span>
                                        {activity.name}
                                    </h3>
                                    <p className="text-base-content/80">
                                        {activity.description}
                                    </p>
                                    {activity.address && (
                                        <p className="text-sm text-base-content/60">
                                            📍 {activity.address}
                                        </p>
                                    )}
                                    <div className="card-actions mt-2 items-center gap-2">
                                        <span className="badge badge-outline">
                                            ¥{activity.price.toLocaleString()}
                                        </span>
                                        <span className="badge badge-outline">
                                            {activity.duration_minutes}分
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="mt-8 flex gap-4">
                        <button
                            type="button"
                            className="btn btn-outline flex-1"
                            onClick={() => navigate("/")}
                        >
                            辞退する
                        </button>
                        <button
                            type="button"
                            className="btn btn-primary flex-1"
                            onClick={() => navigate(`/payment/${plan.id}`)}
                        >
                            受け取る
                        </button>
                    </div>
                </div>
            )}
            </Container>
    );
}
