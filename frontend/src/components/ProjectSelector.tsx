import { useQuery } from '@tanstack/react-query'
import { FolderKanban } from 'lucide-react'
import { API_BASE_URL } from '@/lib/apiBase'
import { Dropdown } from '@/components/ui/DropdownMenu'

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

  const options = projects?.map((project) => ({
    value: project.slug,
    label: project.name,
    icon: <FolderKanban className="w-4 h-4 text-gray-400" />,
  })) || []

  if (isLoading) {
    return (
      <div className="flex items-center gap-2">
        <FolderKanban className="w-4 h-4 text-gray-400" />
        <div className="h-9 min-w-[140px] rounded-lg border border-white/10 bg-white/5 px-3 animate-pulse">
          <div className="h-4 w-20 bg-white/10 rounded mt-2.5" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center gap-2">
        <FolderKanban className="w-4 h-4 text-red-400" />
        <span className="text-sm text-red-400">Erro ao carregar</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <FolderKanban className="w-4 h-4 text-gray-400" />
      <Dropdown
        options={options}
        value={selectedProject}
        onChange={onProjectChange}
        placeholder="Selecionar projeto..."
      />
    </div>
  )
}
