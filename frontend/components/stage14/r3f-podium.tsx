"use client";
import * as React from "react";
import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { RoundedBox, Capsule, Html, Text } from "@react-three/drei";
import * as THREE from "three";
import type { Speaker } from "@/lib/types";

const COLOR_HEX: Record<Speaker, string> = {
  pro:   "#4ade80",
  con:   "#3da8ff",
  judge: "#ffc94c",
};
const GLYPH: Record<Speaker, string> = { pro: "P", con: "C", judge: "⚖" };
const NAME: Record<Speaker, string> = { pro: "PRO", con: "CON", judge: "JUDGE" };

interface Props {
  speaker: Speaker;
  position: [number, number, number];
  rotationY: number;
  active: boolean;
}

export function R3FPodium({ speaker, position, rotationY, active }: Props): React.JSX.Element {
  const groupRef = useRef<THREE.Group>(null);
  const lightRef = useRef<THREE.PointLight>(null);
  const colour = COLOR_HEX[speaker];
  const emissive = active ? 1.5 : 0.25;

  useFrame((state) => {
    if (!groupRef.current) return;
    const t = state.clock.elapsedTime;
    groupRef.current.position.y = position[1] + (active ? Math.sin(t * 1.4) * 0.04 : 0);
    if (lightRef.current) {
      lightRef.current.intensity = active ? 8 + Math.sin(t * 3) * 0.6 : 1.5;
    }
  });

  return (
    <group ref={groupRef} position={position} rotation={[0, rotationY, 0]}>
      <pointLight ref={lightRef} position={[0, 2.5, 0.6]} color={colour}
        intensity={active ? 8 : 1.5} distance={5} decay={1.8} />

      <RoundedBox args={[1.6, 1.9, 1.1]} radius={0.08} smoothness={4} position={[0, 0.95, 0]} castShadow receiveShadow>
        <meshStandardMaterial color="#0e1428" metalness={0.4} roughness={0.55}
          emissive={colour} emissiveIntensity={active ? 0.12 : 0.04} />
      </RoundedBox>
      <RoundedBox args={[1.7, 0.12, 1.2]} radius={0.04} smoothness={4} position={[0, 1.95, 0]} castShadow>
        <meshStandardMaterial color={colour} metalness={0.6} roughness={0.3}
          emissive={colour} emissiveIntensity={active ? 0.8 : 0.25} />
      </RoundedBox>
      <mesh position={[0, 1.1, 0.56]}>
        <ringGeometry args={[0.28, 0.36, 48]} />
        <meshStandardMaterial color={colour} emissive={colour}
          emissiveIntensity={active ? 1.4 : 0.6} side={THREE.DoubleSide} />
      </mesh>
      <Text position={[0, 1.1, 0.58]} fontSize={0.32}
        color={colour} anchorX="center" anchorY="middle"
        outlineWidth={0.005} outlineColor={colour}
        outlineOpacity={active ? 0.6 : 0.25}>
        {GLYPH[speaker]}
      </Text>

      <mesh position={[-0.3, 2.05, 0.3]} rotation={[0, 0, Math.PI / 4]}>
        <cylinderGeometry args={[0.012, 0.012, 0.5, 8]} />
        <meshStandardMaterial color="#1a1f2e" metalness={0.8} roughness={0.4} />
      </mesh>
      <mesh position={[-0.13, 2.22, 0.42]}>
        <capsuleGeometry args={[0.04, 0.08, 4, 8]} />
        <meshStandardMaterial color="#0a0f1e" metalness={0.9} roughness={0.3}
          emissive={colour} emissiveIntensity={active ? 0.4 : 0.1} />
      </mesh>

      <Capsule args={[0.32, 0.6, 4, 12]} position={[0, 2.55, -0.05]} castShadow>
        <meshStandardMaterial color="#0a1024" metalness={0.3} roughness={0.65}
          emissive={colour} emissiveIntensity={active ? 0.3 : 0.08} />
      </Capsule>
      <mesh position={[0, 3.15, -0.05]} castShadow>
        <sphereGeometry args={[0.35, 24, 24]} />
        <meshStandardMaterial color="#0e1530" metalness={0.4} roughness={0.55}
          emissive={colour} emissiveIntensity={active ? 0.45 : 0.12} />
      </mesh>
      <mesh position={[0, 3.15, 0.32]}>
        <ringGeometry args={[0.18, 0.22, 32]} />
        <meshStandardMaterial color={colour} emissive={colour}
          emissiveIntensity={active ? emissive : 0.4} side={THREE.DoubleSide} />
      </mesh>

      <Html position={[0, 0.4, 0.58]} center
        style={{ pointerEvents: "none",
          fontFamily: "var(--font-mono)", fontSize: "11px",
          letterSpacing: "0.25em", fontWeight: 700,
          color: colour, opacity: active ? 1 : 0.55,
          textShadow: active ? `0 0 10px ${colour}` : "none" }}>
        {NAME[speaker]}
      </Html>
    </group>
  );
}
