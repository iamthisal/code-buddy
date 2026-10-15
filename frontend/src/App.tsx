import { useEffect, useState } from 'react'
import { ArrowUp, Check, ChevronDown, Download, Eye, FileClock, LayoutTemplate, Monitor, PanelLeftClose, Plus, RotateCcw, Smartphone, Tablet, WandSparkles } from 'lucide-react'
import { api, type Project, type ProjectSummary, type Version } from './api'

type Panel = 'chat' | 'theme' | 'versions' | 'validation' | 'templates'
type Device = 'desktop' | 'tablet' | 'mobile'
const examples = [
  { title: 'The local bakery', prompt: 'A bakery called Butter & Crumb selling cupcakes and custom cakes, pink theme, with FAQ and contact' },
  { title: 'The neighborhood studio', prompt: 'A yoga studio called Still House with booking, testimonials and contact, green theme' },
  { title: 'The new idea', prompt: 'A waitlist for a new coffee app called Daybreak, orange theme, with FAQ' },
]

export default function App() {
  const [projects, setProjects] = useState<ProjectSummary[]>([])
  const [project, setProject] = useState<Project | null>(null)
  const [panel, setPanel] = useState<Panel>('chat')
  const [device, setDevice] = useState<Device>('desktop')
  const [prompt, setPrompt] = useState('')
  const [instruction, setInstruction] = useState('')
  const [versions, setVersions] = useState<Version[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [sidebar, setSidebar] = useState(true)
  const [draftColor, setDraftColor] = useState('#256f68')

  useEffect(() => { api.projects().then(setProjects).catch(err => setError(err.message)) }, [])
  useEffect(() => { if (project && panel === 'versions') api.versions(project.id).then(setVersions).catch(err => setError(err.message)) }, [project, panel])
  useEffect(() => { if (project) setDraftColor(project.spec.theme.primary) }, [project?.spec.theme.primary])

  async function load(id: number) {
    setBusy(true); setError('')
    try { setProject(await api.project(id)); setVersions(await api.versions(id)); setPanel('chat') } catch (err) { setError((err as Error).message) } finally { setBusy(false) }
  }
  async function create(value = prompt) {
    if (!value.trim()) return
    setBusy(true); setError('')
    try {
      const next = await api.create(value)
      setProject(next); setVersions([]); setPrompt(''); setPanel('chat'); setProjects(await api.projects())
    } catch (err) { setError((err as Error).message) } finally { setBusy(false) }
  }
  async function edit(value = instruction) {
    if (!project || !value.trim()) return
    setBusy(true); setError('')
    try { setProject(await api.refine(project.id, value)); setVersions(await api.versions(project.id)); setInstruction('') } catch (err) { setError((err as Error).message) } finally { setBusy(false) }
  }
  async function restore(number: number) {
    if (!project) return
    setBusy(true); setError('')
    try { setProject(await api.restore(project.id, number)); setVersions(await api.versions(project.id)) } catch (err) { setError((err as Error).message) } finally { setBusy(false) }
  }
  function download() {
    if (!project) return
    const link = document.createElement('a')
    link.href = `/api/v1/projects/${project.id}/export`
    link.download = `siteforge-${project.id}.zip`
    link.click()
  }

  return <div className="app-shell">
    {sidebar && <aside className="sidebar">
      <div className="brand"><span className="brand-mark"><WandSparkles size={17} /></span><span>SiteForge</span><button className="icon-button sidebar-close" aria-label="Collapse sidebar" title="Collapse sidebar" onClick={() => setSidebar(false)}><PanelLeftClose size={18} /></button></div>
      <button className="new-button" onClick={() => { setProject(null); setPanel('chat'); setError('') }}><Plus size={17} /> New project</button>
      <div className="sidebar-label">YOUR PROJECTS</div>
      <div className="project-list">{projects.map(p => <button key={p.id} className={`project-link ${project?.id === p.id ? 'active' : ''}`} onClick={() => load(p.id)}><span className="project-initial">{p.name[0]}</span><span className="project-name">{p.name}</span><span className="project-version">v{p.current_version}</span></button>)}</div>
      <div className="sidebar-foot">Built for the first big idea.</div>
    </aside>}
    <main className="workspace">
      <header className="topbar">
        <div className="topbar-title">{!sidebar && <button className="icon-button" title="Expand sidebar" aria-label="Expand sidebar" onClick={() => setSidebar(true)}><PanelLeftClose size={18} /></button>}{project ? <><span>{project.name}</span><span className="version-pill">Version {project.current_version}</span></> : <span>New project</span>}</div>
        <div className="topbar-actions">{project && <><button className="text-button" onClick={() => setPanel('validation')} title="View validation report"><span className={`status-dot ${project.validation.valid ? '' : 'error'}`} />{project.validation.valid ? 'Validated' : 'Needs review'}</button><button className="outline-button" onClick={download}><Download size={16} /> Export ZIP</button></>}</div>
      </header>
      {error && <div className="error-banner" role="alert">{error}<button onClick={() => setError('')} aria-label="Dismiss error">×</button></div>}
      {!project ? <section className="start-view"><div className="start-inner"><span className="start-icon"><WandSparkles size={23} /></span><h1>What are you building?</h1><p>Tell us about your business. We’ll turn it into a site you can explore and edit.</p><form className="prompt-box" onSubmit={e => { e.preventDefault(); create() }}><label className="sr-only" htmlFor="new-prompt">Describe your business</label><textarea id="new-prompt" value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="A bakery selling cupcakes and custom cakes, pink theme, with FAQ..." rows={4} maxLength={2000} /><div className="prompt-box-bottom"><span>{prompt.length}/2000</span><button className="send-button" type="submit" disabled={busy || prompt.trim().length < 3} aria-label="Generate site"><ArrowUp size={20} /></button></div></form><div className="examples-label">START WITH AN IDEA</div><div className="examples">{examples.map(example => <button key={example.title} className="example" onClick={() => create(example.prompt)}><LayoutTemplate size={19} /><span>{example.title}</span><span className="example-arrow">↗</span></button>)}</div></div></section> : <div className="editor">
        <section className="control-panel">
          <div className="panel-tabs" role="tablist" aria-label="Editor panels">{([['chat', 'Edit'], ['theme', 'Theme'], ['versions', 'History'], ['validation', 'Checks'], ['templates', 'Templates']] as const).map(([key, title]) => <button key={key} role="tab" aria-selected={panel === key} className={panel === key ? 'selected' : ''} onClick={() => setPanel(key)}>{title}</button>)}</div>
          {panel === 'chat' && <div className="panel-body chat-panel"><div className="panel-heading"><span className="panel-icon"><WandSparkles size={18} /></span><h2>Make it yours</h2><p>Ask for a change and a new version will appear.</p></div><div className="conversation"><div className="message user-message">{project.prompt}</div><div className="message system-message"><Check size={16} /> Your {project.spec.kind} site is ready to preview.</div>{versions.slice(0, 3).filter(v => v.number > 1).reverse().map(v => <div className="message user-message" key={v.number}>{v.instruction}</div>)}</div><form className="edit-form" onSubmit={e => { e.preventDefault(); edit() }}><label htmlFor="edit-prompt" className="sr-only">Describe a change</label><textarea id="edit-prompt" value={instruction} onChange={e => setInstruction(e.target.value)} placeholder="Make it dark and add pricing..." rows={3} maxLength={500} /><div className="edit-actions"><span>Try “add FAQ” or “change color to green”</span><button className="send-button" type="submit" disabled={busy || instruction.trim().length < 3} aria-label="Apply change"><ArrowUp size={19} /></button></div></form></div>}
          {panel === 'theme' && <div className="panel-body"><div className="panel-heading"><h2>Theme</h2><p>Colors and typography for this site.</p></div><div className="setting"><label htmlFor="theme-color">Primary color</label><div className="color-row"><input id="theme-color" type="color" value={draftColor} onChange={e => setDraftColor(e.target.value)} /><code>{draftColor}</code><button className="apply-button" disabled={busy || draftColor === project.spec.theme.primary} onClick={() => edit(`change color to ${draftColor}`)}>Apply</button></div></div><div className="setting"><span>Appearance</span><div className="segmented"><button className={project.spec.theme.background === '#ffffff' ? 'active' : ''} onClick={() => edit('make it light')}>Light</button><button className={project.spec.theme.background !== '#ffffff' ? 'active' : ''} onClick={() => edit('make it dark')}>Dark</button></div></div><div className="setting"><span>Font</span><div className="segmented"><button className={project.spec.theme.font === 'sans' ? 'active' : ''} onClick={() => edit('change font to sans')}>Sans</button><button className={project.spec.theme.font === 'serif' ? 'active' : ''} onClick={() => edit('change font to serif')}>Serif</button></div></div></div>}
          {panel === 'versions' && <div className="panel-body"><div className="panel-heading"><h2>Version history</h2><p>Restore any earlier version as a new version.</p></div><div className="version-list">{versions.map(v => <div className="version-item" key={v.number}><span className="version-icon"><FileClock size={17} /></span><div><strong>Version {v.number}</strong><p>{v.instruction}</p><small>{new Date(v.created_at).toLocaleString()}</small></div>{v.number !== project.current_version && <button className="icon-button" title={`Restore version ${v.number}`} aria-label={`Restore version ${v.number}`} onClick={() => restore(v.number)}><RotateCcw size={17} /></button>}</div>)}</div></div>}
          {panel === 'validation' && <div className="panel-body"><div className="panel-heading"><h2>Site checks</h2><p>Accessibility and structure checks for the current version.</p></div><div className={`validation-result ${project.validation.valid ? 'ok' : 'bad'}`}><Check size={18} /><strong>{project.validation.valid ? 'No errors found' : 'Review needed'}</strong></div>{project.validation.issues.map(issue => <div className="issue" key={issue.code}>{issue.message}</div>)}</div>}
          {panel === 'templates' && <div className="panel-body"><div className="panel-heading"><h2>Site type</h2><p>This project uses the {project.spec.kind} layout.</p></div><div className="template-list">{['Landing', 'Store', 'Booking', 'Waitlist', 'Menu'].map(kind => <div className={project.spec.kind === kind.toLowerCase() ? 'template-row current' : 'template-row'} key={kind}><LayoutTemplate size={18} /><span>{kind}</span>{project.spec.kind === kind.toLowerCase() && <Check size={16} />}</div>)}</div></div>}
        </section>
        <section className="preview-panel"><div className="preview-toolbar"><div className="preview-title"><Eye size={17} /><span>Live preview</span><ChevronDown size={15} /></div><div className="device-controls" aria-label="Preview size"><button className={device === 'desktop' ? 'active' : ''} title="Desktop" aria-label="Desktop preview" onClick={() => setDevice('desktop')}><Monitor size={17} /></button><button className={device === 'tablet' ? 'active' : ''} title="Tablet" aria-label="Tablet preview" onClick={() => setDevice('tablet')}><Tablet size={17} /></button><button className={device === 'mobile' ? 'active' : ''} title="Mobile" aria-label="Mobile preview" onClick={() => setDevice('mobile')}><Smartphone size={17} /></button></div><span className="preview-url">siteforge.preview</span></div><div className="preview-stage"><div className={`preview-frame ${device}`}><iframe key={`${project.id}-${project.current_version}`} title={`${project.name} preview`} src={project.preview_url} sandbox="allow-scripts allow-same-origin" /></div></div></section>
      </div>}
    </main>
  </div>
}
