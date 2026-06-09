"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";
import { Button } from "@/app/components/ui/button";
import { Checkbox } from "@/app/components/ui/checkbox";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";

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
      <Button variant="outline" onClick={reset}>
        Reset
      </Button>
    </div>
  );
}

// Radix Select has no empty-string value; this sentinel represents "no filter".
const ANY = "__any__";

function FilterInput({
  field,
  value,
  onChange,
}: {
  field: FilterField;
  value: string;
  onChange: (v: string) => void;
}) {
  if (field.type === "checkbox") {
    return (
      <label className="flex flex-col gap-1">
        <span className="text-xs uppercase tracking-wider text-neutral-500">{field.label}</span>
        <Checkbox
          checked={value === "true"}
          onCheckedChange={(c) => onChange(c === true ? "true" : "")}
        />
      </label>
    );
  }

  if (field.type === "select") {
    return (
      <div className="flex flex-col gap-1">
        <Label>{field.label}</Label>
        <Select
          value={value === "" ? ANY : value}
          onValueChange={(v) => onChange(v === ANY ? "" : v)}
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
    );
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
  );
}
