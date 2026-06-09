"use client";

import * as React from "react";
import * as CheckboxPrimitive from "@radix-ui/react-checkbox";
import { cn } from "@/app/lib/cn";

const CheckIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
    <path d="M20 6 9 17l-5-5" />
  </svg>
);

export const Checkbox = React.forwardRef<
  React.ElementRef<typeof CheckboxPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root>
>(({ className, ...props }, ref) => (
  <CheckboxPrimitive.Root
    ref={ref}
    className={cn(
      "flex h-5 w-5 items-center justify-center rounded border border-neutral-700 bg-neutral-950 focus:outline-none focus-visible:ring-2 focus-visible:ring-neutral-400 data-[state=checked]:border-neutral-100 data-[state=checked]:bg-neutral-100 data-[state=checked]:text-neutral-900",
      className,
    )}
    {...props}
  >
    <CheckboxPrimitive.Indicator>
      <CheckIcon />
    </CheckboxPrimitive.Indicator>
  </CheckboxPrimitive.Root>
));
Checkbox.displayName = "Checkbox";
