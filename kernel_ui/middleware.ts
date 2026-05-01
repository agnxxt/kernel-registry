import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // 1. Skip if already on setup or static assets
  if (pathname.startsWith('/setup') || pathname.startsWith('/_next') || pathname.includes('api')) {
    return NextResponse.next()
  }

  try {
    // 2. Check if kernel is initialized
    const apiUrl = 'http://kernel-api:8000';
    const res = await fetch(apiUrl + "/api/v1/setup/status", { next: { revalidate: 0 } });
    const { initialized } = await res.json();

    if (!initialized) {
      return NextResponse.redirect(new URL('/setup', request.url))
    }
  } catch (e) {
    console.error("Middleware setup check failed", e);
  }

  return NextResponse.next()
}
