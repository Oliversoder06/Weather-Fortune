import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Weather Fortune",
  description: "Get your daily weather forecast using AI predictions.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
