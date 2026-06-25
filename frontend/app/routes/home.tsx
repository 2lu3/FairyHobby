import { useState } from "react";
import { redirect, useFetcher } from "react-router";
import { signInWithPopup } from "firebase/auth";
import StartModal from "~/component/home/StartModal";
import { auth, provider } from "~/lib/firebase.client";
import Container from "~/component/Container";
import { createSession, redirectWithSession } from "~/lib/auth.server";
import type { Route } from "./+types/home";

function closeStartModal() {
  const dialog = document.getElementById("start_modal");
  if (dialog instanceof HTMLDialogElement) {
    dialog.close();
  }
}

export const meta: Route.MetaFunction = () => [
  { title: "妖精からの招待状" },
];

export async function action({ request }: Route.ActionArgs) {
  const formData = await request.formData();
  const token = getFormString(formData, "token");

  if (!token) {
    return { errorMessage: "認証トークンが必要です" };
  }

  const session = await createSession(token);
  if (session.errorMessage) {
    return { errorMessage: session.errorMessage };
  }

  if (session.needs_signup) {
    return redirect("/signin");
  }

  if (session.user_id) {
    return redirectWithSession(session.setCookie);
  }

  return { errorMessage: "セッションの作成に失敗しました" };
}

export default function Login() {
  const fetcher = useFetcher<{ errorMessage?: string }>();
  const [localErrorMessage, setLocalErrorMessage] = useState<string | null>(null);
  const [isPopupSigningIn, setIsPopupSigningIn] = useState(false);

  const isSubmitting =
    isPopupSigningIn ||
    fetcher.state === "submitting" ||
    fetcher.state === "loading";
  const errorMessage = fetcher.data?.errorMessage ?? localErrorMessage;

  const handleLoginSubmit = async () => {
    setLocalErrorMessage(null);
    setIsPopupSigningIn(true);

    try {
      await signInWithPopup(auth, provider);
    } catch {
      setLocalErrorMessage("ログインが中断されました");
      setIsPopupSigningIn(false);
      return;
    }

    const token = await auth.currentUser?.getIdToken();
    if (!token) {
      setLocalErrorMessage("ログインに失敗しました");
      setIsPopupSigningIn(false);
      return;
    }

    closeStartModal();
    fetcher.submit({ token }, { method: "post" });
    setIsPopupSigningIn(false);
  };

  return (
    <div className="min-h-screen">
      {isSubmitting && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20">
          <span className="loading loading-spinner loading-lg" />
        </div>
      )}
      <Container>
        <section className="mt-24">
          {errorMessage && <div className="alert alert-error">{errorMessage}</div>}
          <div className="flex flex-col gap-8 items-center">
            <h1 className="text-xl">妖精からの招待状</h1>
            <StartModal handleLoginSubmit={handleLoginSubmit} />
          </div>
          <div className="mt-16 flex flex-col gap-4 items-center leading-looser tracking-wide">
            <p>妖精からの招待状は、あなたの人生の新しい楽しみ方を見つけるお手伝いをするサービスです。</p>
            <p>何かを始める理由は、立派なものでなくても構いません。「なんとなく気になったから」「少しだけ毎日を変えてみたいから」そんな「ちょっと面白そう」という気持ちを大切にしています。</p>
            <p>妖精から届く小さな招待状をきっかけに、まだ知らなかった世界や、思いがけない楽しみと出会えるかもしれません。</p>
          </div>
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
