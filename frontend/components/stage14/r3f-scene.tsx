"use client";
import * as React from "react";
import { useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Stars, Environment, Plane, ContactShadows } from "@react-three/drei";
import * as THREE from "three";
import type { Speaker } from "@/lib/types";
import { R3FPodium } from "./r3f-podium";

const COLOR_HEX: Record<Speaker, string> = {
  pro: "#ff3da8", con: "#3da8ff", judge: "#ffc94c",
};

function CursorCamera({ active }: { active: Speaker | null }): null {
  const { camera, pointer } = useThree();
  const target = useRef(new THREE.Vector3(0, 2.2, 0));
  useFrame(() => {
    const offsetX = active === "pro" ? -0.7 : active === "con" ? 0.7 : 0;
    const dx = pointer.x * 0.4 + offsetX;
    const dy = pointer.y * 0.2;
    camera.position.x += (dx - camera.position.x) * 0.05;
    camera.position.y += (2.7 + dy - camera.position.y) * 0.05;
    camera.position.z = 6.5;
    camera.lookAt(target.current);
  });
  return null;
}

function VolumetricBeam({ x, color, active }: { x: number; color: string; active: boolean }): React.JSX.Element {
  const meshRef = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    if (!meshRef.current) return;
    const t = state.clock.elapsedTime;
    const mat = meshRef.current.material as THREE.MeshBasicMaterial;
    mat.opacity = active ? 0.32 + Math.sin(t * 2) * 0.04 : 0.10;
  });
  return (
    <mesh ref={meshRef} position={[x, 4, -0.5]} rotation={[0, 0, 0]}>
      <coneGeometry args={[1.4, 6, 32, 1, true]} />
      <meshBasicMaterial color={color} transparent opacity={0.25}
        side={THREE.DoubleSide} blending={THREE.AdditiveBlending} depthWrite={false} />
    </mesh>
  );
}

interface Props {
  activeSpeaker: Speaker | null;
}

export function R3FScene({ activeSpeaker }: Props): React.JSX.Element {
  return (
    <Canvas
      shadows
      dpr={[1, 2]}
      camera={{ position: [0, 2.7, 6.5], fov: 50 }}
      style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
      gl={{ antialias: true, alpha: false }}
      onCreated={({ scene }) => { scene.background = new THREE.Color("#050818"); }}
    >
      <CursorCamera active={activeSpeaker} />

      <ambientLight intensity={0.18} color="#3a4470" />
      <directionalLight position={[0, 8, 4]} intensity={0.35} color="#7080a0" />

      <fog attach="fog" args={["#050818", 8, 22]} />

      <Stars radius={50} depth={40} count={2200} factor={3} saturation={0.4} fade speed={0.4} />

      <Plane args={[40, 40]} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <meshStandardMaterial color="#0a1230" metalness={0.55} roughness={0.55} />
      </Plane>
      <gridHelper args={[40, 40, "#1c2440", "#11182d"]} position={[0, 0.001, 0]} />

      <ContactShadows position={[0, 0.005, 0]} opacity={0.5} scale={20} blur={2.6} far={5} color="#000" />

      <Plane args={[60, 4]} position={[0, 1, -8]} rotation={[0, 0, 0]} receiveShadow>
        <meshStandardMaterial color="#070b1e" metalness={0.1} roughness={0.9} />
      </Plane>

      <VolumetricBeam x={-3} color={COLOR_HEX.pro} active={activeSpeaker === "pro"} />
      <VolumetricBeam x={0} color={COLOR_HEX.judge} active={activeSpeaker === "judge"} />
      <VolumetricBeam x={3} color={COLOR_HEX.con} active={activeSpeaker === "con"} />

      <R3FPodium speaker="pro"   position={[-3, 0, 0]}   rotationY={0.22}  active={activeSpeaker === "pro"} />
      <R3FPodium speaker="judge" position={[0, 0, 1.2]}  rotationY={0}     active={activeSpeaker === "judge"} />
      <R3FPodium speaker="con"   position={[3, 0, 0]}    rotationY={-0.22} active={activeSpeaker === "con"} />

      <Environment preset="night" />
    </Canvas>
  );
}
