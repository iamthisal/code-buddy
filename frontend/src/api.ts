export type Item = { name: string; description: string; price: string }
export type Theme = { primary: string; background: string; text: string; font: 'sans' | 'serif' }
export type Spec = { name: string; kind: string; description: string; tagline: string; sections: string[]; items: Item[]; theme: Theme }
export type Project = { id: number; name: string; prompt: string; current_version: number; spec: Spec; validation: { valid: boolean; issues: { level: string; code: string; message: string }[] }; preview_url: string }
export type ProjectSummary = Pick<Project, 'id' | 'name' | 'current_version'>
export type Version = { number: number; instruction: string; created_at: string; spec: Spec }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, init)
  const data = await response.json()
  if (!response.ok) {
    const detail = data.detail
    throw new Error(typeof detail === 'string' ? detail : detail?.message || 'Something went wrong')
  }
  return data as T
}

const post = (body: object): RequestInit => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
export const api = {
  projects: () => request<ProjectSummary[]>('/projects'),
  project: (id: number) => request<Project>(`/projects/${id}`),
  create: (prompt: string) => request<Project>('/projects', post({ prompt })),
  refine: (id: number, instruction: string) => request<Project>(`/projects/${id}/refine`, post({ instruction })),
  versions: (id: number) => request<Version[]>(`/projects/${id}/versions`),
  restore: (id: number, number: number) => request<Project>(`/projects/${id}/restore/${number}`, { method: 'POST' }),
}
