import { useState } from "react";
import { Form, Link, redirect } from "react-router";
import type { Route } from "./+types/_auth.payment.$planId";
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

type Activity = {
    id: string;
    name: string;
    price: number;
};

export async function loader({ request, params }: Route.LoaderArgs) {
    const { planId } = params;

    const planRes = await backendFetch(request, `/plans/${planId}`);
    if (!planRes.ok) {
        return {
            planId,
            plan: null,
            totalPrice: 0,
            errorMessage: "プランが見つかりませんでした",
        };
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
    const activities = activityResults.filter(
        (activity): activity is Activity => activity !== null,
    );

    const totalPrice = activities.reduce(
        (sum, activity) => sum + activity.price,
        0,
    );

    return { planId, plan, totalPrice, errorMessage: null };
}

export async function action({ request, params }: Route.ActionArgs) {
    const { planId } = params;

    const res = await backendFetch(request, "/plan-histories", {
        method: "POST",
        body: JSON.stringify({ plan_id: planId }),
    });
    if (!res.ok) {
        const body = await res.text();
        console.error(
            `Failed to create plan history: status=${res.status} planId=${planId} body=${body}`,
        );
        return { errorMessage: "購入処理に失敗しました" };
    }
    return redirect("/mypage");
}

function formatCardNumber(value: string): string {
    const digits = value.replace(/\D/g, "").slice(0, 16);
    return digits.replace(/(.{4})/g, "$1 ").trim();
}

function formatExpiry(value: string): string {
    const digits = value.replace(/\D/g, "").slice(0, 4);
    if (digits.length <= 2) {
        return digits;
    }
    return `${digits.slice(0, 2)}/${digits.slice(2)}`;
}

export default function Payment({ loaderData, actionData }: Route.ComponentProps) {
    const { plan, totalPrice, errorMessage } = loaderData;
    const [cardNumber, setCardNumber] = useState("");
    const [cardHolder, setCardHolder] = useState("");
    const [expiry, setExpiry] = useState("");
    const [cvc, setCvc] = useState("");

    return (
        <Container size="sm" className="min-h-screen flex items-center">
            <div className="card w-full bg-base-100 shadow-xl">
                <div className="card-body">
                    <h1 className="text-2xl font-bold">お支払い</h1>
                    <p className="text-base-content/70">
                        クレジットカード情報を入力してください
                    </p>

                    {errorMessage && (
                        <p className="mt-2 text-error">{errorMessage}</p>
                    )}

                    {plan && (
                        <div className="mt-4 rounded-box bg-base-200 p-4">
                            <p className="font-semibold">{plan.name}</p>
                            <div className="mt-2 flex items-center justify-between">
                                <span className="text-base-content/70">合計金額</span>
                                <span className="text-2xl font-bold">
                                    ¥{totalPrice.toLocaleString()}
                                </span>
                            </div>
                        </div>
                    )}

                    <Form method="post" className="mt-6 flex flex-col gap-4">
                        <fieldset className="fieldset">
                            <legend className="fieldset-legend">カード番号</legend>
                            <input
                                type="text"
                                inputMode="numeric"
                                autoComplete="cc-number"
                                placeholder="1234 5678 9012 3456"
                                className="input input-bordered w-full"
                                value={cardNumber}
                                onChange={(e) =>
                                    setCardNumber(formatCardNumber(e.target.value))
                                }
                            />
                        </fieldset>

                        <fieldset className="fieldset">
                            <legend className="fieldset-legend">カード名義</legend>
                            <input
                                type="text"
                                autoComplete="cc-name"
                                placeholder="TARO YAMADA"
                                className="input input-bordered w-full uppercase"
                                value={cardHolder}
                                onChange={(e) => setCardHolder(e.target.value)}
                            />
                        </fieldset>

                        <div className="flex gap-4">
                            <fieldset className="fieldset flex-1">
                                <legend className="fieldset-legend">有効期限</legend>
                                <input
                                    type="text"
                                    inputMode="numeric"
                                    autoComplete="cc-exp"
                                    placeholder="MM/YY"
                                    className="input input-bordered w-full"
                                    value={expiry}
                                    onChange={(e) =>
                                        setExpiry(formatExpiry(e.target.value))
                                    }
                                />
                            </fieldset>

                            <fieldset className="fieldset flex-1">
                                <legend className="fieldset-legend">セキュリティコード</legend>
                                <input
                                    type="text"
                                    inputMode="numeric"
                                    autoComplete="cc-csc"
                                    placeholder="123"
                                    className="input input-bordered w-full"
                                    value={cvc}
                                    onChange={(e) =>
                                        setCvc(
                                            e.target.value
                                                .replace(/\D/g, "")
                                                .slice(0, 4),
                                        )
                                    }
                                />
                            </fieldset>
                        </div>

                        {actionData?.errorMessage && (
                            <p className="text-error">{actionData.errorMessage}</p>
                        )}

                        <div className="mt-4 flex flex-col gap-2">
                            <button
                                type="submit"
                                className="btn btn-primary w-full"
                                disabled={!plan}
                            >
                                続行する
                            </button>
                            <Link to="/mypage" className="btn btn-ghost w-full">
                                キャンセルする
                            </Link>
                        </div>
                    </Form>
                </div>
            </div>
        </Container>
    );
}
