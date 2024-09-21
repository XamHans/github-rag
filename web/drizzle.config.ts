import type { Config } from "drizzle-kit";

export default {
    schema: "./modules/user/schema.ts",
    out: "./migrations",
    dialect: "postgresql", // New required field
    dbCredentials: {
        connectionString: process.env.DATABASE_URL!,
    },
} satisfies Config;