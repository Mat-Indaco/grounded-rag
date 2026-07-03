import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Grounded RAG Assistant",
  description: "RAG con citas verificables y guardrails contra alucinaciones.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
