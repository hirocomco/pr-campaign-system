// Core API types matching backend schemas

export interface Trend {
  id: string
  title: string
  description: string
  source: string
  platforms: string[]
  score: number
  pr_potential_score?: number
  viral_potential_score?: number
  brand_safety_score?: number
  sustainability_score?: number
  estimated_reach: number
  keywords: string[]
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface TrendSummary {
  id: string
  title: string
  source: string
  score: number
  platforms: string[]
  estimated_reach: number
  created_at: string
}

export interface Campaign {
  id: string
  trend_id: string
  title: string
  description: string
  campaign_type: CampaignType
  status: CampaignStatus
  target_industries: string[]
  estimated_reach: number
  execution_difficulty: DifficultyLevel
  viral_potential_score: number
  timeliness_score: number
  originality_score: number
  feasibility_score: number
  overall_score: number
  execution_requirements: ExecutionRequirements
  brand_considerations: BrandConsiderations
  content_suggestions: string[]
  angles: CampaignAngle[]
  views_count: number
  downloads_count: number
  created_at: string
  updated_at: string
}

export interface CampaignSummary {
  id: string
  title: string
  campaign_type: CampaignType
  status: CampaignStatus
  overall_score: number
  estimated_reach: number
  execution_difficulty: DifficultyLevel
  angles_count: number
  created_at: string
}

export interface CampaignAngle {
  id: string
  campaign_id: string
  title: string
  description: string
  target_audience: string
  key_message: string
  supporting_data?: string
  quality_score: number
  estimated_reach: number
  effort_required: DifficultyLevel
  timeline_days: number
  created_at: string
  updated_at: string
}

export interface ExecutionRequirements {
  budget_range: string
  team_size: number
  skills_required: string[]
  tools_needed: string[]
  timeline_weeks: number
}

export interface BrandConsiderations {
  brand_safety_score: number
  risk_factors: string[]
  alignment_score: number
  content_guidelines: string[]
}

// Enums
export enum CampaignType {
  REACTIVE = "reactive",
  PROACTIVE = "proactive",
  SEASONAL = "seasonal",
  NEWS_JACKING = "news_jacking",
  THOUGHT_LEADERSHIP = "thought_leadership"
}

export enum CampaignStatus {
  DRAFT = "draft",
  READY = "ready",
  ACTIVE = "active",
  COMPLETED = "completed",
  ARCHIVED = "archived"
}

export enum DifficultyLevel {
  EASY = "easy",
  MEDIUM = "medium",
  HARD = "hard",
  EXPERT = "expert"
}

// API Response types
export interface TrendListResponse {
  trends: TrendSummary[]
  total: number
  page: number
  size: number
  has_next: boolean
  has_previous: boolean
}

export interface CampaignListResponse {
  campaigns: CampaignSummary[]
  total: number
  page: number
  size: number
  has_next: boolean
  has_previous: boolean
}

// Analytics types
export interface TrendStats {
  total_trends: number
  by_source: Record<string, number>
  by_platform: Record<string, number>
  average_score: number
  score_distribution: Record<string, number>
  top_performing: TrendSummary[]
}

export interface CampaignStats {
  total_campaigns: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  by_difficulty: Record<string, number>
  average_score: number
  top_performing: CampaignSummary[]
}

export interface DashboardMetrics {
  trends_today: number
  campaigns_generated: number
  avg_trend_score: number
  avg_campaign_score: number
  trending_platforms: string[]
  top_industries: string[]
  growth_metrics: {
    trends_growth: number
    campaigns_growth: number
    engagement_growth: number
  }
}

// Filter and search types
export interface TrendFilters {
  source?: string
  platforms?: string[]
  min_score?: number
  max_score?: number
  date_range?: {
    start: string
    end: string
  }
  keywords?: string[]
}

export interface CampaignFilters {
  campaign_type?: CampaignType
  status?: CampaignStatus
  difficulty?: DifficultyLevel
  min_score?: number
  max_score?: number
  industries?: string[]
  date_range?: {
    start: string
    end: string
  }
}

// UI state types
export interface LoadingState {
  isLoading: boolean
  error?: string
}

export interface PaginationState {
  page: number
  size: number
  total: number
}

export interface SortState {
  field: string
  direction: 'asc' | 'desc'
}

// Form types
export interface TrendCreateForm {
  title: string
  description: string
  source: string
  platforms: string[]
  keywords: string[]
}

export interface CampaignCreateForm {
  trend_id: string
  title: string
  description: string
  campaign_type: CampaignType
  target_industries: string[]
}

// Hook return types
export interface UseTrendsReturn {
  trends: Trend[]
  loading: boolean
  error?: string
  refetch: () => void
  hasNextPage: boolean
  hasPreviousPage: boolean
  nextPage: () => void
  previousPage: () => void
}

export interface UseCampaignsReturn {
  campaigns: Campaign[]
  loading: boolean
  error?: string
  refetch: () => void
  hasNextPage: boolean
  hasPreviousPage: boolean
  nextPage: () => void
  previousPage: () => void
}

// Component prop types
export interface TrendCardProps {
  trend: Trend | TrendSummary
  onView?: (trend: Trend | TrendSummary) => void
  onGenerateCampaign?: (trend: Trend | TrendSummary) => void
  compact?: boolean
}

export interface CampaignCardProps {
  campaign: Campaign | CampaignSummary
  onView?: (campaign: Campaign | CampaignSummary) => void
  onEdit?: (campaign: Campaign | CampaignSummary) => void
  onDelete?: (campaign: Campaign | CampaignSummary) => void
  compact?: boolean
}

export interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon?: any
  loading?: boolean
}

// Error types
export interface ApiError {
  message: string
  code?: number
  details?: Record<string, any>
}

// Configuration types
export interface AppConfig {
  apiUrl: string
  refreshInterval: number
  pageSize: number
  maxRetries: number
}

// Search and filter types
export interface SearchResult<T> {
  items: T[]
  total: number
  query: string
  filters?: Record<string, any>
}

export interface AutocompleteOption {
  value: string
  label: string
  category?: string
}

// Theme and UI types
export interface ThemeConfig {
  mode: 'light' | 'dark' | 'system'
  primaryColor: string
  fontFamily: string
} 