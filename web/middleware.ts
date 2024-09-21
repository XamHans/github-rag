import NextAuth from "next-auth"
import authConfig from "./auth.config"

// Use only one of the two middleware options below
// 1. Use middleware directly
export const { auth: middleware } = NextAuth(authConfig)

