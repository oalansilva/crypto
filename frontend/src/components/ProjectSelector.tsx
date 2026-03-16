import { useQuery } from '@tanstack/react-query'
import { FolderKanban } from 'lucide-react'
import { API_BASE_URL } from '@/lib/apiBase'

export type Project = {
  id: string
  slug: string
  name: string
}

type ProjectSelectorProps = {
  selectedProject: string
  onProjectChange: (projectSlug: string) => void
}

export function ProjectSelector({ selectedProject, onProjectChange }: ProjectSelectorProps) {
  const { data: projects, isLoading, error } = useQuery<Project[]>({
    queryKey: ['workflow', 'projects'],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/workflow/projects`)
      if (!res.ok) throw new Error(`Failed to load projects (${res.status})`)
      return res.json()
    },
    refetchOnWindowFocus: false,
  })

  return (
    <div className="flex items-center gap-2">
      <FolderKanban className="w-4 h-4 text-gray-400" />
      <select
        value={selectedProject}
        onChange={(e) => onProjectChange(e.target.value)}
        disabled={isLoading}
        className="h-9 min-w-[140px] rounded-lg border border-white/10 bg-white/5 px-3 text-sm text-gray-100 focus:outline-none focus:ring-2 focus:ring-cyan-400/30 disabled:opacity-50"
        aria-label="Selecionar projeto"
      >
        {isLoading ? (
          <option value="">Carregando...</option>
        ) : error ? (
          <option value="">Erro ao carregar</option>
        ) : (
          projects?.map((project) => (
            <option key={project.id} value={project.slug}>
              {project.name}
            </option>
          ))
        )}
      </select>
    </div>
  )
}
