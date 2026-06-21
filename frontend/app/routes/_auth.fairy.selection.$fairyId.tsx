import { redirect } from "react-router";
import type { Route } from "./+types/_auth.fairy.selection.$fairyId";

export function loader({ request, params }: Route.LoaderArgs) {
    const { fairyId } = params;
    const url = new URL(request.url);

    const latitude = url.searchParams.get("latitude");
    const longitude = url.searchParams.get("longitude");
    const date = url.searchParams.get("date");
    const budget = url.searchParams.get("budget");

    if (!latitude || !longitude || !date || !budget) {
        return redirect(`/fairy/invitation/${fairyId}`);
    }

    return {
        fairyId,
        latitude: Number(latitude),
        longitude: Number(longitude),
        date,
        budget: Number(budget),
    };
}

export default function FairySelection({ loaderData }: Route.ComponentProps) {
    const { latitude, longitude, date, budget } = loaderData;

    return (
        <div className="p-8">
            <h1 className="text-xl font-semibold">プランを選ぶ</h1>
            <dl className="mt-4 space-y-2 text-sm">
                <div><dt className="inline font-medium">緯度: </dt><dd className="inline">{latitude}</dd></div>
                <div><dt className="inline font-medium">経度: </dt><dd className="inline">{longitude}</dd></div>
                <div><dt className="inline font-medium">日付: </dt><dd className="inline">{date}</dd></div>
                <div><dt className="inline font-medium">予算: </dt><dd className="inline">{budget}円</dd></div>
            </dl>
        </div>
    );
}
