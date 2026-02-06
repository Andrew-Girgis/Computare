"use client";

import { useRef, useState, useCallback, type ReactNode } from "react";

export function ShineHeadline({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLHeadingElement>(null);
  const [gradient, setGradient] = useState<string | undefined>(undefined);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLHeadingElement>) => {
      const el = ref.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      setGradient(
        `radial-gradient(circle 120px at ${x}px ${y}px, var(--color-gold) 0%, var(--color-ink) 100%)`
      );
    },
    []
  );

  const handleMouseLeave = useCallback(() => {
    setGradient(undefined);
  }, []);

  return (
    <h1
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={className}
      style={{
        padding: "0.1em 0.15em",
        margin: "-0.1em -0.15em",
        ...(gradient
          ? {
              backgroundImage: gradient,
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              WebkitTextFillColor: "transparent",
              transition: "none",
            }
          : {}),
      }}
    >
      {children}
    </h1>
  );
}
