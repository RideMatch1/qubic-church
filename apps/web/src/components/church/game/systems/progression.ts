/**
 * Anna Matrix Explorer - Progression System
 * Level, XP, Energy, and stat management
 */

import type { PlayerStats } from '../engine/types'

// ============================================
// XP & LEVELING
// ============================================

/**
 * XP required for each level (1-100)
 * Uses exponential formula: base * (level ^ exponent)
 */
export function getXPForLevel(level: number): number {
  if (level <= 1) return 0
  const base = 100
  const exponent = 1.5
  return Math.floor(base * Math.pow(level - 1, exponent))
}

/**
 * Get total XP needed from level 1 to target level
 */
export function getTotalXPForLevel(level: number): number {
  let total = 0
  for (let i = 1; i <= level; i++) {
    total += getXPForLevel(i)
  }
  return total
}

/**
 * Calculate level from total XP
 */
export function getLevelFromXP(totalXP: number): { level: number; currentXP: number; xpForNextLevel: number } {
  let level = 1
  let remainingXP = totalXP

  while (level < 100) {
    const xpNeeded = getXPForLevel(level + 1)
    if (remainingXP < xpNeeded) {
      break
    }
    remainingXP -= xpNeeded
    level++
  }

  return {
    level,
    currentXP: remainingXP,
    xpForNextLevel: getXPForLevel(level + 1),
  }
}

/**
 * Add XP and calculate level ups
 */
export function addXP(
  currentStats: PlayerStats,
  xpGained: number
): { newStats: PlayerStats; levelsGained: number; statsGained: Partial<PlayerStats> } {
  const totalXP = currentStats.experience + xpGained
  const { level, currentXP, xpForNextLevel } = getLevelFromXP(totalXP)

  const levelsGained = level - currentStats.level

  // Calculate stat gains
  const statsGained = calculateStatGainsForLevels(currentStats.level, level)

  const newStats: PlayerStats = {
    ...currentStats,
    level,
    experience: currentXP,
    experienceToNextLevel: xpForNextLevel,
    maxEnergy: currentStats.maxEnergy + statsGained.maxEnergy!,
    maxHealth: currentStats.maxHealth + statsGained.maxHealth!,
    attackPower: currentStats.attackPower + statsGained.attackPower!,
    defense: currentStats.defense + statsGained.defense!,
    scanPower: currentStats.scanPower + statsGained.scanPower!,
  }

  return { newStats, levelsGained, statsGained }
}

/**
 * Calculate total stat gains between two levels
 */
export function calculateStatGainsForLevels(
  fromLevel: number,
  toLevel: number
): Partial<PlayerStats> {
  let maxEnergy = 0
  let maxHealth = 0
  let attackPower = 0
  let defense = 0
  let scanPower = 0

  for (let level = fromLevel + 1; level <= toLevel; level++) {
    const gains = getStatGainsForLevel(level)
    maxEnergy += gains.maxEnergy
    maxHealth += gains.maxHealth
    attackPower += gains.attackPower
    defense += gains.defense
    scanPower += gains.scanPower
  }

  return { maxEnergy, maxHealth, attackPower, defense, scanPower }
}

/**
 * Get stat gains for a specific level
 */
export function getStatGainsForLevel(level: number): {
  maxEnergy: number
  maxHealth: number
  attackPower: number
  defense: number
  scanPower: number
} {
  // Base gains per level
  const base = {
    maxEnergy: 2,
    maxHealth: 5,
    attackPower: 1,
    defense: 1,
    scanPower: 1,
  }

  // Bonus at milestone levels (10, 25, 50, 75, 100)
  const milestones = [10, 25, 50, 75, 100]
  if (milestones.includes(level)) {
    return {
      maxEnergy: base.maxEnergy * 3,
      maxHealth: base.maxHealth * 3,
      attackPower: base.attackPower * 3,
      defense: base.defense * 3,
      scanPower: base.scanPower * 3,
    }
  }

  return base
}

// ============================================
// ENERGY SYSTEM
// ============================================

export interface EnergyConfig {
  maxEnergy: number
  regenRate: number // Energy per second
  regenDelay: number // Seconds before regen starts after use
}

export const DEFAULT_ENERGY_CONFIG: EnergyConfig = {
  maxEnergy: 100,
  regenRate: 1, // 1 energy per second
  regenDelay: 2, // 2 seconds before regen starts
}

/**
 * Calculate energy regeneration
 */
export function calculateEnergyRegen(
  currentEnergy: number,
  maxEnergy: number,
  timeSinceLastUse: number, // in seconds
  config: EnergyConfig = DEFAULT_ENERGY_CONFIG
): number {
  if (currentEnergy >= maxEnergy) return maxEnergy

  // No regen during delay period
  const effectiveTime = Math.max(0, timeSinceLastUse - config.regenDelay)

  const regenAmount = Math.floor(effectiveTime * config.regenRate)
  return Math.min(maxEnergy, currentEnergy + regenAmount)
}

/**
 * Time until full energy
 */
