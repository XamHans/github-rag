"use client";
import { MultiStepLoader } from "@/components/ui/multi-step-loader";
import { IconSquareRoundedX } from "@tabler/icons-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

export default function RAGStatus() {
  const [isLoading, setIsLoading] = useState(false);
  const [currentRepo, setCurrentRepo] = useState("");
  const [processedCount, setProcessedCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [socket, setSocket] = useState(null);
  const [currentStatus, setCurrentStatus] = useState("IDLE");
  const router = useRouter();
  const loadingStates = [
    { status: "FETCHING_REPOS", text: "Fetching Starred Repos" },
    { status: "PROCESSING", text: "Processing Repositories", currentRepo },
    { status: "COMPLETE", text: "Process Complete" },
  ];

  const connectWebSocket = useCallback(() => {
    const newSocket = new WebSocket("ws://localhost:8000/ws");

    newSocket.onopen = () => {
      console.log("WebSocket connected");
      newSocket.send(JSON.stringify({ github_username: "XamHans" }));
    };

    newSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("received ws event ", data);
      if (data.status === "FETCHING_REPOS") {
        setCurrentStatus("FETCHING_REPOS");
        setIsLoading(true);
      } else if (data.status && data.status.current_repo) {
        setCurrentStatus("PROCESSING");
        setCurrentRepo(data.status.current_repo);
        setProcessedCount(data.status.processed_count);
        setTotalCount(data.status.total_count);
      } else if (data.status === "COMPLETE") {
        setCurrentStatus("COMPLETE");

        setTimeout(() => {
          setIsLoading(false);
          newSocket.close();
          router.push("/chat");
        }, 2500);
      }
    };

    newSocket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    newSocket.onclose = () => {
      console.log("WebSocket disconnected");
    };

    setSocket(newSocket);
  }, []);

  useEffect(() => {
    if (isLoading && !socket) {
      connectWebSocket();
    }

    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [isLoading, socket, connectWebSocket]);

  const startProcess = () => {
    setIsLoading(true);
    setCurrentStatus("IDLE");
    setCurrentRepo("");
    setProcessedCount(0);
    setTotalCount(0);
  };

  const stopProcess = () => {
    if (socket) {
      socket.close();
    }
    setIsLoading(false);
    setCurrentStatus("IDLE");
    setCurrentRepo("");
    setProcessedCount(0);
    setTotalCount(0);
  };

  return (
    <div className="w-full h-[60vh] flex flex-col items-center justify-center">
      <MultiStepLoader
        loadingStates={loadingStates}
        currentStatus={currentStatus}
        isLoading={isLoading}
        className="mb-6"
      />

      {isLoading && currentStatus === "PROCESSING" && (
        <div className="text-center mt-4">
          <p className="text-lg mb-4">
            Progress: {processedCount} / {totalCount}
          </p>
          <div className="w-64 h-4 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-300 ease-in-out"
              style={{
                width: `${
                  totalCount > 0 ? (processedCount / totalCount) * 100 : 0
                }%`,
              }}
            ></div>
          </div>
        </div>
      )}

      {isLoading && currentStatus === "COMPLETE" && (
        <div className="text-center mt-4">
          <p className="text-lg mb-4">We are ready now. Redirecting to chat</p>
        </div>
      )}

      {!isLoading && (
        <button
          onClick={startProcess}
          className="text-white mx-auto text-sm md:text-base transition font-medium duration-200 h-10 rounded-lg px-8 flex items-center justify-center bg-blue-500 hover:bg-blue-600 mt-4"
        >
          Start Processing
        </button>
      )}

      {isLoading && (
        <button
          className="fixed top-4 right-4 text-black dark:text-white z-[120]"
          onClick={stopProcess}
        >
          <IconSquareRoundedX className="h-10 w-10" />
        </button>
      )}
    </div>
  );
}
