import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sign In",
  robots: { index: false, follow: false },
};

export default function LoginPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-center">Sign in</h1>
      <p className="text-muted-foreground text-center">
        Sign in to your Computare account.
      </p>
    </div>
  );
}
