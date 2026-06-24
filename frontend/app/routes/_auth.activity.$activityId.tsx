import { Form, Link, redirect, useNavigation } from "react-router";
import type { Route } from "./+types/_auth.activity.$activityId";
import Container from "~/component/Container";
import { backendFetch } from "~/lib/fetcher.server";

export const meta: Route.MetaFunction = () => [
    { title: "体験を編集する | 妖精からの招待状" },
];

type Activity = {
    id: string;
    name: string;
    description: string;
    price: number;
    duration_minutes: number;
    image_urls: string[];
    owner_user_id: string;
    address: string | null;
};

type CurrentUser = {
    id: string;
};

export async function loader({ request, params }: Route.LoaderArgs) {
    const { activityId } = params;

    const [activityRes, meRes] = await Promise.all([
        backendFetch(request, `/activities/${activityId}`),
        backendFetch(request, "/users/me"),
    ]);

    if (!activityRes.ok) {
        return { activity: null, isOwner: false };
    }
    const activity = (await activityRes.json()) as Activity;
    const currentUserId = meRes.ok
        ? ((await meRes.json()) as CurrentUser).id
        : null;

    return { activity, isOwner: currentUserId === activity.owner_user_id };
}

export async function action({ request, params }: Route.ActionArgs) {
    const { activityId } = params;
    const formData = await request.formData();
    const intent = formData.get("intent");

    if (intent === "delete") {
        const res = await backendFetch(request, `/activities/${activityId}`, {
            method: "DELETE",
        });
        if (!res.ok) {
            return { errorMessage: "体験の削除に失敗しました", saved: false };
        }
        return redirect("/mypage");
    }

    const name = formData.get("name");
    const description = formData.get("description");
    const priceRaw = formData.get("price");
    const durationRaw = formData.get("duration_minutes");
    const address = formData.get("address");
    const imageUrlsRaw = formData.get("image_urls");

    if (
        typeof name !== "string" ||
        name.trim().length === 0 ||
        typeof description !== "string" ||
        description.trim().length === 0
    ) {
        return { errorMessage: "体験名と説明を入力してください", saved: false };
    }

    const price = Number(priceRaw);
    const durationMinutes = Number(durationRaw);
    if (!Number.isInteger(price) || price < 0) {
        return { errorMessage: "料金は0以上の整数で入力してください", saved: false };
    }
    if (!Number.isInteger(durationMinutes) || durationMinutes <= 0) {
        return { errorMessage: "所要時間は1以上の整数で入力してください", saved: false };
    }

    const image_urls =
        typeof imageUrlsRaw === "string"
            ? imageUrlsRaw
                  .split("\n")
                  .map((url) => url.trim())
                  .filter((url) => url.length > 0)
            : [];

    const res = await backendFetch(request, `/activities/${activityId}`, {
        method: "PATCH",
        body: JSON.stringify({
            name: name.trim(),
            description: description.trim(),
            price,
            duration_minutes: durationMinutes,
            image_urls,
            address:
                typeof address === "string" && address.trim().length > 0
                    ? address.trim()
                    : null,
            preference_text: null,
        }),
    });

    if (!res.ok) {
        return { errorMessage: "体験の更新に失敗しました", saved: false };
    }

    return { errorMessage: null, saved: true };
}

export default function ActivityEdit({
    loaderData,
    actionData,
}: Route.ComponentProps) {
    const { activity, isOwner } = loaderData;
    const navigation = useNavigation();
    const isSubmitting = navigation.state === "submitting";

    if (!activity) {
        return (
            <Container className="flex-1">
                <section className="mt-12">
                    <p className="text-error">体験が見つかりませんでした</p>
                    <Link to="/mypage" className="link mt-4 inline-block">
                        マイページに戻る
                    </Link>
                </section>
            </Container>
        );
    }

    if (!isOwner) {
        return (
            <Container className="flex-1">
                <section className="mt-12">
                    <p className="text-error">
                        この体験を編集する権限がありません
                    </p>
                    <Link to="/mypage" className="link mt-4 inline-block">
                        マイページに戻る
                    </Link>
                </section>
            </Container>
        );
    }

    return (
        <Container className="flex-1">
            <section className="mt-12">
                <h1 className="text-2xl font-bold">体験を編集する</h1>

                {actionData?.errorMessage && (
                    <p className="mt-4 text-error">{actionData.errorMessage}</p>
                )}
                {actionData?.saved && (
                    <p className="mt-4 text-success">体験を更新しました</p>
                )}

                <Form method="post" className="mt-8 flex flex-col gap-4">
                    <fieldset className="fieldset">
                        <legend className="fieldset-legend">体験名</legend>
                        <input
                            type="text"
                            name="name"
                            required
                            defaultValue={activity.name}
                            className="input input-bordered w-full"
                        />
                    </fieldset>

                    <fieldset className="fieldset">
                        <legend className="fieldset-legend">説明</legend>
                        <textarea
                            name="description"
                            rows={4}
                            required
                            defaultValue={activity.description}
                            className="textarea textarea-bordered w-full"
                        />
                    </fieldset>

                    <div className="flex flex-col gap-4 sm:flex-row">
                        <fieldset className="fieldset flex-1">
                            <legend className="fieldset-legend">料金 (円)</legend>
                            <input
                                type="number"
                                name="price"
                                min={0}
                                step={1}
                                required
                                defaultValue={activity.price}
                                className="input input-bordered w-full"
                            />
                        </fieldset>

                        <fieldset className="fieldset flex-1">
                            <legend className="fieldset-legend">
                                所要時間 (分)
                            </legend>
                            <input
                                type="number"
                                name="duration_minutes"
                                min={1}
                                step={1}
                                required
                                defaultValue={activity.duration_minutes}
                                className="input input-bordered w-full"
                            />
                        </fieldset>
                    </div>

                    <fieldset className="fieldset">
                        <legend className="fieldset-legend">住所 (任意)</legend>
                        <input
                            type="text"
                            name="address"
                            defaultValue={activity.address ?? ""}
                            className="input input-bordered w-full"
                        />
                    </fieldset>

                    <fieldset className="fieldset">
                        <legend className="fieldset-legend">
                            画像URL (任意・1行に1つ)
                        </legend>
                        <textarea
                            name="image_urls"
                            rows={3}
                            defaultValue={activity.image_urls.join("\n")}
                            className="textarea textarea-bordered w-full"
                        />
                    </fieldset>

                    <div className="flex items-center justify-between">
                        <Link to="/mypage" className="btn btn-ghost">
                            戻る
                        </Link>
                        <button
                            type="submit"
                            name="intent"
                            value="update"
                            className="btn btn-primary"
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? "保存中..." : "更新する"}
                        </button>
                    </div>
                </Form>

                <Form
                    method="post"
                    className="mt-4"
                    onSubmit={(event) => {
                        if (!confirm("この体験を削除しますか?")) {
                            event.preventDefault();
                        }
                    }}
                >
                    <button
                        type="submit"
                        name="intent"
                        value="delete"
                        className="btn btn-error btn-outline"
                        disabled={isSubmitting}
                    >
                        この体験を削除する
                    </button>
                </Form>
            </section>
        </Container>
    );
}
