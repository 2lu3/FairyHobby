import { Form, useNavigation } from "react-router";
import type { Route } from "./+types/_auth.review.$planId";
import Container from "~/component/Container";
import { backendFetch } from "~/lib/fetcher.server";

type PlanItem = {
    activity_id: string;
};

type Plan = {
    id: string;
    name: string;
    description: string;
    details: PlanItem[];
};

type ActivityReview = {
    id: string;
    text: string;
    activity_id: string;
    owner_user_id: string;
};

type Activity = {
    id: string;
    name: string;
    description: string;
    image_urls: string[];
    reviews: ActivityReview[];
};

type CurrentUser = {
    id: string;
};

export async function loader({ request, params }: Route.LoaderArgs) {
    const { planId } = params;

    const planRes = await backendFetch(request, `/plans/${planId}`);
    if (!planRes.ok) {
        return {
            plan: null,
            activities: [] as Activity[],
            currentUserId: null as string | null,
            errorMessage: "プランが見つかりませんでした",
        };
    }
    const plan = (await planRes.json()) as Plan;

    const meRes = await backendFetch(request, "/users/me");
    const currentUserId = meRes.ok
        ? ((await meRes.json()) as CurrentUser).id
        : null;

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
    const activities = activityResults.filter(
        (activity): activity is Activity => activity !== null,
    );

    return { plan, activities, currentUserId, errorMessage: null };
}

export async function action({ request }: Route.ActionArgs) {
    const formData = await request.formData();
    const activityId = formData.get("activity_id");
    const text = formData.get("text");
    const reviewId = formData.get("review_id");

    if (typeof activityId !== "string" || typeof text !== "string") {
        return { errorMessage: "入力内容が不正です", activityId: null };
    }
    if (text.trim().length === 0) {
        return { errorMessage: "レビューを入力してください", activityId };
    }

    const res =
        typeof reviewId === "string" && reviewId.length > 0
            ? await backendFetch(request, `/activity-reviews/${reviewId}`, {
                  method: "PATCH",
                  body: JSON.stringify({ text }),
              })
            : await backendFetch(request, "/activity-reviews/", {
                  method: "POST",
                  body: JSON.stringify({ activity_id: activityId, text }),
              });
    if (!res.ok) {
        return { errorMessage: "レビューの投稿に失敗しました", activityId };
    }

    return { errorMessage: null, activityId };
}

export default function Review({
    loaderData,
    actionData,
}: Route.ComponentProps) {
    const { plan, activities, currentUserId, errorMessage } = loaderData;
    const navigation = useNavigation();
    const isLoadingReviews = navigation.state === "loading";

    return (
        <Container className="flex-1">
            <section className="mt-24">
                <h1 className="text-2xl font-bold">レビューを投稿する</h1>
                {plan && (
                    <p className="mt-1 text-base-content/70">{plan.name}</p>
                )}

                {errorMessage && (
                    <p className="mt-4 text-error">{errorMessage}</p>
                )}

                <div className="mt-8 flex flex-col gap-6">
                    {activities.map((activity) => {
                        const isTarget = actionData?.activityId === activity.id;
                        const succeeded = isTarget && !actionData?.errorMessage;
                        const failed = isTarget && !!actionData?.errorMessage;

                        const existingReview = currentUserId
                            ? activity.reviews.find(
                                  (review) =>
                                      review.owner_user_id === currentUserId,
                              )
                            : undefined;

                        return (
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
                                    <h2 className="card-title">{activity.name}</h2>
                                    {activity.description && (
                                        <p className="text-base-content/80">
                                            {activity.description}
                                        </p>
                                    )}

                                    <Form
                                        method="post"
                                        className="mt-4 flex flex-col gap-3"
                                    >
                                        <input
                                            type="hidden"
                                            name="activity_id"
                                            value={activity.id}
                                        />
                                        {existingReview && (
                                            <input
                                                type="hidden"
                                                name="review_id"
                                                value={existingReview.id}
                                            />
                                        )}
                                        <fieldset className="fieldset">
                                            <legend className="fieldset-legend">
                                                レビュー
                                            </legend>
                                            {isLoadingReviews ? (
                                                <div className="flex w-full justify-center py-6">
                                                    <span className="loading loading-spinner loading-md"></span>
                                                </div>
                                            ) : (
                                                <textarea
                                                    key={
                                                        existingReview?.id ??
                                                        "new"
                                                    }
                                                    name="text"
                                                    rows={4}
                                                    defaultValue={
                                                        existingReview?.text ??
                                                        ""
                                                    }
                                                    placeholder="体験した感想を入力してください"
                                                    className="textarea textarea-bordered w-full"
                                                />
                                            )}
                                        </fieldset>

                                        {failed && (
                                            <p className="text-error">
                                                {actionData?.errorMessage}
                                            </p>
                                        )}
                                        {succeeded && (
                                            <p className="text-success">
                                                レビューを保存しました
                                            </p>
                                        )}

                                        <div className="card-actions justify-end">
                                            <button
                                                type="submit"
                                                className="btn btn-primary"
                                            >
                                                {existingReview
                                                    ? "更新する"
                                                    : "投稿する"}
                                            </button>
                                        </div>
                                    </Form>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </section>
        </Container>
    );
}
