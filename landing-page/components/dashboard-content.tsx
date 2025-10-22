'use client'

import { useState, useEffect } from 'react'
import { UserButton, useAuth } from '@clerk/nextjs'
import { Key, BarChart3, CreditCard, Settings, Copy, CheckCircle, AlertTriangle, TestTube } from 'lucide-react'
import { generateAPIKey, getUserAPIKeys, getUsageStats } from '../lib/api-client'
import ScanDemo from './scan-demo'

export default function DashboardContent({ user }: { user: any }) {
  const [activeTab, setActiveTab] = useState('api-keys')

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
                <span className="text-xl font-bold text-white">S</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">SentinelDF</h1>
                <p className="text-sm text-slate-400">Dashboard</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-medium text-white">{user?.firstName || user?.emailAddresses[0]?.emailAddress}</p>
                <p className="text-xs text-slate-400">Free Plan</p>
              </div>
              <UserButton afterSignOutUrl="/" />
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        {/* Welcome Message */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white">
            Welcome back, {user?.firstName || 'there'}! 👋
          </h2>
          <p className="mt-2 text-slate-400">
            Manage your API keys, monitor usage, and configure your account.
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-2 border-b border-slate-800">
          <button
            onClick={() => setActiveTab('api-keys')}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'api-keys'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Key className="h-4 w-4" />
            API Keys
          </button>
          <button
            onClick={() => setActiveTab('usage')}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'usage'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <BarChart3 className="h-4 w-4" />
            Usage
          </button>
          <button
            onClick={() => setActiveTab('billing')}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'billing'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <CreditCard className="h-4 w-4" />
            Billing
          </button>
          <button
            onClick={() => setActiveTab('test')}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'test'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <TestTube className="h-4 w-4" />
            Test API
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'settings'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Settings className="h-4 w-4" />
            Settings
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'api-keys' && <APIKeysTab userId={user?.id} />}
        {activeTab === 'usage' && <UsageTab />}
        {activeTab === 'test' && <ScanDemo />}
        {activeTab === 'billing' && <BillingTab />}
        {activeTab === 'settings' && <SettingsTab user={user} />}
      </div>
    </div>
  )
}

