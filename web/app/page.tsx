import { OAuthButtons } from "./(auth)/components/sign-in";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center">
      <main className="flex flex-col items-center gap-8 max-w-2xl">
        <h1 className="text-4xl sm:text-6xl font-bold mb-4">
          Finally, Chat with Your Repos
        </h1>
        <p className="text-xl mb-8">
          Explore and interact with your GitHub repositories like never before.
        </p>
        <OAuthButtons />
      </main>
    </div>
  );
}
