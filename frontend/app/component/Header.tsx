interface HeaderProps {
    name: string;
    icon: string;
    className?: string;
}

export default function Header( { name, icon, className }: HeaderProps ) {
    return (
        <header className={`navbar bg-base-100 ${className}`}>
            <div className="flex-1 flex items-center gap-4">
                <img src={`data:image/svg+xml;utf8,${encodeURIComponent(icon)}`} alt={name} className="w-10 h-10" />
                <h1>{name}</h1>
            </div>
            <div className="flex-none">
                <ul className="menu menu-horizontal px-1">
                    <li><a>Link</a></li>
                    <li>
                        <details>
                            <summary>Parent</summary>
                            <ul className="bg-base-100 rounded-t-none p-2">
                                <li><a>Link 1</a></li>
                                <li><a>Link 2</a></li>
                            </ul>
                        </details>
                    </li>
                </ul>
            </div>
        </header>
    )
}