import "./globals.css";
export const metadata = { title: "Signal Detector", description: "Customer operations risk signals" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
