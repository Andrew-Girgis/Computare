"use client";

import { useEffect, useRef, useState } from "react";

function TypewriterLine({
  text,
  className = "",
  speed = 35,
  active = false,
  onComplete,
}: {
  text: string;
  className?: string;
  speed?: number;
  active?: boolean;
  onComplete?: () => void;
}) {
  const [visible, setVisible] = useState(0);

  useEffect(() => {
    if (!active) return;
    if (visible >= text.length) {
      onComplete?.();
      return;
    }

    const timeout = setTimeout(() => {
      setVisible((v) => v + 1);
    }, speed);

    return () => clearTimeout(timeout);
  }, [active, visible, text.length, speed, onComplete]);

  return (
    <div className={className}>
      <span>{text.slice(0, visible)}</span>
    </div>
  );
}

export function ScrollTypewriterSequence({
  lines,
  className = "",
  lineClassName = "",
  speed = 35,
  pauseBetween = 300,
}: {
  lines: string[];
  className?: string;
  lineClassName?: string;
  speed?: number;
  pauseBetween?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [activeLine, setActiveLine] = useState(-1);

  // Trigger on scroll into view
  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setActiveLine(0);
          observer.unobserve(el);
        }
      },
      { threshold: 0.15 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className={className}>
      {lines.map((text, i) => (
        <TypewriterLine
          key={i}
          text={text}
          className={lineClassName}
          speed={speed}
          active={activeLine === i}
          onComplete={() => {
            setTimeout(() => setActiveLine(i + 1), pauseBetween);
          }}
        />
      ))}
    </div>
  );
}
