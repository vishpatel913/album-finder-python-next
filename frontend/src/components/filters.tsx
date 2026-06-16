import { Button } from './ui/button'
import { Checkbox } from './ui/checkbox'
import { Input } from './ui/input'
import { Label } from './ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select'

export type FilterField = {
  name: string
  label: string
  type: 'text' | 'number' | 'date' | 'select' | 'checkbox'
  options?: { value: string; label: string }[]
  placeholder?: string
}

// Controlled and framework-agnostic: the parent owns the values and decides how
// they persist (local state, URL search params, etc.). In the old Next app this
// component pushed to next/navigation directly; now it just calls back.
export interface FiltersProps {
  fields: FilterField[]
  values: Record<string, string>
  onChange: (name: string, value: string) => void
  onReset: () => void
}

export function Filters({ fields, values, onChange, onReset }: FiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-3 rounded-lg border border-neutral-800 bg-neutral-900/40 p-4">
      {fields.map((field) => (
        <FilterInput
          key={field.name}
          field={field}
          value={values[field.name] ?? ''}
          onChange={(v) => onChange(field.name, v)}
        />
      ))}
      <Button variant="outline" onClick={onReset}>
        Reset
      </Button>
    </div>
  )
}

// Radix Select has no empty-string value; this sentinel represents "no filter".
const ANY = '__any__'

function FilterInput({
  field,
  value,
  onChange,
}: {
  field: FilterField
  value: string
  onChange: (v: string) => void
}) {
  if (field.type === 'checkbox') {
    return (
      <label className="flex flex-col gap-1">
        <span className="text-xs uppercase tracking-wider text-neutral-500">{field.label}</span>
        <Checkbox
          checked={value === 'true'}
          onCheckedChange={(c) => onChange(c === true ? 'true' : '')}
        />
      </label>
    )
  }

  if (field.type === 'select') {
    return (
      <div className="flex flex-col gap-1">
        <Label>{field.label}</Label>
        <Select
          value={value === '' ? ANY : value}
          onValueChange={(v) => onChange(v === ANY ? '' : v)}
        >
          <SelectTrigger className="min-w-[10rem]">
            <SelectValue placeholder="—" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ANY}>—</SelectItem>
            {(field.options ?? []).map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    )
  }

  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wider text-neutral-500">{field.label}</span>
      <Input
        type={field.type}
        value={value}
        placeholder={field.placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  )
}
