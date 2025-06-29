'use client'

import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Search, Filter, ExternalLink } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'

export default function TrendsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [minScore, setMinScore] = useState(0)

  const { data: trends, isLoading } = useQuery({
    queryKey: ['trends', searchTerm, categoryFilter, minScore],
    queryFn: async () => {
      const params = new URLSearchParams({
        size: '50',
        ...(categoryFilter && { category: categoryFilter }),
        ...(minScore > 0 && { min_score: minScore.toString() })
      })
      
      const response = await fetch(`/api/trends?${params}`)
      if (!response.ok) throw new Error('Failed to fetch trends')
      return response.json()
    },
  })

  const filteredTrends = trends?.filter((trend: any) => 
    trend.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    trend.description?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const categories = [...new Set(trends?.map((t: any) => t.category).filter(Boolean))] || []

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
            <TrendingUp className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold text-foreground">Trending Topics</h1>
          </div>
          <p className="text-muted-foreground text-lg">
            Discover the latest trends and their PR potential
          </p>
        </div>

        {/* Filters */}
        <div className="bg-card border rounded-lg p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search trends..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-md bg-background"
                />
              </div>
            </div>

            {/* Category Filter */}
            <div className="lg:w-48">
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full px-3 py-2 border rounded-md bg-background"
              >
                <option value="">All Categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Score Filter */}
            <div className="lg:w-48">
              <select
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                className="w-full px-3 py-2 border rounded-md bg-background"
              >
                <option value={0}>All Scores</option>
                <option value={0.3}>Score ≥ 30%</option>
                <option value={0.5}>Score ≥ 50%</option>
                <option value={0.7}>Score ≥ 70%</option>
              </select>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-3 mb-8">
          <div className="bg-card border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Total Trends</p>
            <p className="text-2xl font-bold text-foreground">{trends?.length || 0}</p>
          </div>
          <div className="bg-card border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Showing</p>
            <p className="text-2xl font-bold text-foreground">{filteredTrends.length}</p>
          </div>
          <div className="bg-card border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Avg Score</p>
            <p className="text-2xl font-bold text-foreground">
              {filteredTrends.length > 0 
                ? Math.round((filteredTrends.reduce((sum: number, t: any) => sum + t.score, 0) / filteredTrends.length) * 100) 
                : 0}%
            </p>
          </div>
        </div>

        {/* Trends Grid */}
        <div className="space-y-4">
          {filteredTrends.map((trend: any) => (
            <Link key={trend.id} href={`/trends/${trend.id}`}>
              <div className="bg-card border rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-foreground mb-2 hover:text-primary">
                      {trend.title}
                    </h3>
                    {trend.description && (
                      <p className="text-muted-foreground mb-3 line-clamp-2">
                        {trend.description}
                      </p>
                    )}
                  </div>
                  <div className="text-right ml-4">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-2xl font-bold text-primary">
                        {Math.round(trend.score * 100)}%
                      </span>
                      {trend.is_rising && <TrendingUp className="h-4 w-4 text-green-500" />}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {trend.sustainability_score >= 0.7 ? 'Sustainable' : 'Short-term'}
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  {trend.category && (
                    <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                      {trend.category}
                    </span>
                  )}
                  {trend.platforms?.map((platform: string) => (
                    <span key={platform} className="px-2 py-1 bg-muted text-muted-foreground text-xs rounded-full">
                      {platform}
                    </span>
                  ))}
                </div>

                <div className="flex justify-between items-center text-sm text-muted-foreground">
                  <div className="flex gap-4">
                    <span>Volume: {trend.volume?.toLocaleString() || 0}</span>
                    <span>Velocity: {Math.round((trend.velocity || 0) * 100)}%</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span>View Details</span>
                    <ExternalLink className="h-3 w-3" />
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {filteredTrends.length === 0 && (
          <div className="text-center py-12">
            <TrendingUp className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">No trends found</h3>
            <p className="text-muted-foreground">
              Try adjusting your search terms or filters
            </p>
          </div>
        )}
      </div>
    </div>
  )
} 