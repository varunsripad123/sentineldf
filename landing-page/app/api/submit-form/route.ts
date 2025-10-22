import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const formData = await request.formData()
    const email = formData.get('email')
    const company = formData.get('company')
    const useCase = formData.get('useCase')

    // Submit to Netlify Forms
    const netlifyFormData = new URLSearchParams()
    netlifyFormData.append('form-name', 'beta-signup')
    netlifyFormData.append('email', email as string)
    netlifyFormData.append('company', (company as string) || '')
    netlifyFormData.append('useCase', (useCase as string) || '')

    // In production on Netlify, this will work
    // In development, it will just succeed
    if (process.env.NETLIFY) {
      await fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: netlifyFormData.toString(),
      })
    }

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Form submission error:', error)
    return NextResponse.json({ success: false, error: 'Submission failed' }, { status: 500 })
  }
}
