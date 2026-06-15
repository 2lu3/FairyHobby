import { Form, redirect } from "react-router";
import { useState, useEffect } from "react";
import type { Route } from "./+types/route";
import { useAuthUser } from "~/lib/useAuthUser.client";

export async function action({ request }: Route.ActionArgs) {
    const formData = await request.formData();
    const displayName = formData.get("display_name");
    const token = formData.get("token");

    if (typeof displayName !== "string" || !displayName.trim()) {
        return { errorMessage: "名前を入力してください" };
    }
    if (typeof token !== "string" || !token) {
        return { errorMessage: "ログインが必要です" };
    }

    const response = await fetch(`${process.env.BACKEND_URL}/users/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ display_name: displayName.trim() }),
    });

    const data = await response.json().catch(() => null);

    if (response.status === 201 || response.status === 409) {
        return redirect(`/${data?.id}`);
    }
    if (response.status === 401) {
        return { errorMessage: "Google認証に失敗しました" };
    }
    return { errorMessage: "ユーザー登録に失敗しました" };
}

export default function Register( { actionData }: Route.ComponentProps) {
    const errorMessage = actionData?.errorMessage;
    const { user } = useAuthUser();
    const [token, setToken] = useState<string | null>(null);


    useEffect(() => {
        if (user) {
            user.getIdToken().then((token) => {
                setToken(token);
            });
        }
    }, [user]);

    return (
        <div className="min-h-screen">
            {errorMessage && <div className="alert alert-error">{errorMessage}</div>}
            <div className="mx-auto w-full max-w-xl px-8">
                <section className="mt-24">
                    <h1 className="text-xl">妖精からの招待状</h1>
                </section>
                <section className="mt-16">
                    <Form method="post">
                        <input className="input" name="display_name" type="text" placeholder="あなたの名前を入力してください" required />
                        {token ? <button type="submit" className="btn">登録する</button> : <span className="loading loading-spinner loading-md"></span>}
                        <input type="hidden" name="token" value={token ?? ""} />
                    </Form>
                </section>
            </div>
        </div>
    );
}