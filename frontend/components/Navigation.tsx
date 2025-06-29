'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'
import { TrendingUp, Zap, BarChart3, Home } from 'lucide-react'

export function Navigation() {
  const pathname = usePathname()
  const [currentTime, setCurrentTime] = useState('')

  useEffect(() => {
    // Set initial time
    setCurrentTime(new Date().toLocaleTimeString())
    
    // Update time every minute
    const interval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString())
    }, 60000)

    return () => clearInterval(interval)
  }, [])

  const navItems = [
    { href: '/', label: 'Dashboard', icon: Home },
    { href: '/trends', label: 'Trends', icon: TrendingUp },
    { href: '/campaigns', label: 'Campaigns', icon: Zap },
    { href: '/analytics', label: 'Analytics', icon: BarChart3 },
  ]

  return (
    <nav className="bg-card border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <TrendingUp className="h-6 w-6 text-primary" />
            <span className="text-lg font-semibold text-foreground">
              PR Campaign System
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-6">
            {navItems.map(({ href, label, icon: Icon }) => {
              const isActive = pathname === href || (href !== '/' && pathname.startsWith(href))
              
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </Link>
              )
            })}
          </div>

          {/* User Menu (placeholder) */}
          <div className="flex items-center gap-4">
            {currentTime && (
              <div className="text-sm text-muted-foreground">
                Last updated: {currentTime}
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
} 