"use client";
import * as React from "react";
import { useEffect, useSyncExternalStore } from "react";
import { motion, useScroll, useTransform, type MotionValue } from "motion/react";
import type Lenis from "lenis";
import { Slide } from "./slide";
import { getState, subscribe, setState } from "@/lib/state";
import { useLenis } from "./lenis-provider";
import type { Slide as SlideT } from "@/lib/types";

function useStoreState() {
  return useSyncExternalStore(subscribe, getState, getState);
}

interface ScrollSlideProps {
  slide: SlideT;
  index: number;
  total: number;
  scrollYProgress: MotionValue<number>;
  isLatest: boolean;
}

function ScrollSlide({
  slide,
  index,
  total,
  scrollYProgress,
  isLatest,
}: ScrollSlideProps): React.JSX.Element {
  const startProgress = index / total;
  const endProgress = (index + 1) / total;
  const fadeBand = 0.3 / total;
  const opacity = useTransform(
    scrollYProgress,
    [startProgress, startProgress + fadeBand, endProgress - fadeBand, endProgress],
    [0, 1, 1, 0],
  );
  const y = useTransform(
    scrollYProgress,
    [startProgress, startProgress + fadeBand, endProgress - fadeBand, endProgress],
    [24, 0, 0, -24],
  );

  return (
    <motion.div style={{ position: "absolute", inset: 0, opacity, y }}>
      <Slide slide={slide} index={index} isLatest={isLatest} />
    </motion.div>
  );
}

export function Stage(): React.JSX.Element {
  const state = useStoreState();
  const lenis = useLenis();
  const { scrollYProgress } = useScroll();
  const slidesCount = state.slides.length;

  // Auto-follow: when a new slide arrives and followLive is on, smooth-scroll to it.
  useEffect(() => {
    if (slidesCount === 0 || !state.followLive || !lenis) return;
    const target = (slidesCount - 1) * window.innerHeight;
    lenis.scrollTo(target, { duration: 0.7 });
  }, [slidesCount, state.followLive, lenis]);

  // Detect user scrolling up — pause auto-follow.
  useEffect(() => {
    if (!lenis) return;
    let lastY = 0;
    // Lenis "scroll" callback signature is (lenis: Lenis) => void; read scroll
    // position from the instance rather than the callback argument.
    const onScroll = (instance: Lenis) => {
      const scroll = instance.scroll;
      const userScrolledUp = scroll < lastY - 4;
      lastY = scroll;
      const idx = Math.round(scroll / window.innerHeight);
      const latest = state.slides.length - 1;
      if (userScrolledUp && idx < latest && state.followLive) setState({ followLive: false });
      if (state.currentIndex !== idx) setState({ currentIndex: idx });
    };
    const off = lenis.on("scroll", onScroll);
    return () => {
      if (typeof off === "function") off();
      else lenis.off("scroll", onScroll);
    };
  }, [lenis, state.followLive, state.currentIndex, state.slides.length]);

  if (slidesCount === 0) return <></>;

  return (
    <div style={{ height: `${slidesCount * 100}vh`, position: "relative" }}>
      <div style={{ position: "sticky", top: 0, height: "100vh", overflow: "hidden" }}>
        {state.slides.map((s, i) => (
          <ScrollSlide
            key={s.id}
            slide={s}
            index={i}
            total={slidesCount}
            scrollYProgress={scrollYProgress}
            isLatest={i === slidesCount - 1}
          />
        ))}
      </div>
    </div>
  );
}
