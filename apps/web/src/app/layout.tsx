import type { Metadata } from "next";
import { Source_Sans_3, Space_Grotesk } from "next/font/google";

import { SiteHeader } from "@/components/SiteHeader";

import "./globals.css";

const sourceSans = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-sans",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
});

export const metadata: Metadata = {
  title: "JobScope Signal Graph",
  description:
    "Mede quais skills aparecem juntas em vagas de Dados/Analytics (boards públicos Greenhouse/Lever) e compara com evidências reais de portfólio.",
  icons: {
    icon: "/icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className={`${sourceSans.variable} ${spaceGrotesk.variable} font-sans antialiased`}>
        <SiteHeader />
        {children}
        <footer className="border-t border-[var(--line)] py-6 text-center text-xs text-[var(--muted)]">
          Dados públicos de boards Greenhouse/Lever · agregados apenas · amostra não representativa
          do mercado total
        </footer>
      </body>
    </html>
  );
}
