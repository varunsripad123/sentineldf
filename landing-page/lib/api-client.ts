/**
 * API client for SentinelDF backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CreateUserRequest {
  email: string;
  name: string;
  company: string;
}

export interface CreateUserResponse {
  user_id: number;
  email: string;
  api_key: string;
  message: string;
}

/**
 * Create a new user and generate API key
 */
export async function createUserAndAPIKey(
  data: CreateUserRequest
): Promise<CreateUserResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/keys/users`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create user');
  }

  return response.json();
}

/**
 * Send API key via email
 */
export async function sendAPIKeyEmail(email: string, apiKey: string) {
  // Using Web3Forms to send email
  const response = await fetch('https://api.web3forms.com/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      access_key: process.env.NEXT_PUBLIC_WEB3FORMS_KEY,
      subject: 'Your SentinelDF API Key',
      from_name: 'SentinelDF',
      email: email,
      message: `
Welcome to SentinelDF!

Your API key is: ${apiKey}

⚠️ IMPORTANT: Save this key securely. You won't be able to see it again!

Quick Start:
1. Install the SDK:
   pip install sentineldf-ai

2. Use your API key:
   from sentineldf import SentinelDF
   client = SentinelDF(api_key="${apiKey}")
   results = client.scan(["your text to scan"])

Documentation: https://docs.sentineldf.com
Support: support@sentineldf.com

Happy scanning!
- The SentinelDF Team
      `.trim(),
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to send email');
  }

  return response.json();
}

/**
 * Generate a new API key for authenticated user
 */
export async function generateAPIKey(
  clerkToken: string,
  keyName: string = 'Dashboard Key'
): Promise<{ api_key: string; key_id: number; key_prefix: string }> {
  const response = await fetch(`${API_BASE_URL}/v1/keys/create?name=${encodeURIComponent(keyName)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${clerkToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate API key');
  }

  return response.json();
}

/**
 * Get user's API keys
 */
export async function getUserAPIKeys(
  clerkToken: string
): Promise<Array<{ id: number; name: string; key_prefix: string; created_at: string }>> {
  const response = await fetch(`${API_BASE_URL}/v1/keys/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${clerkToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch API keys');
  }

  return response.json();
}

/**
 * Get usage statistics for the authenticated user
 * Aggregates usage across all API keys owned by the user
 */
export async function getUsageStats(
  clerkToken: string
): Promise<{
  total_calls: number;
  documents_scanned: number;
  quarantined_documents: number;
  quota_limit: number;
  quota_remaining: number;
  quota_percentage_used: number;
  cost_dollars: number;
}> {
  const response = await fetch(`${API_BASE_URL}/v1/usage/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${clerkToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch usage stats');
  }

  return response.json();
}


