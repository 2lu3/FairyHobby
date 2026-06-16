interface HeaderProps {
    userName: string;
}

export default function Header( { userName }: HeaderProps ) {
    return (
        <header className="navbar bg-base-100">
            <div className="flex-1">
                <a className="btn btn-ghost text-xl">{userName}</a>
            </div>
            <div className="flex-none">
                <ul className="menu menu-horizontal px-1">
                    <li><a className="text-xl">Link</a></li>
                    <li>
                        <details>
                            <summary className="text-xl">Parent</summary>
                            <ul className="bg-base-100 rounded-t-none p-2">
                                <li><a className="text-xl">Link 1</a></li>
                                <li><a className="text-xl">Link 2</a></li>
                            </ul>
                        </details>
                    </li>
                </ul>
            </div>
        </header>
    )
}