import { backendFetch } from "~/lib/fetcher.server";
import type { Route } from "./+types/_auth.fairy.$fairyId";
import Container from "~/component/Container";
import { useState } from "react";
import { DayPicker } from "react-day-picker";
import { Form, redirect, useNavigate, useRouteLoaderData } from "react-router";
import type { loader as authLoader } from "./_auth";

export async function loader({ request, params }: Route.LoaderArgs) {
    const { fairyId } = params;
    const res = await backendFetch(request, `/fairies/${fairyId}`);
    const fairy = await res.json();
    if (!res.ok) {
        return { fairy: null, errorMessage: "Fairy not found" };
    }
    const description = fairy.prompt.split("。")[0] + "。" + fairy.prompt.split("。")[1];
    return { fairy, description, errorMessage: null };
}

export async function action({ request, params }: Route.ActionArgs) {
    const formData = await request.formData();
    const payload = {
        date: formData.get("date"),
        budget: formData.get("budget"),
    }

    const res = await backendFetch(request, `/recommendation/jobs`, {
        method: "POST",
        body: JSON.stringify(payload),
    });
    if (!res.ok) {
        return { errorMessage: "Failed to create recommendation job" };
    }
    const recommendationJob = await res.json();
    return redirect(`/selection/${recommendationJob.id}`);
}


export default function Fairy({ loaderData }: Route.ComponentProps) {
    const { user } = useRouteLoaderData("routes/_auth") as Exclude<
        Awaited<ReturnType<typeof authLoader>>,
        Response
    >;
    const navigate = useNavigate();
    const { fairy, description, errorMessage } = loaderData;
    const [userAgreed, setUserAgreed] = useState<boolean>(false);
    const [date, setDate] = useState<Date | null>(null);
    const [budget, setBudget] = useState<number | null>(null);
    const [error] = useState<string | null>(errorMessage);

    const canAccept =
        date !== null &&
        budget !== null;

    return (
        <div className="min-h-screen flex flex-col items-center justify-center">
            {errorMessage && <div className="alert alert-error">{error}</div>}
            <Container size="sm" className="flex flex-col gap-12">
                <h1 className="text-center text-xl">招待状を受け取りますか？</h1>
                <div className="bg-[url('/paper.jpg')] bg-cover bg-center bg-no-repeat shadow-lg py-8 px-12">
                    {!userAgreed ? <FairyLetter fairyName={fairy.name} userName={user.display_name} />
                        :
                        <UserLetter fairyName={fairy.name} userName={user.display_name} date={date} setDate={setDate} budget={budget} setBudget={setBudget} />}
                </div>
                {userAgreed ? (
                    <Form method="post">
                        <input type="hidden" name="date" value={date?.toISOString() ?? ""} required />
                        <input type="hidden" name="budget" value={budget?.toString() ?? ""} required />
                        <div className="flex justify-center gap-4">
                            <button type="button" className="btn btn-outline" onClick={() => navigate("/")}>やめる</button>
                            <button type="submit" className="btn btn-primary" disabled={!canAccept}>送信する</button>
                        </div>
                    </Form>
                ) : (
                    <div className="flex justify-center gap-4">
                        <button className="btn btn-outline" onClick={() => navigate("/")}>やめる</button>
                        <button className="btn btn-primary" onClick={() => setUserAgreed(true)}>受け取る</button>
                    </div>
                )}
            </Container>
        </div>
    )
}

function FairyLetter({ fairyName, userName }: { fairyName: string; userName: string }) {
    return (
        <article className="prose prose-neutral max-w-none">
            <h1 className="text-center font-normal tracking-wide">
                親愛なる {userName} 様
            </h1>
            <p>私は、あなたのそばで日々を見守る小さな妖精です。</p>
            <p>
                あなたの歩みを眺めているうちに、贈りたい小さな冒険を見つけました。
            </p>
            <div className="not-prose my-8 space-y-2 text-center text-sm tracking-[0.2em] text-base-content/75">
                <p>知らない香り。</p>
                <p>初めての手触り。</p>
                <p>久しぶりに踊る心</p>
            </div>
            <p>
                完璧な準備は要りません。
                好奇心だけ、持ってきてください。
            </p>
            <p>あなたが来てくれたら、私も嬉しいです。</p>
            <p className="mt-12 text-right not-prose:text-sm not-prose:tracking-widest">
                {fairyName} より
            </p>
        </article>
    );
}

interface UserLetterProps {
    fairyName: string;
    userName: string;
    date: Date | null;
    setDate: (date: Date) => void;
    budget: number | null;
    setBudget: (budget: number | null) => void;
}

function UserLetter({ fairyName, userName, date, setDate, budget, setBudget }: UserLetterProps) {
    return (
        <article className="prose prose-neutral max-w-none">
            <h1 className="text-center font-normal tracking-wide">
                小さな妖精 {fairyName} 様
            </h1>
            <p>
                お手紙、拝見しました。
                こんなことを思ってくださっていたとは、思いもよりません。
                お誘いいただき、ありがとうございます。
            </p>
            <p>
                ささやかながら、私の状況をお伝えさせてください。
            </p>
            <p>
                ご都合をお聞きくださるのでしたら、
                <CalendarPicker id="date" date={date} setDate={setDate} />
                でしたら、構いません。
            </p>
            <p>
                また、予算は
                <input
                    type="number"
                    value={budget ?? ""}
                    onChange={(e) => setBudget(e.target.value === "" ? null : Number(e.target.value))}
                    className="input input-border bg-transparent w-fit"
                />円ほどです。
            </p>
            <p>
                もしよろしければ、その日でおすすめをお教えいただけますと幸いです。
                お忙しいところ恐れ入りますが、どうぞよろしくお願いいたします。
            </p>
            <p className="mt-12 text-right not-prose:text-sm not-prose:tracking-widest">
                {userName} より
            </p>
        </article>
    );
}

interface CalendarPickerProps {
    id: string;
    date: Date | null;
    setDate: (date: Date) => void;
}

function CalendarPicker({ id, date, setDate }: CalendarPickerProps) {
    const popoverId = `rdp-popover-${id}`;
    const anchorName = `--rdp-${id}`;

    return (
        <span className="relative inline-block align-baseline">
            <button
                type="button"
                popoverTarget={popoverId}
                className="input input-border w-fit bg-transparent font-semibold"
                style={{ anchorName } as React.CSSProperties}
            >
                {date ? date.toLocaleDateString() : "日付を選んでください"}
            </button>
            <div
                popover="auto"
                id={popoverId}
                className="dropdown z-50 bg-base-100 p-2 shadow-lg rounded-box"
                style={{ positionAnchor: anchorName } as React.CSSProperties}
            >
                <DayPicker
                    className="react-day-picker"
                    mode="single"
                    selected={date ?? undefined}
                    onSelect={(selected) => {
                        if (selected) setDate(selected);
                    }}
                />
            </div>
        </span>
    );
}