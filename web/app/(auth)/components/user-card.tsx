import Image from "next/image";

interface User {
  name?: string | null;
  email?: string | null;
  image?: string | null;
}

interface UserCardProps {
  user: User;
}

export function UserCard({ user }: UserCardProps) {
  return (
    <div className="bg-gray-800 shadow-lg rounded-lg p-6 max-w-sm w-full">
      <div className="flex items-center space-x-4">
        {user.image && (
          <Image
            src={user.image}
            alt={user.name || "User"}
            width={64}
            height={64}
            className="rounded-full"
          />
        )}
        <div className="flex justify-center">
          <h2 className="text-2xl mx-auto w-100 font-semibold">
            {user.name || "GitHub User"}
          </h2>
        </div>
      </div>
    </div>
  );
}
