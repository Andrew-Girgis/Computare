"use client";

import { useEffect, useRef, useState, useCallback } from "react";

const TOTAL_FRAMES = 90;
const FRAME_NAMES = Array.from(
  { length: TOTAL_FRAMES },
  (_, i) => `frame_${String(i).padStart(3, "0")}-ascii-art.txt`
);

class AnimationManager {
  private raf: number | null = null;
  private lastFrame = -1;
  private frameTime: number;
  private callback: () => void;

  constructor(callback: () => void, fps = 24) {
    this.callback = callback;
    this.frameTime = 1000 / fps;
  }

  start() {
    if (this.raf != null) return;
    this.raf = requestAnimationFrame(this.update);
  }

  pause() {
    if (this.raf == null) return;
    this.lastFrame = -1;
    cancelAnimationFrame(this.raf);
    this.raf = null;
  }

  private update = (time: number) => {
    if (this.lastFrame === -1) {
      this.lastFrame = time;
    } else {
      let delta = time - this.lastFrame;
      while (delta >= this.frameTime) {
        this.callback();
        delta -= this.frameTime;
        this.lastFrame += this.frameTime;
      }
    }
    this.raf = requestAnimationFrame(this.update);
  };
}

export function ASCIIAnimation({
  className = "",
  fps = 24,
  basePath = "/ascii/soj_ascii_frames",
}: {
  className?: string;
  fps?: number;
  basePath?: string;
}) {
  const [frames, setFrames] = useState<string[]>([]);
  const [current, setCurrent] = useState(0);
  const framesRef = useRef<string[]>([]);
  const preRef = useRef<HTMLPreElement>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;

    let cancelled = false;

    async function load() {
      const batchSize = 10;
      const loaded: string[] = [];

      for (let i = 0; i < FRAME_NAMES.length; i += batchSize) {
        if (cancelled) return;
        const batch = FRAME_NAMES.slice(i, i + batchSize);
        const results = await Promise.all(
          batch.map(async (name) => {
            const res = await fetch(`${basePath}/${name}`);
            if (!res.ok) return "";
            return res.text();
          })
        );
        loaded.push(...results);

        if (i === 0 && !cancelled) {
          framesRef.current = [...loaded];
          setFrames([...loaded]);
          setCurrent(0);
        } else if (!cancelled) {
          framesRef.current = [...loaded];
          setFrames([...loaded]);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [basePath, mounted]);

  const advance = useCallback(() => {
    setCurrent((c) =>
      framesRef.current.length === 0 ? c : (c + 1) % framesRef.current.length
    );
  }, []);

  const [manager] = useState(() => new AnimationManager(advance, fps));

  useEffect(() => {
    if (frames.length === 0) return;

    const reducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;
    if (reducedMotion) return;

    const onFocus = () => manager.start();
    const onBlur = () => manager.pause();

    window.addEventListener("focus", onFocus);
    window.addEventListener("blur", onBlur);

    if (document.visibilityState === "visible") {
      manager.start();
    }

    return () => {
      window.removeEventListener("focus", onFocus);
      window.removeEventListener("blur", onBlur);
      manager.pause();
    };
  }, [manager, frames.length]);

  useEffect(() => {
    if (preRef.current && frames[current]) {
      preRef.current.textContent = frames[current];
    }
  }, [current, frames]);

  if (!mounted || frames.length === 0) return null;

  return (
    <pre
      ref={preRef}
      className={className}
      style={{ fontFamily: "monospace" }}
      aria-hidden="true"
    >
      {frames[0]}
    </pre>
  );
}