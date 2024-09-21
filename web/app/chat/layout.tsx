import type { Metadata } from "next";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Chat App",
  description: "Chat with your Github Repositories",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex flex-col min-h-screen">
          <header className="bg-inherit text-primary-foreground py-4">
            <div className="container mx-auto px-4">
              <h1 className="text-2xl font-bold">Chat with Repo's</h1>
            </div>
          </header>
          <main className="flex-grow container mx-auto px-4 py-8">
            {children}
          </main>
          <footer className="bg-muted py-4">
            <div className="container mx-auto px-4 text-center text-sm">
              © 2023 AI Chat App. All rights reserved.
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
