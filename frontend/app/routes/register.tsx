import { Form, redirect, useNavigate, useNavigation } from "react-router";
import { useState, useEffect } from "react";
import type { Route } from "./+types/route";
import { useAuthUser } from "~/lib/useAuthUser.client";
import { registerUser, createSession } from "~/lib/auth.server";


export async function action({ request }: Route.ActionArgs) {
    const formData = await request.formData();
    const displayName = getFormString(formData, "display_name");
    const token = getFormString(formData, "token");

    if (!displayName || !token) {
        return { errorMessage: "ユーザー名とトークンが必要です" };
    }

    const result = await registerUser({
        displayName,
        token,
    });

    if (result.response.status === 201 && result.data?.id) {
        return redirect("/", {
            headers: result.setCookie ? { "Set-Cookie": result.setCookie } : undefined,
        });
    }

    if (result.response.status === 409) {
        const session = await createSession(token);

        if (!session.needs_signup && session.user_id) {
            return redirect("/", {
                headers: session.setCookie
                    ? { "Set-Cookie": session.setCookie }
                    : undefined,
            });
        }

        return {
            errorMessage: `ログインに失敗しました: needs_signup=${session.needs_signup}, user_id=${session.user_id}`,
        };
    }

    if (result.response.status === 401) {
        return { errorMessage: "Google認証に失敗しました" };
    }

    return { errorMessage: "ユーザー登録に失敗しました" };
}

export default function Register({ actionData }: Route.ComponentProps) {
    const errorMessage = actionData?.errorMessage;
    const { user, loading } = useAuthUser();
    const navigate = useNavigate();
    const navigation = useNavigation();
    const [token, setToken] = useState<string | null>(null);
    const isSubmitting = navigation.state === "submitting";
    const canSubmit = Boolean(token) && !isSubmitting;

    useEffect(() => {
        if (loading) {
            return;
        }

        if (!user) {
            navigate("/home");
            return;
        }

        void user.getIdToken().then(setToken);
    }, [loading, navigate, user]);

    if (loading || !user || !token) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <span className="loading loading-spinner loading-md" />
            </div>
        );
    }

    return (
        <div className="min-h-screen">
            {errorMessage && <div className="alert alert-error">{errorMessage}</div>}
            <div className="mx-auto w-full max-w-xl px-8">
                <section className="mt-24">
                    <h1 className="text-xl">妖精からの招待状</h1>
                </section>
                <section className="mt-16">
                    <Form method="post" className="flex flex-col gap-4">
                        <input type="hidden" name="token" value={token} />
                        <input
                            className="input"
                            name="display_name"
                            type="text"
                            placeholder="あなたの名前を入力してください"
                            required
                            disabled={!canSubmit}
                        />
                        <button type="submit" className="btn" disabled={!canSubmit}>
                            {isSubmitting ? (
                                <span className="loading loading-spinner loading-sm" />
                            ) : (
                                "登録する"
                            )}
                        </button>
                    </Form>
                </section>
            </div>
        </div>
    );
}

function getFormString(formData: FormData, name: string): string | null {
    const value = formData.get(name);
    if (typeof value !== "string") {
        return null;
    }

    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : null;
}