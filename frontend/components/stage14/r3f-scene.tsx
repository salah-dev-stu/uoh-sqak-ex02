"use client";
import * as React from "react";
import { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import {
  Stars, Environment, Plane, ContactShadows, PresentationControls,
} from "@react-three/drei";
import * as THREE from "three";
import type { Speaker } from "@/lib/types";
import { R3FPodium } from "./r3f-podium";
import { SpeechBubble } from "./speech-bubble";

const COLOR_HEX: Record<Speaker, string> = {
  pro: "#4ade80", con: "#3da8ff", judge: "#ffc94c",
};

const CAMERA_TARGETS: Record<string, [number, number, number]> = {
  // Camera shifts to the OPPOSITE side of the speaker so the speaker
  // appears on the near side of the frame (Pro turn → camera on the
  // right looking left, Pro reads big in the left foreground).
  pro:     [ 3.6, 3.4, 8.6],   // camera right, look across at Pro on left
  con:     [-3.6, 3.4, 8.6],   // camera left, look across at Con on right
  judge:   [ 0,   3.6, 9.4],   // centred, a touch closer
  default: [ 0,   3.6, 10.0],
};
const LOOK_AT: [number, number, number] = [0, 2.0, 0];

function CameraDirector({ activeSpeaker }: { activeSpeaker: Speaker | null }): null {
  const targetPos = useRef(new THREE.Vector3(...CAMERA_TARGETS.default));
  useFrame(({ camera }) => {
    const key = activeSpeaker ?? "default";
    targetPos.current.set(...(CAMERA_TARGETS[key] ?? CAMERA_TARGETS.default));
    camera.position.lerp(targetPos.current, 0.035);
    camera.lookAt(LOOK_AT[0], LOOK_AT[1], LOOK_AT[2]);
  });
  return null;
}

interface BeamProps { x: number; z?: number; color: string; active: boolean }
function VolumetricBeam({ x, z = 0, color, active }: BeamProps): React.JSX.Element {
  const meshRef = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    if (!meshRef.current) return;
    const t = state.clock.elapsedTime;
    const mat = meshRef.current.material as THREE.MeshBasicMaterial;
    mat.opacity = active ? 0.32 + Math.sin(t * 2) * 0.04 : 0.10;
  });
  return (
    <mesh ref={meshRef} position={[x, 4, z]} rotation={[0, 0, 0]}>
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
      camera={{ position: [0, 3.6, 10], fov: 38 }}
      style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
      gl={{ antialias: true, alpha: false }}
      onCreated={({ scene, camera }) => {
        scene.background = new THREE.Color("#050818");
        camera.lookAt(0, 2.0, 0);
      }}
    >
      <CameraDirector activeSpeaker={activeSpeaker} />

      <ambientLight intensity={0.18} color="#3a4470" />
      <directionalLight position={[0, 8, 4]} intensity={0.35} color="#7080a0" />

      <fog attach="fog" args={["#050818", 8, 22]} />

      <PresentationControls
        global
        cursor
        snap
        speed={1}
        zoom={1}
        rotation={[0, 0, 0]}
        polar={[-Math.PI / 28, Math.PI / 28]}
        azimuth={[-Math.PI / 8, Math.PI / 8]}
      >
        <Stars radius={50} depth={40} count={2200} factor={3} saturation={0.4} fade speed={0.4} />

        <Plane args={[40, 40]} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
          <meshStandardMaterial color="#0a1230" metalness={0.55} roughness={0.55} />
        </Plane>
        <gridHelper args={[40, 40, "#1c2440", "#11182d"]} position={[0, 0.001, 0]} />

        <ContactShadows position={[0, 0.005, 0]} opacity={0.5} scale={20} blur={2.6} far={5} color="#000" />

        <Plane args={[60, 4]} position={[0, 1, -8]} rotation={[0, 0, 0]} receiveShadow>
          <meshStandardMaterial color="#070b1e" metalness={0.1} roughness={0.9} />
        </Plane>

        <VolumetricBeam x={-3} z={0}   color={COLOR_HEX.pro}   active={activeSpeaker === "pro"} />
        <VolumetricBeam x={0}  z={1.2} color={COLOR_HEX.judge} active={activeSpeaker === "judge"} />
        <VolumetricBeam x={3}  z={0}   color={COLOR_HEX.con}   active={activeSpeaker === "con"} />

        <R3FPodium speaker="pro"   position={[-3, 0, 0]}   rotationY={0.22}  active={activeSpeaker === "pro"} />
        <R3FPodium speaker="judge" position={[0, 0, 1.2]}  rotationY={0}     active={activeSpeaker === "judge"} />
        <R3FPodium speaker="con"   position={[3, 0, 0]}    rotationY={-0.22} active={activeSpeaker === "con"} />

        <SpeechBubble />
      </PresentationControls>

      <Environment preset="night" />
    </Canvas>
  );
}
