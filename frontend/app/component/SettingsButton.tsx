import { Ellipsis, LogOut, NotebookPen, SettingsIcon, User } from "lucide-react"
import { useId } from "react"
import { Form, NavLink } from "react-router"

export default function SettingsButton() {
    const id = useId().replace(/:/g, "-");
    const popoverId = `popover-${id}`;
    const anchorName = `--anchor-${id}`;
    return (
        <div>
            <button
                type="button"
                aria-label="メニューを開く"
                className="btn btn-circle size-16 min-h-16 p-0 bg-base-100"
                popoverTarget={popoverId}
                style={{ anchorName: anchorName }}
            >
                <Ellipsis className="pointer-events-none" />
            </button>

            <div className="flex flex-col p-4 gap-4 dropdown bg-base-100 w-56 rounded-box shadow-sm"
                popover="auto" id={popoverId} style={{
                    positionAnchor: anchorName,
                    position: "fixed",
                    inset: "auto",
                    margin: 0,
                    bottom: "anchor(top)",
                    left: "anchor(left)",
                }}>
                <ul className="menu bg-base-100 rounded-box w-full gap-2">
                    <li><NavLink to="/profile"><User />自分のページへ</NavLink></li>
                    <li><NavLink to="/records"><NotebookPen />記録を見る</NavLink></li>
                    <li><NavLink to="/settings"><SettingsIcon />設定</NavLink></li>
                    <li>
                        <Form method="post" action="/logout" className="w-full">
                            <button type="submit" className="w-full flex items-center gap-2"><LogOut />ログアウト</button>
                        </Form>
                    </li>
                </ul>
                <button className="btn join-item bg-base-100 btn-square w-full" popoverTarget={popoverId}>閉じる</button>

            </div>
        </div>
    )
}