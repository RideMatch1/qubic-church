#!/usr/bin/env node
/**
 * ORACLE EXPORT — DB → Dashboard JSON Export
 *
 * Exports oracle-dashboard.json for the web dashboard.
 * Can be used standalone or imported by ORACLE_AUTOPILOT.
 *
 * Usage: node scripts/oracle-export.mjs
 */

import { getDb, closeDb, getDashboardExport } from './oracle-db.mjs'
import { writeFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const OUTPUT_PATH = join(__dirname, '..', 'public', 'data', 'oracle-dashboard.json')

/**
 * Export dashboard JSON from SQLite to public/data.
 */
export function exportDashboard() {
  const data = getDashboardExport()
  writeFileSync(OUTPUT_PATH, JSON.stringify(data, null, 2))
  console.log(`     Exported to oracle-dashboard.json (${(JSON.stringify(data).length / 1024).toFixed(1)} KB)`)
  return data
}

// Run standalone if called directly
if (process.argv[1]?.endsWith('oracle-export.mjs')) {
  const db = getDb()
  const data = exportDashboard()
  console.log()
  console.log(`  Summary:`)
  console.log(`    Predictions: ${data.summary.totalPredictions}`)
  console.log(`    Accuracy:    ${data.summary.overallAccuracy ?? '--'}%`)
  console.log(`    Prices:      ${data.summary.totalPriceSnapshots}`)
  console.log(`    Pairs:       ${data.summary.uniquePairs}`)
  console.log(`    Strategies:  ${data.strategies.length}`)
  closeDb()
}
