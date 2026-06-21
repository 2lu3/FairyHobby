import { useEffect, useState } from "react";
import { Form, redirect } from "react-router";
import type { Route } from "./+types/_auth.settings";
import Container from "~/component/Container";
import { backendFetch } from "~/lib/fetcher.server";


export async function loader({ request }: Route.LoaderArgs) {
    const res = await backendFetch(request, "/users/me");
    if (!res.ok) {
        return redirect("/home");
    }
    const user = await res.json();
    return { userId: user.id, displayName: user.display_name };
}

export async function action({ request }: Route.ActionArgs) {
    const formData = await request.formData();
    const displayName = formData.get("display_name");
    if (!displayName) {
        return { errorMessage: "名前が必要です" };
    }
    const userId = formData.get("userId");
    if (!userId) {
        return { errorMessage: "ユーザーIDが必要です" };
    }
    const res = await backendFetch(request, `/users/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({ "display_name": displayName }),
    });
    if (!res.ok) {
        return { errorMessage: "名前の更新に失敗しました" };
    }
    return redirect("/settings");
}

export default function Settings({ loaderData }: Route.ComponentProps) {
    const [displayName, setDisplayName] = useState(loaderData.displayName);
    const [changeDisplayName, setChangeDisplayName] = useState(false);

    useEffect(() => {
        setDisplayName(loaderData.displayName);
        setChangeDisplayName(false);
    }, [loaderData.displayName]);

    return (
            <Container className="flex-1 flex flex-col gap-12">
                <section className="mt-24 border-b border-base-300 pb-4">
                    <h1>設定</h1>
                </section>
                <section>
                    <fieldset className="fieldset bg-base-100 border-base-300 rounded-box w-xs border p-4">
                        <p className="text-base">
                            名前
                        </p>
                        {changeDisplayName ? (
                            <Form method="post" className="flex flex-col gap-4">
                                <input type="text" className="input text-base" name="display_name" value={displayName} onChange={(e) => setDisplayName(e.target.value)} required />
                                <input type="hidden" name="userId" value={loaderData.userId} />
                                <div className="flex justify-end gap-2">
                                    <button type="button" onClick={() => { setDisplayName(loaderData.displayName); setChangeDisplayName(false); }} className="btn bg-base-100 border-base-100">キャンセル</button>
                                    <button type="submit" className="btn border-base-300 btn-outline w-fit">保存する</button>
                                </div>
                            </Form>
                        ) : (
                            <div className="flex flex-col gap-4">
                                <div className="text-base">
                                    {displayName}
                                </div>
                                <button type="button" onClick={() => setChangeDisplayName(true)} className="btn border-base-300 btn-outline w-fit">変更</button>
                            </div>

                        )}
                    </fieldset>
                </section>
            </Container>
    )
}