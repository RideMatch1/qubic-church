import { NextRequest, NextResponse } from 'next/server'
import {
  getEscrowStatus,
  checkEscrowDeposit,
  executeJoinBet,
  executeSweep,
} from '@/lib/predict/escrow-manager'
import { ensureAutoCron } from '@/lib/predict/auto-cron'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'
import { escrowLog } from '@/lib/predict/logger'

// Start background cron on first bet status check (frontend polls every 5s)
ensureAutoCron()

/**
 * GET /api/predict/bet/status — Poll escrow/bet status
 *
 * Query params:
 *   id: bet ID (bet_xxx) or escrow ID (esc_xxx)
 *   check: if "true", actively check blockchain for deposits (default: true)
 *
 * Used by the frontend to track the lifecycle:
 *   awaiting_deposit → deposit_detected → joining_sc → active_in_sc → won/lost → swept
 *
 * Auto-actions triggered inline:
 *   - awaiting_deposit: live-check blockchain → if deposit found, auto-trigger joinBet
 *   - deposit_detected: auto-trigger executeJoinBet()
 *   - won_awaiting_sweep: auto-trigger executeSweep()
 */
export async function GET(request: NextRequest) {
  const rl = rateLimitResponse(request, 'GET /bet/status')
  if (rl) return rl

  try {
    const { searchParams } = new URL(request.url)
    const id = searchParams.get('id')
    const shouldCheck = searchParams.get('check') !== 'false'

    if (!id) {
      return NextResponse.json(
        { error: 'Missing required param: id (bet_xxx or esc_xxx)' },
        { status: 400 },
      )
    }

    // First get the current status from DB
    let status = getEscrowStatus(id)

    if (!status) {
      return NextResponse.json(
        { error: 'Bet/escrow not found' },
        { status: 404 },
      )
    }

    // --- Phase 1: Deposit Detection ---
    if (shouldCheck && status.status === 'awaiting_deposit') {
      try {
        const balance = await checkEscrowDeposit(status.escrowId)
        if (balance > 0n) {
          status = getEscrowStatus(id)!
        }
      } catch (err) {
        escrowLog.warn({ err }, 'live balance check failed')
      }
    }

    // --- Phase 2: Auto-JoinBet ---
    if (shouldCheck && status.status === 'deposit_detected') {
      try {
        escrowLog.info({ escrowId: status.escrowId }, 'auto-triggering joinBet')
        const result = await executeJoinBet(status.escrowId)
        if (result.success) {
          escrowLog.info({ txId: result.txId, tick: result.tick }, 'joinBet success (API-triggered)')
        } else {
          escrowLog.warn({ error: result.error }, 'joinBet failed (API-triggered)')
        }
        // Re-fetch status regardless (status changed to joining_sc or active_in_sc)
        status = getEscrowStatus(id)!
      } catch (err) {
        escrowLog.warn({ err }, 'auto-joinBet failed')
      }
    }

    // --- Phase 3: Auto-Sweep ---
    if (shouldCheck && status.status === 'won_awaiting_sweep') {
      try {
        escrowLog.info({ escrowId: status.escrowId }, 'auto-triggering sweep')
        const result = await executeSweep(status.escrowId)
        if (result.success) {
          escrowLog.info({ txId: result.txId, amountQu: result.amountQu }, 'sweep success (API-triggered)')
        } else {
          escrowLog.warn({ error: result.error }, 'sweep failed (API-triggered)')
        }
        status = getEscrowStatus(id)!
      } catch (err) {
        escrowLog.warn({ err }, 'auto-sweep failed')
      }
    }

    return NextResponse.json(status)
  } catch (error) {
    return safeErrorResponse(error, 'Failed to get bet status')
  }
}
