interface FairyCardProps {
    image_url: string;
    name: string;
    description: string;
    onClick: () => void;
}

export default function FairyCard({ image_url, name, description, onClick }: FairyCardProps) {
    return (
        <div className="card sm:card-side bg-base-100 shadow-sm">
            <figure>
                <img
                    src={image_url}
                    alt={`妖精 ${name}`}
                    className="w-full h-full object-contain" />
            </figure>
            <div className="card-body">
                <h2 className="card-title">{name}</h2>
                <p>{description}</p>
                <div className="card-actions justify-end">
                    <button className="btn btn-primary" onClick={onClick}>招待状を受け取る</button>
                </div>
            </div>
        </div>
    )
}