import { useNavigate } from "react-router";

import Container from "~/component/Container";
import type { Route } from "./+types/_auth._index";

export const meta: Route.MetaFunction = () => [
    { title: "妖精からの招待状" },
];

export default function Home() {
    const navigate = useNavigate();

    return (
        <Container className="flex-1">
            <div className="flex flex-col items-center gap-6">
                <button
                    type="button"
                    className="btn btn-primary btn-lg w-full max-w-md"
                    onClick={() => navigate("/fairy")}
                >
                    体験を購入する
                </button>
                <button
                    type="button"
                    className="btn btn-secondary btn-lg w-full max-w-md"
                    onClick={() => navigate("/activity")}
                >
                    体験をシェアする
                </button>
            </div>
        </Container>
    );
}
