import { NextRequest, NextResponse } from 'next/server'
import { requestWithdrawal, validateAuthToken } from '@/lib/qflash/balance-manager'
import { rateLimitResponse } from '@/lib/predict/rate-limiter'
import { safeErrorResponse } from '@/lib/predict/api-utils'

/**
 * POST /api/qflash/account/withdraw — Request a withdrawal
 *
 * Headers: Authorization: Bearer <api_token>
 * Body: { address, amountQu, destination }
 */
export async function POST(request: NextRequest) {
  const rl = rateLimitResponse(request, 'POST /account/withdraw')
  if (rl) return rl

  try {
    // Auth check
    const authAccount = validateAuthToken(request.headers.get('authorization'))
    if (!authAccount) {
      return NextResponse.json({ error: 'Unauthorized — provide Bearer token' }, { status: 401 })
    }

    let body: { address?: string; amountQu?: number; destination?: string }
    try {
      body = await request.json()
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 })
    }

    if (!body.amountQu || !body.destination) {
      return NextResponse.json(
        { error: 'Missing required fields: amountQu, destination' },
        { status: 400 },
      )
    }

    // Use authenticated account's address
    const address = body.address ?? authAccount.address
    if (address !== authAccount.address) {
      return NextResponse.json({ error: 'Address does not match authenticated account' }, { status: 403 })
    }

    const tx = requestWithdrawal({
      address,
      amountQu: body.amountQu,
      destinationAddress: body.destination,
    })

    return NextResponse.json({
      transactionId: tx.id,
      status: tx.status,
      amountQu: tx.amountQu,
      message: 'Withdrawal queued. Will be processed within the next cron cycle.',
    })
  } catch (error) {
    const msg = error instanceof Error ? error.message : 'Failed to process withdrawal'
    const isClientError = ['Insufficient balance', 'Account not found', 'Address', 'Minimum', 'Source', 'Destination'].some((p) => msg.includes(p))
    if (isClientError) {
      return NextResponse.json({ error: msg }, { status: 400 })
    }
    return safeErrorResponse(error, 'Failed to process withdrawal')
  }
}
