import { useState } from "react";
import { redirect, useSubmit } from "react-router";
import { getAuth, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import StartModal from "~/component/home/StartModal";
import { auth, provider } from "~/lib/firebase.client";
import Container from "~/component/Container";
import { createSession } from "~/lib/auth.server";  
import type { Route } from "./+types/home";

export async function action({ request }: Route.ActionArgs) {
  const formData = await request.formData();
  const token = formData.get("token");

  if (typeof token !== "string") {
    return { errorMessage: "Invalid token" };
  }
  
  const { user_id, needs_signup, setCookie } = await createSession(token);
  if (needs_signup) {
    return redirect("/signin");
  }
  if (user_id) {
    return redirect("/", 
      { headers: setCookie ? { "Set-Cookie": setCookie } : undefined },
    );
  }
  return { errorMessage: "Failed to create session" };
}

export default function Login() {
  const submit = useSubmit();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);


  const handleLoginSubmit = async () => {
    await signInWithPopup(auth, provider)
      .catch((error) => {
        setErrorMessage("ログインが中断されました");
        return;
      });
    const token = await auth.currentUser?.getIdToken();
    if (!token) {
      setErrorMessage("ログインに失敗しました");
      return;
    }
    
    submit(
      { token },
      { method: "post" },
    );
    
  }

  return (
    <div className="min-h-screen">
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