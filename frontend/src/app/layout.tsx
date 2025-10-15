import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "docInfo",
  description: "Local document access system",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
