'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import {
  Search,
  Eye,
  EyeOff,
  Palette,
  Mountain,
  Grid3X3,
  FlaskConical,
  Square,
  ChevronDown,
  Download,
  X,
  Zap,
  Target,
  Sparkles,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { AnnaGridControlsProps, ViewMode, ColorTheme, AnnaCell } from './types'
import { VIEW_MODE_CONFIG, COLOR_THEMES, QUICK_NAV_PRESETS } from './constants'

const VIEW_MODE_ICONS: Record<ViewMode, React.ReactNode> = {
  heatmap: <Palette className="w-4 h-4" />,
  terrain: <Mountain className="w-4 h-4" />,
  wireframe: <Grid3X3 className="w-4 h-4" />,
  scientific: <FlaskConical className="w-4 h-4" />,
  flat: <Square className="w-4 h-4" />,
}

export function AnnaGridControls({
  viewMode,
  colorTheme,
  showVIPMarkers,
  showSpecialRows,
  stats,
  selectedCell,
  onViewModeChange,
  onColorThemeChange,
  onToggleVIP,
  onToggleSpecialRows,
  onSearch,
  onCellFound,
  onJumpToPreset,
  onExport,
}: AnnaGridControlsProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchError, setSearchError] = useState<string | null>(null)
  const [showViewModeMenu, setShowViewModeMenu] = useState(false)
  const [showColorMenu, setShowColorMenu] = useState(false)
  const [showQuickNav, setShowQuickNav] = useState(false)

  const searchInputRef = useRef<HTMLInputElement>(null)
  const viewModeRef = useRef<HTMLDivElement>(null)
  const colorMenuRef = useRef<HTMLDivElement>(null)
  const quickNavRef = useRef<HTMLDivElement>(null)

  // Close menus on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (viewModeRef.current && !viewModeRef.current.contains(e.target as Node)) {
        setShowViewModeMenu(false)
      }
      if (colorMenuRef.current && !colorMenuRef.current.contains(e.target as Node)) {
        setShowColorMenu(false)
      }
      if (quickNavRef.current && !quickNavRef.current.contains(e.target as Node)) {
        setShowQuickNav(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Search handler
  const handleSearch = useCallback(() => {
    if (!searchQuery.trim()) return

    const found = onSearch(searchQuery)
    if (found) {
      onCellFound(found)
      setSearchError(null)
      setSearchQuery('')
    } else {
      setSearchError('Cell not found. Try: address (0-16383), row,col, or value')
      setTimeout(() => setSearchError(null), 3000)
    }
  }, [searchQuery, onSearch, onCellFound])

  // Keyboard handler for search
  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    } else if (e.key === 'Escape') {
      setSearchQuery('')
      searchInputRef.current?.blur()
    }
  }

  return (
    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/95 to-transparent pt-8 pb-4 px-4 pointer-events-auto">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between gap-4">
          {/* Left: View Mode */}
          <div className="flex items-center gap-2">
            {/* View Mode Selector */}
            <div className="relative" ref={viewModeRef}>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowViewModeMenu(!showViewModeMenu)}
                className="h-9 px-3 gap-2 bg-white/5 border border-white/10 text-white hover:bg-white/10"
              >
                {VIEW_MODE_ICONS[viewMode]}
                <span className="text-xs">{VIEW_MODE_CONFIG[viewMode].name}</span>
                <ChevronDown className="w-3 h-3" />
              </Button>

              {showViewModeMenu && (
                <div className="absolute bottom-full left-0 mb-2 py-1 bg-gray-900 border border-white/10 rounded-lg shadow-xl min-w-[160px] z-50">
                  {(Object.keys(VIEW_MODE_CONFIG) as ViewMode[]).map((mode) => (
                    <button
                      key={mode}
                      onClick={() => {
                        onViewModeChange(mode)
                        setShowViewModeMenu(false)
                      }}
                      className={`w-full px-3 py-2 text-left text-sm flex items-center gap-2 hover:bg-white/10 transition-colors ${
                        mode === viewMode ? 'text-orange-400' : 'text-gray-400'
                      }`}
                    >
                      {VIEW_MODE_ICONS[mode]}
                      <div>
                        <div className="font-medium">{VIEW_MODE_CONFIG[mode].name}</div>
                        <div className="text-[10px] text-gray-500">
                          {VIEW_MODE_CONFIG[mode].description}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Color Theme Selector */}
            <div className="relative" ref={colorMenuRef}>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowColorMenu(!showColorMenu)}
                className="h-9 px-3 gap-2 bg-white/5 border border-white/10 text-white hover:bg-white/10"
              >
                <div className="flex gap-0.5">
                  <div
                    className="w-2 h-4 rounded-l"
                    style={{ backgroundColor: COLOR_THEMES[colorTheme].negative }}
                  />
                  <div
                    className="w-2 h-4"
                    style={{ backgroundColor: COLOR_THEMES[colorTheme].neutral }}
                  />
                  <div
                    className="w-2 h-4 rounded-r"
                    style={{ backgroundColor: COLOR_THEMES[colorTheme].positive }}
                  />
                </div>
                <ChevronDown className="w-3 h-3" />
              </Button>

              {showColorMenu && (
                <div className="absolute bottom-full left-0 mb-2 py-1 bg-gray-900 border border-white/10 rounded-lg shadow-xl min-w-[140px] z-50">
                  {(Object.keys(COLOR_THEMES) as ColorTheme[]).map((theme) => (
                    <button
                      key={theme}
                      onClick={() => {
                        onColorThemeChange(theme)
                        setShowColorMenu(false)
                      }}
                      className={`w-full px-3 py-2 text-left text-sm flex items-center gap-2 hover:bg-white/10 transition-colors ${
                        theme === colorTheme ? 'text-orange-400' : 'text-gray-400'
                      }`}
                    >
                      <div className="flex gap-0.5">
                        <div
                          className="w-2 h-3 rounded-l"
                          style={{ backgroundColor: COLOR_THEMES[theme].negative }}
                        />
                        <div
                          className="w-2 h-3"
                          style={{ backgroundColor: COLOR_THEMES[theme].neutral }}
                        />
                        <div
                          className="w-2 h-3 rounded-r"
                          style={{ backgroundColor: COLOR_THEMES[theme].positive }}
                        />
                      </div>
                      <span>{COLOR_THEMES[theme].name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Toggle VIP Markers */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleVIP}
              className={`h-9 px-3 gap-2 ${
                showVIPMarkers
                  ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                  : 'bg-white/5 border border-white/10 text-gray-500'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span className="text-xs">VIP</span>
            </Button>

            {/* Toggle Special Rows */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleSpecialRows}
              className={`h-9 px-3 gap-2 ${
                showSpecialRows
                  ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                  : 'bg-white/5 border border-white/10 text-gray-500'
              }`}
            >
              {showSpecialRows ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
              <span className="text-xs">Rows</span>
            </Button>
          </div>

          {/* Center: Search */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleSearchKeyDown}
                placeholder="Address (0-16383), row,col, or value..."
                className={`w-full h-9 pl-10 pr-10 bg-white/5 border rounded-lg text-sm text-white placeholder:text-gray-600 focus:outline-none focus:ring-1 transition-colors ${
                  searchError
                    ? 'border-red-500/50 focus:ring-red-500/50'
                    : 'border-white/10 focus:ring-orange-500/50'
                }`}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 hover:bg-white/10 rounded"
                >
                  <X className="w-3.5 h-3.5 text-gray-500" />
                </button>
              )}

              {/* Search error tooltip */}
              {searchError && (
                <div className="absolute left-0 right-0 -top-8 text-center">
                  <span className="text-xs text-red-400 bg-red-500/10 px-2 py-1 rounded">
                    {searchError}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Right: Quick Nav & Stats */}
          <div className="flex items-center gap-2">
            {/* Quick Navigation */}
            <div className="relative" ref={quickNavRef}>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowQuickNav(!showQuickNav)}
                className="h-9 px-3 gap-2 bg-white/5 border border-white/10 text-white hover:bg-white/10"
              >
                <Target className="w-4 h-4" />
                <span className="text-xs">Jump To</span>
                <ChevronDown className="w-3 h-3" />
              </Button>

              {showQuickNav && (
                <div className="absolute bottom-full right-0 mb-2 py-1 bg-gray-900 border border-white/10 rounded-lg shadow-xl min-w-[180px] z-50">
                  {QUICK_NAV_PRESETS.map((preset) => (
                    <button
                      key={preset.id}
                      onClick={() => {
                        onJumpToPreset(preset.id as any)
                        setShowQuickNav(false)
                      }}
                      className="w-full px-3 py-2 text-left text-sm flex items-center gap-2 hover:bg-white/10 transition-colors text-gray-400"
                    >
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: preset.color }}
                      />
                      <div className="flex-1">
                        <div className="font-medium">{preset.label}</div>
                        <div className="text-[10px] text-gray-500">
                          [{preset.row}, {preset.col}] = #{preset.address}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Cell Count */}
            {selectedCell ? (
              <div className="text-xs text-gray-400 bg-white/5 px-3 py-2 rounded-lg border border-white/10">
                <span className="text-white font-mono">[{selectedCell.row}, {selectedCell.col}]</span>
                <span className="mx-2">=</span>
                <span
                  className={`font-bold ${
                    selectedCell.value > 0
                      ? 'text-orange-400'
                      : selectedCell.value < 0
                        ? 'text-blue-400'
                        : 'text-gray-400'
                  }`}
                >
                  {selectedCell.value}
                </span>
              </div>
            ) : (
              <div className="text-xs text-gray-500">
                <span className="text-white font-medium">{stats?.totalCells.toLocaleString()}</span>
                <span> cells</span>
              </div>
            )}

            {/* Export */}
            <Button
              variant="ghost"
              size="icon"
              onClick={onExport}
              className="h-9 w-9 bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10"
            >
              <Download className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
