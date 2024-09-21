"use client";

import { Icons } from "@/app/Icons";
import { Button } from "@/components/ui/button";
import { signIn } from "next-auth/react";

export function OAuthButtons(): JSX.Element {
  async function handleOAuthSignIn(provider: "github"): Promise<void> {
    try {
      await signIn(provider, {
        callbackUrl: process.env.NEXT_PUBLIC_REDIRECT_URL,
      });
    } catch (error) {
      console.error(error);
      throw new Error(`Error signing in with ${provider}`);
    }
  }

  return (
    <div className="">
      <Button
        aria-label="Sign in with gitHub"
        variant="outline"
        onClick={() => void handleOAuthSignIn("github")}
        className="w-full sm:w-auto"
      >
        <Icons.gitHub className="mr-2 size-4" />
        GitHub
      </Button>
    </div>
  );
}
