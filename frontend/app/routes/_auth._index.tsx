import { useNavigate } from "react-router";

import Container from "~/component/Container";
import { backendFetch } from "~/lib/fetcher.server";
import type { Route } from "./+types/_auth._index";
import type { FairyReadResponse } from "~/types/fairy";
import FairyCard from "~/component/FairyCard";

export const meta: Route.MetaFunction = () => [
    { title: "妖精を選ぶ | 妖精からの招待状" },
];

export async function loader({ request }: Route.LoaderArgs) {
    const res = await backendFetch(request, "/fairies");
    const res_fairies: FairyReadResponse[] = await res.json();
    const fairies = res_fairies.map((fairy) => {
        return {
            ...fairy,
            description: fairy.prompt.split("。")[0] + "。" + fairy.prompt.split("。")[1],
        }
    });
    return { fairies };
}

export default function Home(
    {loaderData}: Route.ComponentProps
) {
    const { fairies } = loaderData;

    const navigate = useNavigate();

    return (
        <Container className="flex-1">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
                {fairies.map((fairy) => (
                    <FairyCard key={fairy.id} image_url={fairy.image_url} name={fairy.name} description={fairy.description} onClick={() => { navigate(`/fairy/invitation/${fairy.id}`); }} />
                ))}
            </div>
        </Container>
    );
}
