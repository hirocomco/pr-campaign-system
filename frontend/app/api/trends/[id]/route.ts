import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://prcs_backend:8000'

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    console.log(`Fetching trend ${params.id} from ${BACKEND_URL}`)
    
    const response = await fetch(`${BACKEND_URL}/api/v1/trends/${params.id}`, {
      // Force IPv4 and add headers to help with Docker networking
      headers: {
        'Host': 'prcs_backend:8000',
        'User-Agent': 'NextJS-API'
      }
    })
    
    console.log(`Backend response status: ${response.status}`)
    
    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json({ error: 'Trend not found' }, { status: 404 })
      }
      const errorText = await response.text()
      console.error(`Backend error: ${response.status} - ${errorText}`)
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    console.log(`Successfully fetched trend: ${data.title}`)
    return NextResponse.json(data)
  } catch (error) {
    console.error('Trend detail API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch trend', details: error.message },
      { status: 500 }
    )
  }
} 