export function getTimeToFullEnergy(
  currentEnergy: number,
  maxEnergy: number,
  config: EnergyConfig = DEFAULT_ENERGY_CONFIG
): number {
  if (currentEnergy >= maxEnergy) return 0

  const energyNeeded = maxEnergy - currentEnergy
  return Math.ceil(energyNeeded / config.regenRate) + config.regenDelay
}

// ============================================
// INITIAL STATS
// ============================================

export function getInitialStats(): PlayerStats {
  return {
    level: 1,
    experience: 0,
    experienceToNextLevel: getXPForLevel(2),

    energy: 100,
    maxEnergy: 100,
    health: 100,
    maxHealth: 100,

    attackPower: 10,
    defense: 5,
    critChance: 0.05, // 5%
    critDamage: 1.5, // 150% damage

    scanPower: 0,

    totalDistance: 0,
    totalMoves: 0,
  }
}

// ============================================
// LEVEL MILESTONES & UNLOCKS
// ============================================

export interface LevelMilestone {
  level: number
  name: string
  description: string
  unlocks: string[]
}

export const LEVEL_MILESTONES: LevelMilestone[] = [
  {
    level: 1,
    name: 'Newborn Explorer',
    description: 'Begin your journey in the matrix',
    unlocks: ['Genesis Zone', 'Quick Scan', 'Basic Movement'],
  },
  {
    level: 5,
    name: 'Data Initiate',
    description: 'You understand the basics',
    unlocks: ['Bitcoin Layer Access', 'Power Strike Skill'],
  },
  {
    level: 10,
    name: 'Network Scout',
    description: 'The shallow network welcomes you',
    unlocks: ['Shallow Network Access', 'Data Burst Skill', 'Deep Scan'],
  },
  {
    level: 20,
    name: 'Matrix Navigator',
    description: 'You can navigate the processing core',
    unlocks: ['Processing Core Access', 'Equipment Crafting'],
  },
  {
    level: 35,
    name: 'Bridge Walker',
    description: 'The cortex bridge accepts you',
    unlocks: ['Cortex Bridge Access', 'System Override Skill'],
  },
  {
    level: 50,
    name: 'Deep Explorer',
    description: 'Enter the hidden layers',
    unlocks: ['Deep Network Access', 'Full Analysis Scan', 'Advanced Skills'],
  },
  {
    level: 75,
    name: 'Output Seeker',
    description: 'Approach the decision neurons',
    unlocks: ['Output Layer Access', 'Neural Link Skill'],
  },
  {
    level: 100,
    name: 'Matrix Master',
    description: 'You have mastered the matrix',
    unlocks: ['Void Access', 'Matrix Collapse Ultimate', 'All Secrets Revealed'],
  },
]

/**
 * Get milestones achieved at or below given level
 */
export function getAchievedMilestones(level: number): LevelMilestone[] {
  return LEVEL_MILESTONES.filter((m) => m.level <= level)
}

/**
 * Get next milestone
 */
export function getNextMilestone(level: number): LevelMilestone | null {
  return LEVEL_MILESTONES.find((m) => m.level > level) || null
}

// ============================================
// DISPLAY HELPERS
// ============================================

/**
 * Format XP display
 */
export function formatXP(xp: number): string {
  if (xp >= 1000000) {
    return `${(xp / 1000000).toFixed(1)}M`
  }
  if (xp >= 1000) {
    return `${(xp / 1000).toFixed(1)}K`
  }
  return xp.toString()
}

/**
 * Get XP progress percentage
 */
export function getXPProgress(currentXP: number, xpForNextLevel: number): number {
  if (xpForNextLevel <= 0) return 100
  return Math.min(100, (currentXP / xpForNextLevel) * 100)
}

/**
 * Get level color class
 */
export function getLevelColorClass(level: number): string {
  if (level >= 100) return 'text-pink-400'
  if (level >= 75) return 'text-orange-400'
  if (level >= 50) return 'text-purple-400'
  if (level >= 25) return 'text-blue-400'
  if (level >= 10) return 'text-green-400'
  return 'text-gray-400'
}

/**
 * Get energy color based on percentage
 */
export function getEnergyColorClass(energy: number, maxEnergy: number): string {
  const percent = (energy / maxEnergy) * 100
  if (percent <= 20) return 'bg-red-500'
  if (percent <= 50) return 'bg-yellow-500'
  return 'bg-green-500'
}

/**
 * Get health color based on percentage
 */
export function getHealthColorClass(health: number, maxHealth: number): string {
  const percent = (health / maxHealth) * 100
  if (percent <= 20) return 'bg-red-500'
  if (percent <= 50) return 'bg-orange-500'
  return 'bg-green-500'
}

// ============================================
// XP TABLE (for reference)
// ============================================

export function generateXPTable(): { level: number; xpRequired: number; totalXP: number }[] {
  const table = []
  let totalXP = 0

  for (let level = 1; level <= 100; level++) {
    const xpRequired = getXPForLevel(level)
    totalXP += xpRequired
    table.push({ level, xpRequired, totalXP })
  }

  return table
}
