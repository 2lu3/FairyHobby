import { LoginWithGoogleButton } from "./LoginWithGoogleButton";


type StartModalProps = {
    handleLoginSubmit: () => void | Promise<void>;
};

export const StartModal = ({ handleLoginSubmit }: StartModalProps) => {
    return (
        <div>
            <button
                className="btn btn-outline btn-neutral"
                onClick={() => {
                    const dialog = document.getElementById("start_modal");
                    if (dialog instanceof HTMLDialogElement) {
                        dialog.showModal();
                    }
                }}
            >
                はじめる
            </button>
            <dialog id="start_modal" className="modal">
                <div className="modal-box flex flex-col justify-center items-center gap-4 mx-auto px-12">
                    <form method="dialog">
                        {/* if there is a button in form, it will close the modal */}
                        <button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
                    </form>
                    <h3 className="font-bold text-lg">妖精からの招待状</h3>
                    <p className="py-4">あなたの毎日が少しだけ楽しくなる、そんな宝物を見つけるための場所です。</p>
                    <LoginWithGoogleButton onClick={() => { void handleLoginSubmit(); }} />
                </div>
                <form method="dialog" className="modal-backdrop">
                    <button/>
                </form>
            </dialog>
        </div>
    );
};