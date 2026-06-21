import { backendFetch } from "~/lib/fetcher.server";
import type { Route } from "./+types/_auth.fairy.$fairyId";
import Container from "~/component/Container";
import { useState } from "react";
import { DayPicker } from "react-day-picker";
import { Form, useNavigate, useRouteLoaderData } from "react-router";
import type { loader as authLoader } from "./_auth";

type GeoCoordinates = {
    latitude: number;
    longitude: number;
    accuracy: number;
};

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
        latitude: formData.get("latitude"),
        longitude: formData.get("longitude"),
        startDate: formData.get("startDate"),
        endDate: formData.get("endDate"),
        budget: formData.get("budget"),
    }

    const res;
}


export default function Fairy({ loaderData }: Route.ComponentProps) {
    const { user } = useRouteLoaderData("routes/_auth") as Exclude<
        Awaited<ReturnType<typeof authLoader>>,
        Response
    >;
    const navigate = useNavigate();
    const { fairy, description, errorMessage } = loaderData;
    const [userAgreed, setUserAgreed] = useState<boolean>(false);
    const [location, setLocation] = useState<GeoCoordinates | null>(null);
    const [startDate, setStartDate] = useState<Date | null>(null);
    const [endDate, setEndDate] = useState<Date | null>(null);
    const [budget, setBudget] = useState<number | null>(null);
    const [error, setError] = useState<string | null>(errorMessage);

    const canAccept =
        location !== null &&
        startDate !== null &&
        endDate !== null &&
        startDate < endDate &&
        budget !== null;

    const getLocation = () => {
        if (!navigator.geolocation) {
            setError("このブラウザは位置情報に対応していません");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                setLocation({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                });
            },
            (error) => {
                setError(error.message);
            },
            {
                enableHighAccuracy: true,
                timeout: 10_000,
                maximumAge: 0,
            }
        );
    };


    return (
        <div className="min-h-screen flex flex-col items-center justify-center">
            {errorMessage && <div className="alert alert-error">{error}</div>}
            <Container size="sm" className="flex flex-col gap-12">
                <h1 className="text-center text-xl">招待状を受け取りますか？</h1>
                <div className="bg-[url('/paper.jpg')] bg-cover bg-center bg-no-repeat shadow-lg py-8 px-12">
                    {!userAgreed ? <FairyLetter fairyName={fairy.name} userName={user.display_name} />
                        :
                        <UserLetter fairyName={fairy.name} userName={user.display_name} location={location} getLocation={getLocation} startDate={startDate} endDate={endDate} setStartDate={setStartDate} setEndDate={setEndDate} budget={budget} setBudget={setBudget} />}
                </div>
                {userAgreed ? (
                    <Form method="post">
                        <input type="hidden" name="latitude" value={location?.latitude ?? ""} required />
                        <input type="hidden" name="longitude" value={location?.longitude ?? ""} required />
                        <input type="hidden" name="startDate" value={startDate?.toISOString() ?? ""} required />
                        <input type="hidden" name="endDate" value={endDate?.toISOString() ?? ""} required />
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
    location: GeoCoordinates | null;
    getLocation: () => void;
    startDate: Date | null;
    endDate: Date | null;
    setStartDate: (startDate: Date) => void;
    setEndDate: (endDate: Date) => void;
    budget: number | null;
    setBudget: (budget: number | null) => void;
}

function UserLetter({ fairyName, userName, location, getLocation, startDate, endDate, setStartDate, setEndDate, budget, setBudget }: UserLetterProps) {
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
                いま私は、
                {location ? (
                    <>{location.latitude.toFixed(4)}°、{location.longitude.toFixed(4)}°付近におります。</>
                ) : (
                    <button className="btn btn-outline" onClick={getLocation}>現在地を取得する</button>
                )}
            </p>
            <p>
                ご都合をお聞きくださるのでしたら、
                <CalendarPicker id="start" date={startDate} setDate={setStartDate} />
                から
                <CalendarPicker id="end" date={endDate} setDate={setEndDate} />
                のあいだでしたら、いつでも構いません。
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
                もしよろしければ、その範囲でおすすめをお教えいただけますと幸いです。
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