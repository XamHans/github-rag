import { cn } from "@/lib/utils";
import { AnimatePresence, motion } from "framer-motion";

const CheckIcon = ({ className }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    strokeWidth={1.5}
    stroke="currentColor"
    className={cn("w-5 h-5", className)}
  >
    <path d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);

const CheckFilled = ({ className }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="currentColor"
    className={cn("w-5 h-5", className)}
  >
    <path
      fillRule="evenodd"
      d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12Zm13.36-1.814a.75.75 0 1 0-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 0 0-1.06 1.06l2.25 2.25a.75.75 0 0 0 1.14-.094l3.75-5.25Z"
      clipRule="evenodd"
    />
  </svg>
);

const LoaderCore = ({ loadingStates, currentStatus }) => (
  <div className="flex flex-col space-y-2">
    {loadingStates.map((loadingState, index) => {
      const isCompleted =
        loadingStates.findIndex((state) => state.status === currentStatus) >
        index;
      const isCurrent = loadingState.status === currentStatus;

      return (
        <motion.div
          key={index}
          className={cn(
            "flex items-center space-x-2 text-sm",
            isCompleted
              ? "text-green-500"
              : isCurrent
              ? "text-blue-500"
              : "text-gray-400"
          )}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          <div>
            {isCompleted ? (
              <CheckFilled className={undefined} />
            ) : (
              <CheckIcon className={undefined} />
            )}
          </div>
          <span className={cn(isCurrent && "font-medium")}>
            {loadingState.text}
          </span>
          {isCurrent && loadingState.currentRepo && (
            <span className="ml-2 font-semibold text-blue-300">
              ({loadingState.currentRepo})
            </span>
          )}
        </motion.div>
      );
    })}
  </div>
);

export const MultiStepLoader = ({
  loadingStates,
  currentStatus,
  isLoading,
  className,
}) => {
  return (
    <AnimatePresence>
      {isLoading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.3 }}
          className={cn(
            "bg-gray-800 rounded-lg shadow-lg p-6",
            "w-full max-w-sm mx-auto",
            className
          )}
        >
          <h3 className="text-lg font-semibold mb-4">Progress</h3>
          <LoaderCore
            loadingStates={loadingStates}
            currentStatus={currentStatus}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
};