function APIKeysTab({ userId }: { userId: string }) {
  const { getToken } = useAuth()
  const [apiKey, setApiKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [existingKeys, setExistingKeys] = useState<any[]>([])

  // Load existing API keys on mount
  useEffect(() => {
    loadExistingKeys()
  }, [])

  const loadExistingKeys = async () => {
    try {
      const token = await getToken()
      if (!token) return
      
      const keys = await getUserAPIKeys(token)
      setExistingKeys(keys)
    } catch (err) {
      console.error('Failed to load API keys:', err)
    }
  }

  const handleGenerateAPIKey = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const token = await getToken()
      if (!token) {
        throw new Error('Authentication required')
      }
      
      // Call real backend API to generate key
      const result = await generateAPIKey(token, 'Dashboard Key')
      setApiKey(result.api_key)
      
      // Reload keys list
      await loadExistingKeys()
    } catch (err: any) {
      setError(err.message || 'Failed to generate API key')
      console.error('Error generating API key:', err)
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="space-y-6">
      {/* Alert: Getting Started */}
      <div className="rounded-lg bg-blue-900/20 border border-blue-800 p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-white mb-1">Generate your first API key</h3>
            <p className="text-sm text-slate-300">
              You'll need an API key to use SentinelDF. Click the button below to generate one. 
              Make sure to save it securely - you won't be able to see it again!
            </p>
          </div>
        </div>
      </div>

      {/* Generate New Key */}
      <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Generate New API Key</h3>
        
        {error && (
          <div className="mb-4 p-3 bg-red-900/20 border border-red-800 rounded-lg">
            <p className="text-sm text-red-400">❌ {error}</p>
          </div>
        )}
        
        <button
          onClick={handleGenerateAPIKey}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
        >
          {loading ? 'Generating...' : '+ Generate New Key'}
        </button>

        {/* Show generated key */}
        {apiKey && (
          <div className="mt-6 p-4 bg-green-900/20 border border-green-800 rounded-lg">
            <div className="flex items-start gap-3 mb-3">
              <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-white mb-1">API Key Generated!</h4>
                <p className="text-sm text-slate-300">
                  Save this key securely. You won't be able to see it again.
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2 mt-3">
              <code className="flex-1 bg-slate-950 border border-slate-700 px-4 py-3 rounded-lg text-sm font-mono text-green-400 break-all">
                {apiKey}
              </code>
              <button
                onClick={copyToClipboard}
                className="flex-shrink-0 p-3 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 hover:text-white transition-colors"
                title="Copy to clipboard"
              >
                {copied ? (
                  <CheckCircle className="h-5 w-5 text-green-400" />
                ) : (
                  <Copy className="h-5 w-5" />
                )}
              </button>
            </div>

            {/* Comprehensive Examples */}
            <div className="mt-6 space-y-4">
              {/* Python SDK */}
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  🐍 Python SDK
                </h4>
                <code className="block text-xs font-mono text-slate-300 whitespace-pre bg-slate-900 p-3 rounded overflow-x-auto">
{`# Install
pip install sentineldf

# Quick Start
from sentineldf import SentinelDF

client = SentinelDF(api_key="${apiKey.substring(0, 20)}...")
result = client.scan("Your text to scan")

if result['is_safe']:
    print("✅ Text is safe!")
else:
    print(f"⚠️ Threats: {result['threats']}")`}
                </code>
              </div>

              {/* CLI Usage */}
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  💻 CLI Usage
                </h4>
                <code className="block text-xs font-mono text-slate-300 whitespace-pre bg-slate-900 p-3 rounded overflow-x-auto">
{`# Scan a file
sentineldf scan-file data.txt --api-key ${apiKey.substring(0, 15)}...

# Scan directory
sentineldf scan-directory ./data/ --api-key ${apiKey.substring(0, 15)}...

# Launch GUI
sentineldf gui --api-key ${apiKey.substring(0, 15)}...`}
                </code>
              </div>

              {/* Batch Processing */}
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  📊 Batch Processing
                </h4>
                <code className="block text-xs font-mono text-slate-300 whitespace-pre bg-slate-900 p-3 rounded overflow-x-auto">
{`import pandas as pd
from sentineldf import SentinelDF

client = SentinelDF(api_key="${apiKey.substring(0, 20)}...")

# Scan CSV dataset
df = pd.read_csv("training_data.csv")
results = [client.scan(text) for text in df['text']]

# Filter safe samples
df['is_safe'] = [r['is_safe'] for r in results]
safe_df = df[df['is_safe']]
safe_df.to_csv("clean_data.csv")`}
                </code>
              </div>

              {/* API Integration */}
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  🔌 API Integration
                </h4>
                <code className="block text-xs font-mono text-slate-300 whitespace-pre bg-slate-900 p-3 rounded overflow-x-auto">
{`from flask import Flask, request, jsonify
from sentineldf import SentinelDF

app = Flask(__name__)
client = SentinelDF(api_key="${apiKey.substring(0, 20)}...")

@app.route('/check', methods=['POST'])
def check_content():
    text = request.json['text']
    result = client.scan(text)
    return jsonify(result)`}
                </code>
              </div>

              {/* CI/CD Integration */}
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg">
                <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                  ⚙️ CI/CD Integration
                </h4>
                <code className="block text-xs font-mono text-slate-300 whitespace-pre bg-slate-900 p-3 rounded overflow-x-auto">
{`# .github/workflows/scan.yml
name: Scan Training Data
on: [push]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install sentineldf
      - run: |
          sentineldf scan-directory ./data/ \
            --api-key \${{ secrets.SENTINELDF_KEY }} \
            --fail-on-threat`}
                </code>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Existing Keys */}
      <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Your API Keys</h3>
        
        {existingKeys.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            <Key className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>No API keys yet. Generate one above to get started!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {existingKeys.map((key) => (
              <div key={key.id} className="flex items-center justify-between p-4 bg-slate-800 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">{key.name}</p>
                  <p className="text-xs text-slate-400 font-mono mt-1">{key.key_prefix}</p>
                  <p className="text-xs text-slate-500 mt-1">
                    Created: {new Date(key.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 bg-green-900/20 text-green-400 text-xs rounded-full">
                    Active
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function UsageTab() {
  const { getToken } = useAuth()
  const [usage, setUsage] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUsage()
  }, [])

  const loadUsage = async () => {
    try {
      const token = await getToken()
      if (!token) return
      
      const stats = await getUsageStats(token)
      setUsage(stats)
    } catch (err) {
      console.error('Failed to load usage stats:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-slate-400">Loading usage data...</div>
      </div>
    )
  }

  const totalQuota = usage?.quota_limit || 10000
  const usedCalls = usage?.total_calls || 0
  const usagePercent = usage?.quota_percentage_used || ((usedCalls / totalQuota) * 100)

  return (
    <div className="space-y-6">
      {/* Current Month Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
          <p className="text-sm text-slate-400 mb-2">API Calls</p>
          <p className="text-3xl font-bold text-white">{usage?.total_calls || 0}</p>
          <p className="text-sm text-slate-500 mt-2">This month</p>
        </div>
        
        <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
          <p className="text-sm text-slate-400 mb-2">Documents Scanned</p>
          <p className="text-3xl font-bold text-white">{usage?.documents_scanned || 0}</p>
          <p className="text-sm text-slate-500 mt-2">Total processed</p>
        </div>
        
        <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
          <p className="text-sm text-slate-400 mb-2">Threats Blocked</p>
          <p className="text-3xl font-bold text-red-400">{usage?.quarantined_documents || 0}</p>
          <p className="text-sm text-slate-500 mt-2">Quarantined</p>
        </div>
        
        <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
          <p className="text-sm text-slate-400 mb-2">Quota Remaining</p>
          <p className="text-3xl font-bold text-green-400">{usage?.quota_remaining?.toLocaleString() || 0}</p>
          <p className="text-sm text-slate-500 mt-2">of {usage?.quota_limit?.toLocaleString() || '10,000'}</p>
        </div>
      </div>

      {/* Quota Progress */}
      <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Monthly Quota</h3>
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">
              {usedCalls} of {totalQuota.toLocaleString()} calls used
            </span>
            <span className="text-white font-medium">{usagePercent.toFixed(1)}%</span>
          </div>
          <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-500" 
              style={{ width: `${Math.min(usagePercent, 100)}%` }} 
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function BillingTab() {
  return (
    <div className="space-y-6">
      {/* Current Plan */}
      <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Current Plan</h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-2xl font-bold text-white">Free</p>
            <p className="text-sm text-slate-400 mt-1">1,000 API calls/month</p>
          </div>
          <span className="px-4 py-2 bg-green-900/20 text-green-400 rounded-lg text-sm font-medium">
            Active
          </span>
        </div>
      </div>

      {/* Upgrade Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-2">Pro</h3>
          <p className="text-3xl font-bold text-white mb-1">
            $49<span className="text-lg text-slate-400">/month</span>
          </p>
          <p className="text-sm text-slate-400 mb-4">50,000 API calls/month</p>
          <button className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors">
            Upgrade to Pro
          </button>
        </div>

        <div className="rounded-lg bg-gradient-to-br from-purple-900/20 to-pink-900/20 border border-purple-800 p-6">
          <h3 className="text-xl font-bold text-white mb-2">Enterprise</h3>
          <p className="text-3xl font-bold text-white mb-1">Custom</p>
          <p className="text-sm text-slate-400 mb-4">Unlimited API calls</p>
          <button className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium transition-colors">
            Contact Sales
          </button>
        </div>
      </div>
    </div>
  )
}

function SettingsTab({ user }: { user: any }) {
  return (
    <div className="space-y-6">
      <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Account Information</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Email</label>
            <input
              type="email"
              value={user?.emailAddresses[0]?.emailAddress || ''}
              disabled
              className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white disabled:opacity-50"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">User ID</label>
            <input
              type="text"
              value={user?.id || ''}
              disabled
              className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white disabled:opacity-50 font-mono text-sm"
            />
          </div>
        </div>
      </div>

      <div className="rounded-lg bg-slate-900 border border-slate-800 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Documentation</h3>
        <div className="space-y-3">
          <a href="#" className="block text-blue-400 hover:text-blue-300 text-sm">
            📖 API Documentation
          </a>
          <a href="#" className="block text-blue-400 hover:text-blue-300 text-sm">
            💻 Code Examples
          </a>
          <a href="#" className="block text-blue-400 hover:text-blue-300 text-sm">
            🚀 Getting Started Guide
          </a>
        </div>
      </div>
    </div>
  )
}
