import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "@/components/providers";

export const metadata: Metadata = {
  title: "Infinity X One — AI Command Center",
  description: "Production-grade AI system interface powered by Infinity X One Systems",
  applicationName: "InfinityX",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, statusBarStyle: "black-translucent", title: "InfinityX" },
  formatDetection: { telephone: false },
  openGraph: {
    type: "website",
    siteName: "Infinity X One",
    title: "Infinity X One — AI Command Center",
    description: "Production-grade AI system interface",
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#6366f1" },
    { media: "(prefers-color-scheme: dark)", color: "#1e1b4b" },
  ],
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-50 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
