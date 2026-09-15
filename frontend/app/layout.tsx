import type {
  Metadata,
} from "next";

import "./globals.css";

import {
  AuthProvider,
} from "@/components/AuthProvider";

import SiteNavbar from "@/components/SiteNavbar";
import SiteFooter from "@/components/SiteFooter";


export const metadata: Metadata = {
  title: {
    default: "RippleProof",
    template: "%s | RippleProof",
  },

  description:
    "Semantic policy change intelligence with executable proof.",
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <SiteNavbar />

          <main>
            {children}
          </main>

          <SiteFooter />
        </AuthProvider>
      </body>
    </html>
  );
}