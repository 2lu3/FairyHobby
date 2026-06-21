import { Ellipsis, House, LogOut, NotebookPen, SettingsIcon, User } from "lucide-react"
import { Form, NavLink, useLocation, useNavigate } from "react-router"

export default function SettingsButton() {
    const location = useLocation();
    const isHome = location.pathname === "/";
    const navigate = useNavigate();

    return (
        <div className="flex gap-2 items-center border-base-200 border-1 rounded-full bg-base-100">
            <details className="dropdown dropdown-top">
                <summary
                    className="btn btn-circle btn-ghost size-16 min-h-16 p-0"
                    aria-label="メニューを開く"
                >
                    <Ellipsis className="pointer-events-none" />
                </summary>
                <ul className="menu dropdown-content bg-base-100 rounded-box z-1 w-52 p-2 shadow-sm gap-4">
                    <li><NavLink to="/mypage"><User />自分のページへ</NavLink></li>
                    <li><NavLink to="/records"><NotebookPen />記録を見る</NavLink></li>
                    <li><NavLink to="/settings"><SettingsIcon />設定</NavLink></li>
                    <li>
                        <Form method="post" action="/logout" className="w-full">
                            <button type="submit" className="w-full flex items-center gap-2"><LogOut />ログアウト</button>
                        </Form>
                    </li>
                </ul>
            </details>
            {!isHome && (
                <button
                    type="button"
                    aria-label="ホームに戻る"
                    className="btn btn-circle btn-ghost size-16 min-h-16 p-0"
                    onClick={() => { navigate("/"); }}
                >
                    <House className="pointer-events-none" />
                </button>
            )}
        </div>
    )
}
