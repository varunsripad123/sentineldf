'use client';

import { useUser } from "@clerk/nextjs";
import { redirect } from "next/navigation";
import DashboardContent from "../../components/dashboard-content";

export default function DashboardPage() {
  const { isLoaded, isSignedIn, user } = useUser();
  
  // Show loading state
  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }
  
  // Redirect to sign-in if not authenticated
  if (!isSignedIn) {
    redirect('/sign-in');
  }
  
  // Serialize user data to pass to Client Component
  const userData = {
    id: user.id,
    firstName: user.firstName,
    lastName: user.lastName,
    emailAddresses: user.emailAddresses?.map((email: any) => ({
      emailAddress: email.emailAddress,
      id: email.id,
    })),
    imageUrl: user.imageUrl,
  };
  
  return (
    <div className="min-h-screen bg-slate-950">
      <DashboardContent user={userData} />
    </div>
  );
}
