import { useEffect, useRef } from "react";

/** A soft, blurred blue/green gradient blob that follows the cursor across
 * the entire app. Purely decorative and non-interactive (pointer-events
 * disabled, sits behind content via z-index + isolation), updated via
 * direct style mutation on a ref rather than React state so mousemove
 * never triggers a re-render — this runs at 60fps for free.
 */
export function CursorGlow() {
  const glowRef = useRef<HTMLDivElement>(null);
  const position = useRef({ x: 0, y: 0 });
  const target = useRef({ x: 0, y: 0 });
  const frame = useRef<number | null>(null);

  useEffect(() => {
    function handleMove(e: MouseEvent) {
      target.current = { x: e.clientX, y: e.clientY };
    }

    function animate() {
      // Gentle lerp toward the cursor so the glow trails smoothly instead
      // of snapping — reads as "following" rather than "attached."
      position.current.x += (target.current.x - position.current.x) * 0.08;
      position.current.y += (target.current.y - position.current.y) * 0.08;
      if (glowRef.current) {
        glowRef.current.style.transform = `translate3d(${position.current.x}px, ${position.current.y}px, 0)`;
      }
      frame.current = requestAnimationFrame(animate);
    }

    window.addEventListener("mousemove", handleMove);
    frame.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("mousemove", handleMove);
      if (frame.current) cancelAnimationFrame(frame.current);
    };
  }, []);

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 overflow-hidden"
    >
      <div
        ref={glowRef}
        className="cursor-glow-blob absolute -left-[380px] -top-[380px] h-[760px] w-[760px]"
      />
    </div>
  );
}
