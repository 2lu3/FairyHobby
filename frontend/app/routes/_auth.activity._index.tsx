import { Form, useNavigation } from "react-router";
import type { Route } from "./+types/_auth.activity._index";
import Container from "~/component/Container";
import { backendFetch } from "~/lib/fetcher.server";

export const meta: Route.MetaFunction = () => [
    { title: "体験をシェアする | 妖精からの招待状" },
];

export async function action({ request }: Route.ActionArgs) {
    const formData = await request.formData();

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
        return { errorMessage: "体験名と説明を入力してください", created: false };
    }

    const price = Number(priceRaw);
    const durationMinutes = Number(durationRaw);
    if (!Number.isInteger(price) || price < 0) {
        return { errorMessage: "料金は0以上の整数で入力してください", created: false };
    }
    if (!Number.isInteger(durationMinutes) || durationMinutes <= 0) {
        return { errorMessage: "所要時間は1以上の整数で入力してください", created: false };
    }

    const image_urls =
        typeof imageUrlsRaw === "string"
            ? imageUrlsRaw
                  .split("\n")
                  .map((url) => url.trim())
                  .filter((url) => url.length > 0)
            : [];

    const res = await backendFetch(request, "/activities/", {
        method: "POST",
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
        }),
    });

    if (!res.ok) {
        return { errorMessage: "体験の登録に失敗しました", created: false };
    }

    return { errorMessage: null, created: true };
}

export default function Activity({ actionData }: Route.ComponentProps) {
    const navigation = useNavigation();
    const isSubmitting = navigation.state === "submitting";

    return (
        <Container className="flex-1">
            <section className="mt-12">
                <h1 className="text-2xl font-bold">体験をシェアする</h1>
                <p className="mt-1 text-base-content/70">
                    あなたが提供する体験を登録しましょう。
                </p>

                {actionData?.errorMessage && (
                    <p className="mt-4 text-error">{actionData.errorMessage}</p>
                )}
                {actionData?.created && (
                    <p className="mt-4 text-success">体験を登録しました</p>
                )}

                <Form
                    method="post"
                    className="mt-8 flex flex-col gap-4"
                    key={actionData?.created ? "created" : "new"}
                >
                    <fieldset className="fieldset">
                        <legend className="fieldset-legend">体験名</legend>
                        <input
                            type="text"
                            name="name"
                            required
                            placeholder="例: はじめての陶芸体験"
                            className="input input-bordered w-full"
                        />
                    </fieldset>

                    <fieldset className="fieldset">
                        <legend className="fieldset-legend">説明</legend>
                        <textarea
                            name="description"
                            rows={4}
                            required
                            placeholder="体験の内容を入力してください"
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
                                placeholder="4500"
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
                                placeholder="90"
                                className="input input-bordered w-full"
                            />
                        </fieldset>
                    </div>

                    <fieldset className="fieldset">
                        <legend className="fieldset-legend">住所 (任意)</legend>
                        <input
                            type="text"
                            name="address"
                            placeholder="東京都台東区谷中3-1-1"
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
                            placeholder="https://example.com/photo.jpg"
                            className="textarea textarea-bordered w-full"
                        />
                    </fieldset>

                    <div className="flex justify-end">
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? "登録中..." : "体験を登録する"}
                        </button>
                    </div>
                </Form>
            </section>
        </Container>
    );
}
