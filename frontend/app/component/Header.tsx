import { Link } from "react-router";
import Container from "./Container";

interface HeaderProps {
    name: string;
    icon: string;
    className?: string;
}

export default function Header( { name, icon, className }: HeaderProps ) {
    return (
        <header className={`bg-base-100 ${className}`}>
            <Container className="navbar !py-4">
                <div className="flex-1 flex items-center gap-4">
                    <img src={`data:image/svg+xml;utf8,${encodeURIComponent(icon)}`} alt={name} className="w-10 h-10" />
                    <h1>{name}</h1>
                </div>
                <div className="flex-none">
                    <ul className="menu menu-horizontal px-1">
                        <li><Link to="/home">ホーム</Link></li>
                        <li><Link to="/mypage">マイページ</Link></li>
                    </ul>
                </div>
            </Container>
        </header>
    )
}
