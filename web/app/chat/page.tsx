import { Meteors } from "@/components/ui/meteors";
import ChatWindow from "./components/chat-window";

export default function Home() {
  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen overflow-hidden">
      {/* Top left meteors */}
      <div className="absolute top-0 left-0 w-1/3 h-1/3">
        <Meteors />
      </div>

      {/* Chat window */}
      <div className="z-10 w-full max-w-4xl">
        <ChatWindow />
      </div>

      {/* Bottom right meteors */}
      <div className="absolute bottom-0 right-0 w-1/3 h-1/3">
        <Meteors />
      </div>
    </div>
  );
}
