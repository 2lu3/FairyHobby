import { redirect } from "react-router";
import type { Route } from "./+types/_auth.fairy.selection.$fairyId";

export function loader({ request, params }: Route.LoaderArgs) {
    const { fairyId } = params;
    const url = new URL(request.url);

    const latitude = url.searchParams.get("latitude");
    const longitude = url.searchParams.get("longitude");
    const startDate = url.searchParams.get("startDate");
    const endDate = url.searchParams.get("endDate");
    const budget = url.searchParams.get("budget");

    if (!latitude || !longitude || !startDate || !endDate || !budget) {
        return redirect(`/fairy/invitation/${fairyId}`);
    }

    return {
        fairyId,
        latitude: Number(latitude),
        longitude: Number(longitude),
        startDate,
        endDate,
        budget: Number(budget),
    };
}

export default function FairySelection({ loaderData }: Route.ComponentProps) {
    const { latitude, longitude, startDate, endDate, budget } = loaderData;

    return (
        <div className="p-8">
            <h1 className="text-xl font-semibold">プランを選ぶ</h1>
            <dl className="mt-4 space-y-2 text-sm">
                <div><dt className="inline font-medium">緯度: </dt><dd className="inline">{latitude}</dd></div>
                <div><dt className="inline font-medium">経度: </dt><dd className="inline">{longitude}</dd></div>
                <div><dt className="inline font-medium">開始日: </dt><dd className="inline">{startDate}</dd></div>
                <div><dt className="inline font-medium">終了日: </dt><dd className="inline">{endDate}</dd></div>
                <div><dt className="inline font-medium">予算: </dt><dd className="inline">{budget}円</dd></div>
            </dl>
        </div>
    );
}
