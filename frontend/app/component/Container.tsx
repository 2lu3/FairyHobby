

type ContainerProps = {
    size?: "sm" | "md" | "lg";
    children: React.ReactNode;
}

export  default function Container({ children, size = "md" }: ContainerProps) {
    const sizeClass = {
        sm: "max-w-xl",
        md: "max-w-3xl",
        lg: "max-w-5xl",
    }[size];

    return (
        //<div className={`mx-auto w-full px-4 sm:px-6 lg:px-8 ${sizeClass}`}>
        <div className={`mx-auto w-full ${sizeClass}`}>
            {children}
        </div>
    )
}