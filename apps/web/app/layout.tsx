import type { Metadata } from 'next';
import './style.css';
export const metadata: Metadata = { title: 'VoiceSphere AI | Contact Center', description: 'Northstar Retail AI contact center console' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
