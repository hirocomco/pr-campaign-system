'use client'

import { useQuery } from '@tanstack/react-query'
import { TrendingUp, ArrowLeft, ExternalLink, Calendar, BarChart3, Users, Zap } from 'lucide-react'
import Link from 'next/link'
import { useParams } from 'next/navigation'

export default function TrendDetailPage() {
  const params = useParams()
  const trendId = params.id as string

  const { data: trend, isLoading: trendLoading } = useQuery({
    queryKey: ['trend', trendId],
    queryFn: async () => {
      const response = await fetch(`/api/trends/${trendId}`)
      if (!response.ok) throw new Error('Failed to fetch trend')
      return response.json()
    },
  })

  const { data: campaigns, isLoading: campaignsLoading } = useQuery({
    queryKey: ['campaigns', trendId],
    queryFn: async () => {
      const response = await fetch(`/api/campaigns?trend_id=${trendId}`)
      if (!response.ok) throw new Error('Failed to fetch campaigns')
      return response.json()
    },
  })

  if (trendLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-muted rounded w-1/4"></div>
            <div className="h-12 bg-muted rounded w-3/4"></div>
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2 space-y-6">
                <div className="h-48 bg-muted rounded-lg"></div>
                <div className="h-32 bg-muted rounded-lg"></div>
              </div>
              <div className="h-64 bg-muted rounded-lg"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!trend) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground mb-2">Trend Not Found</h1>
          <p className="text-muted-foreground mb-4">The trend you're looking for doesn't exist.</p>
          <Link href="/trends" className="text-primary hover:underline">
            ← Back to Trends
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/trends" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-4">
            <ArrowLeft className="h-4 w-4" />
            Back to Trends
          </Link>
          
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-foreground mb-4">{trend.title}</h1>
              {trend.description && (
                <p className="text-lg text-muted-foreground mb-4">{trend.description}</p>
              )}
              
              <div className="flex flex-wrap gap-2 mb-4">
                {trend.category && (
                  <span className="px-3 py-1 bg-primary/10 text-primary text-sm rounded-full">
                    {trend.category}
                  </span>
                )}
                {trend.platforms?.map((platform: string) => (
                  <span key={platform} className="px-3 py-1 bg-muted text-muted-foreground text-sm rounded-full">
                    {platform}
                  </span>
                ))}
                {trend.is_sustainable && (
                  <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">
                    Sustainable
                  </span>
                )}
              </div>
            </div>
            
            <div className="text-right ml-6">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-5xl font-bold text-primary">{Math.round(trend.score * 100)}%</span>
                {trend.is_rising && <TrendingUp className="h-6 w-6 text-green-500" />}
              </div>
              <p className="text-muted-foreground">Trend Score</p>
            </div>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Key Metrics */}
            <div className="bg-card border rounded-lg p-6">
              <h2 className="text-xl font-semibold text-foreground mb-4">Key Metrics</h2>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="flex items-center gap-3">
                  <BarChart3 className="h-8 w-8 text-primary" />
                  <div>
                    <p className="text-sm text-muted-foreground">Volume</p>
                    <p className="text-xl font-semibold">{trend.volume?.toLocaleString() || 0}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-8 w-8 text-primary" />
                  <div>
                    <p className="text-sm text-muted-foreground">Velocity</p>
                    <p className="text-xl font-semibold">{Math.round((trend.velocity || 0) * 100)}%</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Users className="h-8 w-8 text-primary" />
                  <div>
                    <p className="text-sm text-muted-foreground">Sustainability</p>
                    <p className="text-xl font-semibold">{Math.round((trend.sustainability_score || 0) * 100)}%</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Calendar className="h-8 w-8 text-primary" />
                  <div>
                    <p className="text-sm text-muted-foreground">Age</p>
                    <p className="text-xl font-semibold">
                      {trend.age_hours ? `${Math.round(trend.age_hours)}h` : 'New'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Keywords */}
            {trend.keywords && trend.keywords.length > 0 && (
              <div className="bg-card border rounded-lg p-6">
                <h2 className="text-xl font-semibold text-foreground mb-4">Related Keywords</h2>
                <div className="flex flex-wrap gap-2">
                  {trend.keywords.map((keyword: string) => (
                    <span key={keyword} className="px-3 py-1 bg-muted text-foreground text-sm rounded-full">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Source URLs */}
            {trend.source_urls && trend.source_urls.length > 0 && (
              <div className="bg-card border rounded-lg p-6">
                <h2 className="text-xl font-semibold text-foreground mb-4">Source Links</h2>
                <div className="space-y-2">
                  {trend.source_urls.slice(0, 5).map((url: string, index: number) => (
                    <a
                      key={index}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-primary hover:underline"
                    >
                      <ExternalLink className="h-4 w-4" />
                      {new URL(url).hostname}
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Campaign Ideas */}
            <div className="bg-card border rounded-lg p-6">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="h-5 w-5 text-primary" />
                <h2 className="text-xl font-semibold text-foreground">Campaign Ideas</h2>
              </div>
              
              {campaignsLoading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-24 bg-muted rounded animate-pulse"></div>
                  ))}
                </div>
              ) : campaigns && campaigns.length > 0 ? (
                <div className="space-y-4">
                  {campaigns.slice(0, 5).map((campaign: any) => (
                    <Link key={campaign.id} href={`/campaigns/${campaign.id}`}>
                      <div className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-semibold text-foreground hover:text-primary">
                            {campaign.title}
                          </h3>
                          <span className="text-sm text-primary font-medium">
                            {Math.round((campaign.potential_score || 0) * 100)}%
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">{campaign.headline}</p>
                        <div className="flex justify-between items-center text-xs text-muted-foreground">
                          <span className="px-2 py-1 bg-muted rounded">
                            {campaign.campaign_type}
                          </span>
                          <span>{campaign.execution_timeline}</span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No campaigns generated yet for this trend.</p>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Trend Status */}
            <div className="bg-card border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Trend Status</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status</span>
                  <span className={`font-medium ${
                    trend.status === 'active' ? 'text-green-600' : 
                    trend.status === 'archived' ? 'text-gray-500' : 'text-red-600'
                  }`}>
                    {trend.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Brand Safe</span>
                  <span className={`font-medium ${
                    trend.is_brand_safe ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {trend.is_brand_safe ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Analyzed</span>
                  <span className={`font-medium ${
                    trend.is_analyzed ? 'text-green-600' : 'text-yellow-600'
                  }`}>
                    {trend.is_analyzed ? 'Yes' : 'Pending'}
                  </span>
                </div>
              </div>
            </div>

            {/* Timestamps */}
            <div className="bg-card border rounded-lg p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Timeline</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-muted-foreground">Created</p>
                  <p className="font-medium">
                    {new Date(trend.created_at).toLocaleString()}
                  </p>
                </div>
                {trend.first_seen_at && (
                  <div>
                    <p className="text-muted-foreground">First Seen</p>
                    <p className="font-medium">
                      {new Date(trend.first_seen_at).toLocaleString()}
                    </p>
                  </div>
                )}
                {trend.analyzed_at && (
                  <div>
                    <p className="text-muted-foreground">Analyzed</p>
                    <p className="font-medium">
                      {new Date(trend.analyzed_at).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 