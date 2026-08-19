import { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

type Job = {
  id: number
  title: string
  company?: string
  location?: string
  source: string
  url?: string
  posted_at?: string
  remote?: boolean
}

type Metrics = {
  total_jobs: number
  jobs_fetched_today: number
  successful_runs: number
  failed_runs: number
  duplicate_jobs: number
  average_ingestion_time_seconds: number
}

export default function App() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [runState, setRunState] = useState('idle')

  const fetchData = async () => {
    setLoading(true)
    try {
      const [jobsRes, metricsRes] = await Promise.all([
        fetch(`${API_BASE}/api/jobs?page=1&page_size=10`),
        fetch(`${API_BASE}/api/metrics`),
      ])
      if (jobsRes.ok) {
        const jobsData = await jobsRes.json()
        setJobs(jobsData.items || [])
      }
      if (metricsRes.ok) {
        const metricsData = await metricsRes.json()
        setMetrics(metricsData)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleRunIngestion = async () => {
    setRunState('running')
    try {
      const response = await fetch(`${API_BASE}/api/ingestion/run`, { method: 'POST' })
      const data = await response.json()
      if (!response.ok) {
        setRunState('failed')
        return
      }
      setRunState('success')
      await fetchData()
    } catch {
      setRunState('failed')
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/80">
        <div className="mx-auto max-w-7xl px-6 py-6 flex items-center justify-between">
          <div>
            <div className="text-2xl font-bold">JobPulse</div>
            <div className="text-sm text-slate-400">Resilient Job Data Ingestion</div>
          </div>
          <button
            onClick={handleRunIngestion}
            className="rounded bg-emerald-500 px-4 py-2 font-medium text-slate-950 hover:bg-emerald-400"
          >
            {runState === 'running' ? 'Running...' : 'Run Ingestion'}
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-8">
        <section className="grid gap-4 md:grid-cols-5">
          {[
            ['System', 'HEALTHY'],
            ['Primary', 'HEALTHY'],
            ['Fallback', 'READY'],
            ['Database', 'CONNECTED'],
            ['Source', 'PUBLIC API'],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <div className="text-xs uppercase tracking-wider text-slate-400">{label}</div>
              <div className="mt-3 text-xl font-semibold text-emerald-400">{value}</div>
            </div>
          ))}
        </section>

        <section className="grid gap-4 md:grid-cols-6">
          {metrics ? [
            ['Total Jobs', metrics.total_jobs],
            ['Fetched Today', metrics.jobs_fetched_today],
            ['Successful Runs', metrics.successful_runs],
            ['Failed Runs', metrics.failed_runs],
            ['Duplicate Jobs', metrics.duplicate_jobs],
            ['Avg Ingest Time', `${metrics.average_ingestion_time_seconds}s`],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <div className="text-xs text-slate-400">{label}</div>
              <div className="mt-3 text-2xl font-semibold">{value}</div>
            </div>
          )) : null}
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
            <div className="mb-4 text-lg font-semibold">Recent job listings</div>
            <div className="space-y-3">
              {jobs.length === 0 ? (
                <div className="text-slate-400">No jobs currently available.</div>
              ) : (
                jobs.map((job) => (
                  <div key={job.id} className="rounded border border-slate-800 bg-slate-950 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="font-medium text-white">{job.title}</div>
                      <span className="rounded bg-blue-500/10 px-2 py-1 text-xs text-blue-300">{job.source}</span>
                    </div>
                    <div className="mt-2 text-sm text-slate-300">{job.company || 'Unknown company'} · {job.location || 'Remote'}</div>
                    <div className="mt-2 text-xs text-slate-400">{job.posted_at ? new Date(job.posted_at).toLocaleDateString() : 'Recently posted'}</div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
            <div className="mb-4 text-lg font-semibold">Source health</div>
            <div className="overflow-hidden rounded border border-slate-800">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-slate-800 text-slate-300">
                  <tr>
                    <th className="px-3 py-2">Source</th>
                    <th className="px-3 py-2">Status</th>
                    <th className="px-3 py-2">Last Success</th>
                    <th className="px-3 py-2">Failures</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-t border-slate-800">
                    <td className="px-3 py-2">primary</td>
                    <td className="px-3 py-2 text-emerald-400">healthy</td>
                    <td className="px-3 py-2">—</td>
                    <td className="px-3 py-2">0</td>
                  </tr>
                  <tr className="border-t border-slate-800">
                    <td className="px-3 py-2">fallback</td>
                    <td className="px-3 py-2 text-emerald-400">ready</td>
                    <td className="px-3 py-2">—</td>
                    <td className="px-3 py-2">0</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
