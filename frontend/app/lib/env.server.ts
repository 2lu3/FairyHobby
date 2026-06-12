

export const BACKEND_URL = process.env.BACKEND_URL;

if (!BACKEND_URL) {
    throw new Error("BACKEND_URL is not set");
}