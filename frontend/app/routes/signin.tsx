import { useFetcher, useNavigate } from "react-router";
import { useState, useEffect } from "react";
import type { Route } from "./+types/signin";
import { useAuthUser } from "~/lib/useAuthUser.client";
import {
  registerUser,
  createSession,
  redirectWithSession,
} from "~/lib/auth.server";
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

  if (!displayName) {
    return { errorMessage: "表示名が必要です" };
  }

  const result = await registerUser({
    displayName,
    token,
  });

  if (result.response.status === 201 && result.data?.id) {
    return redirectWithSession(result.setCookie);
  }

  if (result.response.status === 409) {
    const session = await createSession(token);
    if (session.user_id && !session.needs_signup) {
      return redirectWithSession(session.setCookie);
    }
    return { errorMessage: "すでに登録済みです" };
  }

  if (result.response.status === 401) {
    return { errorMessage: "Google認証に失敗しました" };
  }

  return { errorMessage: "ユーザー登録に失敗しました" };
}

export default function Register() {
  const { user, loading } = useAuthUser();
  const navigate = useNavigate();
  const registerFetcher = useFetcher<{
    errorMessage?: string;
  }>();
  const [token, setToken] = useState<string | null>(null);

  const isRegistering =
    registerFetcher.state === "submitting" ||
    registerFetcher.state === "loading";
  const canSubmit = Boolean(token) && !isRegistering;
  const errorMessage = registerFetcher.data?.errorMessage ?? null;

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

function getFormString(formData: FormData, name: string): string | null {
  const value = formData.get(name);
  if (typeof value !== "string") {
    return null;
  }

  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}
