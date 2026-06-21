import { useEffect } from "react";
import { useRevalidator } from "react-router";
import type { Route } from "./+types/_auth.selection.$jobId";
import { backendFetch } from "~/lib/fetcher.server";

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

export async function loader({ request, params }: Route.LoaderArgs) {
    const { jobId } = params;

    const res = await backendFetch(request, `/recommendation/jobs/${jobId}/status`);
    if (!res.ok) {
        return { job: null, plan: null, errorMessage: "Recommendation job not found" };
    }
    const job = (await res.json()) as RecommendationJobStatus;

    let plan: Plan | null = null;
    if (job.status === "completed" && job.plan_id) {
        const planRes = await backendFetch(request, `/plans/${job.plan_id}`);
        if (planRes.ok) {
            plan = (await planRes.json()) as Plan;
        }
    }

    return { job, plan, errorMessage: null };
}

export default function FairySelection({ loaderData }: Route.ComponentProps) {
    const { job, plan, errorMessage } = loaderData;
    const revalidator = useRevalidator();

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
        <div className="p-8">
            <h1 className="text-xl font-semibold">プランを選ぶ</h1>
            {errorMessage && <p className="mt-4 text-error">{errorMessage}</p>}
            {job && <p className="mt-4">ステータス: {job.status}</p>}
            {plan && (
                <div className="mt-4">
                    <p>プランID: {plan.id}</p>
                    <p>名前: {plan.name}</p>
                    <p>説明: {plan.description}</p>
                    <ul>
                        {plan.details.map((item, index) => (
                            <li key={item.activity_id}>
                                {index + 1}. アクティビティID: {item.activity_id}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
