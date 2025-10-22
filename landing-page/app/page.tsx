'use client';

import { useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Hero from '@/components/hero'
import Problem from '@/components/problem'
import Solution from '@/components/solution'
import Features from '@/components/features'
import LiveDemo from '@/components/demo'
import BetaSignup from '@/components/beta-signup'
import Testimonials from '@/components/testimonials'
import CTA from '@/components/cta'
import Footer from '@/components/footer'

export default function Home() {
  const { isSignedIn, isLoaded } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      router.push('/dashboard');
    }
  }, [isLoaded, isSignedIn, router]);

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <Hero />
      <Problem />
      <Solution />
      <Features />
      <LiveDemo />
      <BetaSignup />
      <Testimonials />
      <CTA />
      <Footer />
    </main>
  )
}
