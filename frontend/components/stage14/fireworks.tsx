"use client";
import * as React from "react";
import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const PARTICLES = 64;
const CYCLE_S = 1.9;
const GRAVITY = 1.8;

interface BurstProps {
  origin: [number, number, number];
  color: string;
  offset: number;
}

function FireworkBurst({ origin, color, offset }: BurstProps): React.JSX.Element {
  const ref = useRef<THREE.Points>(null);
  const positions = useMemo(() => new Float32Array(PARTICLES * 3), []);
  const velocities = useMemo(() => new Float32Array(PARTICLES * 3), []);

  const reseed = (): void => {
    for (let i = 0; i < PARTICLES; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const sp = 2 + Math.random() * 2.6;
      velocities[i * 3] = sp * Math.sin(phi) * Math.cos(theta);
      velocities[i * 3 + 1] = sp * Math.sin(phi) * Math.sin(theta) + 1.4;
      velocities[i * 3 + 2] = sp * Math.cos(phi);
    }
  };
  useMemo(() => reseed(), []);

  useFrame((state) => {
    if (!ref.current) return;
    const t = state.clock.elapsedTime + offset;
    const phase = t % CYCLE_S;
    if (phase < 0.05) reseed();
    const dt = phase;
    for (let i = 0; i < PARTICLES; i++) {
      positions[i * 3] = velocities[i * 3] * dt;
      positions[i * 3 + 1] = velocities[i * 3 + 1] * dt - 0.5 * GRAVITY * dt * dt;
      positions[i * 3 + 2] = velocities[i * 3 + 2] * dt;
    }
    ref.current.geometry.attributes.position.needsUpdate = true;
    const fade = Math.max(0, 1 - phase / CYCLE_S);
    const mat = ref.current.material as THREE.PointsMaterial;
    mat.opacity = fade;
  });

  return (
    <points ref={ref} position={origin}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position"
          args={[positions, 3]}
          array={positions} count={PARTICLES} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.2} color={color} transparent
        sizeAttenuation blending={THREE.AdditiveBlending} depthWrite={false} />
    </points>
  );
}

interface FireworksProps {
  winner: "pro" | "con" | null;
}

export function Fireworks({ winner }: FireworksProps): React.JSX.Element | null {
  if (!winner) return null;
  const x = winner === "pro" ? -3 : 3;
  const accent = winner === "pro" ? "#4ade80" : "#3da8ff";
  return (
    <>
      <FireworkBurst origin={[x - 1.4, 3.6, -2.5]} color={accent} offset={0} />
      <FireworkBurst origin={[x + 1.4, 4.4, -3.0]} color={accent} offset={0.65} />
      <FireworkBurst origin={[x,       5.2, -2.2]} color="#ffd76b" offset={1.3} />
      <FireworkBurst origin={[x - 0.6, 4.0, -1.8]} color="#ffffff" offset={1.9} />
    </>
  );
}
