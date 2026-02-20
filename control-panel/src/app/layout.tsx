import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "@/components/providers";

export const metadata: Metadata = {
  title: "Infinity X One — Template Control Panel",
  description: "Compose and deploy production AI systems in under one hour",
  applicationName: "InfinityX Control Panel",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, statusBarStyle: "black-translucent", title: "InfinityX" },
};

export const viewport: Viewport = {
  themeColor: "#6366f1",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body className="min-h-screen bg-gray-950 text-gray-50 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
