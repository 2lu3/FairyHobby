

type ContainerProps = {
    size?: "sm" | "md" | "lg";
    children: React.ReactNode;
    className?: string;
}

export  default function Container({ children, size = "md", className }: ContainerProps) {
    const sizeClass = {
        sm: "max-w-3xl",
        md: "max-w-5xl",
        lg: "max-w-7xl",
    }[size];

    return (
        <div className={`mx-auto w-full p-16 ${sizeClass} ${className}`}>
            {children}
        </div>
    )
}