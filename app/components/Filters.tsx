"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";

type FilterField = {
  name: string;
  label: string;
  type: "text" | "number" | "date" | "select" | "checkbox";
  options?: { value: string; label: string }[];
  placeholder?: string;
};

export function Filters({ fields }: { fields: FilterField[] }) {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();

  const updateParam = useCallback(
    (name: string, value: string) => {
      const next = new URLSearchParams(params.toString());
      if (value) next.set(name, value);
      else next.delete(name);
      router.push(`${pathname}?${next.toString()}`);
    },
    [params, pathname, router],
  );

  const reset = useCallback(() => router.push(pathname), [pathname, router]);

  return (
    <div className="flex flex-wrap items-end gap-3 rounded-lg border border-neutral-800 bg-neutral-900/40 p-4">
      {fields.map((field) => (
        <FilterInput
          key={field.name}
          field={field}
          value={params.get(field.name) ?? ""}
          onChange={(v) => updateParam(field.name, v)}
        />
      ))}
      <button
        onClick={reset}
        className="rounded-md border border-neutral-700 px-3 py-2 text-sm hover:border-neutral-500"
      >
        Reset
      </button>
    </div>
  );
}

function FilterInput({
  field,
  value,
  onChange,
}: {
  field: FilterField;
  value: string;
  onChange: (v: string) => void;
}) {
  const baseInput =
    "rounded-md border border-neutral-700 bg-neutral-950 px-3 py-2 text-sm text-neutral-100 placeholder:text-neutral-500 focus:border-neutral-500 focus:outline-none";

  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wider text-neutral-500">{field.label}</span>
      {field.type === "select" ? (
        <select className={baseInput} value={value} onChange={(e) => onChange(e.target.value)}>
          <option value="">—</option>
          {(field.options ?? []).map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      ) : field.type === "checkbox" ? (
        <input
          type="checkbox"
          checked={value === "true"}
          onChange={(e) => onChange(e.target.checked ? "true" : "")}
          className="h-5 w-5"
        />
      ) : (
        <input
          type={field.type}
          value={value}
          placeholder={field.placeholder}
          onChange={(e) => onChange(e.target.value)}
          className={baseInput}
        />
      )}
    </label>
  );
}
