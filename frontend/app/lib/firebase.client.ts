import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, connectAuthEmulator } from "firebase/auth";

const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const provider = new GoogleAuthProvider();

const useEmulator = import.meta.env.VITE_USE_FIREBASE_EMULATOR === "true";

if (useEmulator) {
    // ローカル: Firebase Auth Emulator に接続する
    const emulatorUrl =
        import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_URL ?? "http://localhost:9099";
    connectAuthEmulator(auth, emulatorUrl, { disableWarnings: true });
} else if (typeof window !== "undefined" && firebaseConfig.measurementId) {
    // 本番のみ Analytics を有効化する (エミュレータ利用時は無効)
    import("firebase/analytics")
        .then(({ getAnalytics }) => getAnalytics(app))
        .catch(() => {
            /* Analytics の初期化失敗は無視する */
        });
}
