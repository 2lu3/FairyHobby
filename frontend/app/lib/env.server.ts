import { z } from 'zod';

const schema = z.object({
    BACKEND_URL: z.string(),
});

export function init() {
    const parsed = schema.safeParse(process.env);
    if (parsed.success === false) {
        console.error(
            '❌ invalid environment variables:',
            parsed.error.flatten().fieldErrors,
        );
        throw new Error('Invalid environment variables');
    }
}



declare global { 
    namespace NodeJS {
        interface ProcessEnv extends z.infer<typeof schema> {}
    }
}


export function getEnv() {
    // client side に渡して良い情報のみを書く
    return {

    }
}