import type { Metadata } from "next";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { LenisProvider } from "@/components/lenis-provider";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"], variable: "--font-space-grotesk", weight: ["400", "500", "600"],
});
const inter = Inter({
  subsets: ["latin"], variable: "--font-inter", weight: ["300", "400", "500"],
});
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"], variable: "--font-jetbrains-mono", weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "Agent Debate · HW2",
  description: "Live scroll-driven debate between Pro and Con, moderated by a Judge.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable}`}>
      <body><LenisProvider>{children}</LenisProvider></body>
    </html>
  );
}
