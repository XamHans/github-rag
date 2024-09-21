import { auth } from "@/auth";
import { db } from "@/lib/db";
import { users } from "@/modules/user/schema";
import { GithubGlobe } from "../components/github-globe";
import RAGStatus from "../components/rag-status";
import { UserCard } from "../components/user-card";

const ConnectingAnimation = () => (
  <div className="absolute left-1/2 -translate-x-1/2 w-[65vw] h-full flex items-center justify-center pointer-events-none z-0">
    <svg
      width="100%"
      height="4"
      viewBox="0 0 100 4"
      preserveAspectRatio="none"
      className="text-blue-500"
    >
      <line
        x1="0"
        y1="2"
        x2="100"
        y2="2"
        stroke="currentColor"
        strokeWidth="4"
        strokeDasharray="10,10"
        className="animate-flow"
      />
      <circle
        cx="0"
        cy="2"
        r="4"
        fill="currentColor"
        className="animate-pulse"
      />
      <circle
        cx="100"
        cy="2"
        r="4"
        fill="currentColor"
        className="animate-pulse"
      />
    </svg>
  </div>
);

export default async function SignInSuccess() {
  const session = await auth();
  console.log(session);
  let user = session?.user;

  //@TODO: Need to fix why session is still null, workaround for hackathon is to get first user from db
  if (!user) {
    // Fetch the first user from the database if no user is authenticated
    const firstUser = await db.select().from(users).limit(1);
    user = firstUser[0] || null;
  }
  return (
    <div className="min-h-screen p-8 sm:p-20 font-[family-name:var(--font-geist-sans)] flex flex-col">
      <h1 className="text-4xl font-bold mb-8 text-center">
        Hi {user ? user.name : "there"}! Let's get started.
      </h1>

      <div className="flex-grow flex flex-col md:flex-row gap-8 items-center justify-center relative overflow-hidden">
        <ConnectingAnimation />

        <div className="flex-1 flex flex-col justify-center z-10 max-w-xs  bg-opacity-80">
          {user && <UserCard user={user} />}
        </div>

        <div className="flex-1 flex justify-center items-center z-20">
          <GithubGlobe />
        </div>

        <div className="flex-1 flex flex-col justify-center z-10 max-w-xs  bg-opacity-80">
          <RAGStatus />
        </div>
      </div>
    </div>
  );
}
