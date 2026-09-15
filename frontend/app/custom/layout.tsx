import type {
  ReactNode,
} from 'react';

import ConsoleNav from '@/components/ConsoleNav';


interface CustomLayoutProps {
  children: ReactNode;
}


export default function CustomLayout({
  children,
}: CustomLayoutProps) {
  return (
    <>
      <ConsoleNav />
      {children}
    </>
  );
}