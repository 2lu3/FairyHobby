

type ContainerProps = {
    children: React.ReactNode;
    className?: string;
}

export  default function Container({ children, className }: ContainerProps) {
    return (
        <div className={`mx-auto w-full max-w-5xl p-16 ${className}`}>
            {children}
        </div>
    )
}
