import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Album Finder",
  description: "Your Music.app library, ranked.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-neutral-800">
          <nav className="mx-auto flex max-w-6xl items-center gap-6 px-6 py-4">
            <Link href="/" className="text-lg font-semibold tracking-tight">
              Album Finder
            </Link>
            <Link href="/artists" className="text-sm text-neutral-300 hover:text-white">
              Artists
            </Link>
            <Link href="/tracks" className="text-sm text-neutral-300 hover:text-white">
              Tracks
            </Link>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
