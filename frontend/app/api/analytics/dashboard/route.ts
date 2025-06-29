import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://prcs_backend:8000'

export async function GET() {
  try {
    // Fetch data from backend APIs in parallel
    const [trendsResponse, campaignsResponse, summaryResponse] = await Promise.all([
      fetch(`${BACKEND_URL}/api/v1/trends/?size=10`),
      fetch(`${BACKEND_URL}/api/v1/campaigns/?size=10`),
      fetch(`${BACKEND_URL}/api/v1/trends/stats/summary`)
    ])

    if (!trendsResponse.ok || !campaignsResponse.ok || !summaryResponse.ok) {
      throw new Error('Failed to fetch data from backend')
    }

    const [trends, campaigns, summary] = await Promise.all([
      trendsResponse.json(),
      campaignsResponse.json(),
      summaryResponse.json()
    ])

    // Structure dashboard data
    const dashboardData = {
      trends: {
        active: summary.active_trends || 0,
        total: summary.total_trends || 0,
        average_score: summary.average_score || 0,
        top_trends: trends || []
      },
      campaigns: {
        total: campaigns?.length || 0,
        featured: campaigns?.filter((c: any) => c.potential_score > 0.7)?.length || 0,
        recent_campaigns: campaigns || []
      },
      summary
    }

    return NextResponse.json(dashboardData)
  } catch (error) {
    console.error('Dashboard API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch dashboard data' },
      { status: 500 }
    )
  }
} 