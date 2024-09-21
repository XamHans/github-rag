import 'dotenv/config';
import { drizzle } from "drizzle-orm/node-postgres";
import { migrate } from "drizzle-orm/node-postgres/migrator";
import { Pool } from "pg";


if (!process.env.DATABASE_URL) {
    throw new Error('DATABASE_URL is not set in the environment variables');
}

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
});

const db = drizzle(pool);

async function runMigrations() {
    console.log("Running migrations...");

    await migrate(db, { migrationsFolder: "./migrations" });

    console.log("Migrations completed!");

    await pool.end();
}

runMigrations().catch(console.error);