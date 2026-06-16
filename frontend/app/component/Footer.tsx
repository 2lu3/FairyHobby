import { NavLink } from "react-router";
import Container from "./Container";

export default function Footer() {
    return (
        <footer className="bg-base-200 text-base-content p-12 text-sm">
            <Container className="flex justify-end gap-24">
                <nav className="flex flex-col items-end gap-4">
                    <NavLink className="link link-hover" to="/home" end>ホーム</NavLink>
                    <NavLink className="link link-hover" to="/usage">使い方</NavLink>
                    <NavLink className="link link-hover" to="/help">Q&A</NavLink>
                </nav>
                <nav className="flex flex-col items-end gap-4">
                        <NavLink className="link link-hover" to="/license">ライセンス</NavLink>
                    <NavLink className="link link-hover" to="/privacy">プライバシーポリシー</NavLink>
                    <NavLink className="link link-hover" to="/terms">利用規約</NavLink>
                </nav>
            </Container>

        </footer>
    )
}