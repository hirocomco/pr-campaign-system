import { NextResponse, NextRequest } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://prcs_backend:8000'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    
    // Forward query parameters to backend
    const backendUrl = new URL('/api/v1/trends/', BACKEND_URL)
    searchParams.forEach((value, key) => {
      backendUrl.searchParams.set(key, value)
    })

    const response = await fetch(backendUrl.toString())
    
    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Trends API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch trends' },
      { status: 500 }
    )
  }
} 