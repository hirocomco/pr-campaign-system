'use client'

import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Zap, BarChart3, Users } from 'lucide-react'

export default function Dashboard() {
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await fetch('/api/analytics/dashboard')
      if (!response.ok) throw new Error('Failed to fetch dashboard data')
      return response.json()
    },
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-muted rounded w-1/3"></div>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-muted rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            PR Campaign Ideation System
          </h1>
          <p className="text-muted-foreground text-lg">
            AI-powered daily trend analysis and campaign generation
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="bg-card border rounded-lg p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-primary" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Active Trends</p>
                <p className="text-2xl font-bold text-foreground">
                  {dashboardData?.trends?.active || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-card border rounded-lg p-6">
            <div className="flex items-center">
              <Zap className="h-8 w-8 text-primary" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Total Campaigns</p>
                <p className="text-2xl font-bold text-foreground">
                  {dashboardData?.campaigns?.total || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-card border rounded-lg p-6">
            <div className="flex items-center">
              <BarChart3 className="h-8 w-8 text-primary" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Avg Trend Score</p>
                <p className="text-2xl font-bold text-foreground">
                  {dashboardData?.trends?.average_score || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-card border rounded-lg p-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-primary" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Featured</p>
                <p className="text-2xl font-bold text-foreground">
                  {dashboardData?.campaigns?.featured || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Trends */}
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-foreground mb-4">Top Trends</h2>
            <div className="space-y-4">
              {dashboardData?.trends?.top_trends?.slice(0, 5).map((trend: any) => (
                <div key={trend.id} className="flex items-center justify-between p-3 bg-muted/50 rounded">
                  <div>
                    <p className="font-medium text-foreground">{trend.title}</p>
                    <p className="text-sm text-muted-foreground">{trend.category}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-primary">{(trend.score * 100).toFixed(0)}%</p>
                    <p className="text-xs text-muted-foreground">
                      {trend.platforms?.join(', ')}
                    </p>
                  </div>
                </div>
              )) || (
                <p className="text-muted-foreground">No trends available</p>
              )}
            </div>
          </div>

          <div className="bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-foreground mb-4">Recent Campaigns</h2>
            <div className="space-y-4">
              {dashboardData?.campaigns?.recent_campaigns?.slice(0, 5).map((campaign: any) => (
                <div key={campaign.id} className="flex items-center justify-between p-3 bg-muted/50 rounded">
                  <div>
                    <p className="font-medium text-foreground">{campaign.title}</p>
                    <p className="text-sm text-muted-foreground">{campaign.campaign_type}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-primary">
                      {(campaign.potential_score * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              )) || (
                <p className="text-muted-foreground">No campaigns available</p>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 flex gap-4">
          <button className="bg-primary text-primary-foreground px-6 py-3 rounded-lg font-medium hover:bg-primary/90 transition-colors">
            View All Trends
          </button>
          <button className="bg-secondary text-secondary-foreground px-6 py-3 rounded-lg font-medium hover:bg-secondary/90 transition-colors">
            Browse Campaigns
          </button>
          <button className="border border-border text-foreground px-6 py-3 rounded-lg font-medium hover:bg-muted transition-colors">
            Analytics
          </button>
        </div>
      </div>
    </div>
  )
} 