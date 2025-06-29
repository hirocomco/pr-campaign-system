'use client'

import { useQuery } from '@tanstack/react-query'
import { Zap, Search, ExternalLink } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'

export default function CampaignsPage() {
  const [searchTerm, setSearchTerm] = useState('')

  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: async () => {
      const response = await fetch('/api/campaigns?size=20')
      if (!response.ok) throw new Error('Failed to fetch campaigns')
      return response.json()
    },
  })

  const filteredCampaigns = campaigns?.filter((campaign: any) => 
    campaign.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    campaign.headline?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-muted rounded w-1/4"></div>
            <div className="h-12 bg-muted rounded"></div>
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-32 bg-muted rounded-lg"></div>
            ))}
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
          <div className="flex items-center gap-3 mb-4">
            <Zap className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold text-foreground">Campaign Ideas</h1>
          </div>
          <p className="text-muted-foreground text-lg">
            AI-generated campaign concepts ready for execution
          </p>
        </div>

        {/* Search */}
        <div className="bg-card border rounded-lg p-6 mb-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search campaigns..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-md bg-background"
            />
          </div>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <div className="bg-card border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Total Campaigns</p>
            <p className="text-2xl font-bold text-foreground">{campaigns?.length || 0}</p>
          </div>
          <div className="bg-card border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Showing</p>
            <p className="text-2xl font-bold text-foreground">{filteredCampaigns.length}</p>
          </div>
          <div className="bg-card border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Avg Score</p>
            <p className="text-2xl font-bold text-foreground">
              {filteredCampaigns.length > 0 
                ? Math.round((filteredCampaigns.reduce((sum: number, c: any) => sum + (c.potential_score || 0), 0) / filteredCampaigns.length) * 100) 
                : 0}%
            </p>
          </div>
        </div>

        {/* Campaigns Grid */}
        <div className="space-y-4">
          {filteredCampaigns.map((campaign: any) => (
            <div key={campaign.id} className="bg-card border rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-foreground mb-2">
                    {campaign.title}
                  </h3>
                  <p className="text-muted-foreground mb-3">
                    {campaign.headline}
                  </p>
                  {campaign.brief && (
                    <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                      {campaign.brief}
                    </p>
                  )}
                </div>
                <div className="text-right ml-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-2xl font-bold text-primary">
                      {Math.round((campaign.potential_score || 0) * 100)}%
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Potential Score
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                  {campaign.campaign_type}
                </span>
                <span className="px-2 py-1 bg-muted text-muted-foreground text-xs rounded-full">
                  {campaign.execution_timeline}
                </span>
                <span className="px-2 py-1 bg-muted text-muted-foreground text-xs rounded-full">
                  {campaign.difficulty_level}
                </span>
              </div>

              <div className="flex justify-between items-center text-sm text-muted-foreground">
                <div className="flex gap-4">
                  <span>Audience: {campaign.target_audience}</span>
                  <span>Budget: {campaign.budget_range}</span>
                </div>
                <div className="text-xs">
                  {new Date(campaign.created_at).toLocaleDateString()}
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredCampaigns.length === 0 && (
          <div className="text-center py-12">
            <Zap className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">No campaigns found</h3>
            <p className="text-muted-foreground">
              Try adjusting your search terms
            </p>
          </div>
        )}
      </div>
    </div>
  )
} 