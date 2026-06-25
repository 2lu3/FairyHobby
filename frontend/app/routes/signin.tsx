import { redirect, useFetcher, useNavigate } from "react-router";
import { useState, useEffect, useRef } from "react";
import type { Route } from "./+types/signin";
import { useAuthUser } from "~/lib/useAuthUser.client";
import { registerUser, createSession } from "~/lib/auth.server";
import Container from "~/component/Container";

export const meta: Route.MetaFunction = () => [
    { title: "新規登録 | 妖精からの招待状" },
];

export async function action({ request }: Route.ActionArgs) {
    const formData = await request.formData();
    const displayName = getFormString(formData, "display_name");
    const token = getFormString(formData, "token");

    if (!token) {
        return { errorMessage: "認証トークンが必要です" };
    }

    // Google ログイン直後: DB にユーザーがいればセッションを付与して / へ
    if (!displayName) {
        const session = await createSession(token);
        if (session.errorMessage) {
            return { errorMessage: session.errorMessage };
        }
        if (!session.needs_signup && session.user_id) {
            return redirectWithSession(session.setCookie);
        }
        return null;
    }

    // 新規登録: POST /users がセッションを付与する（createSession は呼ばない）
    const result = await registerUser({
        displayName,
        token,
    });

    if (result.response.status === 201 && result.data?.id) {
        return redirectWithSession(result.setCookie);
    }

    if (result.response.status === 409) {
        return { alreadyRegistered: true };
    }

    if (result.response.status === 401) {
        return { errorMessage: "Google認証に失敗しました" };
    }

    return { errorMessage: "ユーザー登録に失敗しました" };
}

export default function Register() {
    const { user, loading } = useAuthUser();
    const navigate = useNavigate();
    const sessionFetcher = useFetcher<{
        errorMessage?: string;
    }>();
    const registerFetcher = useFetcher<{
        errorMessage?: string;
        alreadyRegistered?: boolean;
    }>();
    const [token, setToken] = useState<string | null>(null);
    const sessionCheckedRef = useRef(false);
    const alreadyRegisteredHandledRef = useRef(false);

    const isCheckingSession =
        sessionFetcher.state === "submitting" || sessionFetcher.state === "loading";
    const isRegistering =
        registerFetcher.state === "submitting" || registerFetcher.state === "loading";
    const isBusy = isCheckingSession || isRegistering;
    const canSubmit = Boolean(token) && !isBusy;
    const errorMessage =
        sessionFetcher.data?.errorMessage ?? registerFetcher.data?.errorMessage ?? null;

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

    useEffect(() => {
        if (!token || sessionCheckedRef.current) {
            return;
        }
        sessionCheckedRef.current = true;
        sessionFetcher.submit({ token }, { method: "post" });
    }, [token, sessionFetcher]);

    useEffect(() => {
        if (
            !registerFetcher.data?.alreadyRegistered ||
            !token ||
            alreadyRegisteredHandledRef.current
        ) {
            return;
        }
        alreadyRegisteredHandledRef.current = true;
        sessionCheckedRef.current = false;
        sessionFetcher.submit({ token }, { method: "post" });
    }, [registerFetcher.data?.alreadyRegistered, token, sessionFetcher]);

    if (loading || !user || !token || isCheckingSession) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <span className="loading loading-spinner loading-md" />
            </div>
        );
    }

    return (
        <div className="min-h-screen">
            {errorMessage && <div className="alert alert-error">{errorMessage}</div>}
            <Container>
                <section className="mt-24">
                    <h1 className="text-xl">妖精からの招待状</h1>
                </section>
                <section className="mt-16">
                    <registerFetcher.Form method="post" className="flex flex-col gap-4">
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
                            {isRegistering ? (
                                <span className="loading loading-spinner loading-sm" />
                            ) : (
                                "登録する"
                            )}
                        </button>
                    </registerFetcher.Form>
                </section>
            </Container>
        </div>
    );
}

function redirectWithSession(setCookie: string | null) {
    if (!setCookie) {
        return { errorMessage: "セッションの保存に失敗しました" };
    }

    return redirect("/", {
        headers: { "Set-Cookie": setCookie },
    });
}

function getFormString(formData: FormData, name: string): string | null {
    const value = formData.get(name);
    if (typeof value !== "string") {
        return null;
    }

    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : null;
}
