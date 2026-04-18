"use client";

import React from "react";
import { motion } from "framer-motion";

export function AmbientOrbs() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      {/* Primary Glow */}
      <motion.div
        animate={{
          x: [0, 100, -50, 0],
          y: [0, -50, 100, 0],
          scale: [1, 1.2, 0.9, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute top-[-10%] left-[-10%] h-[600px] w-[600px] rounded-full bg-primary/20 blur-[120px]"
      />
      
      {/* Secondary Glow */}
      <motion.div
        animate={{
          x: [0, -120, 80, 0],
          y: [0, 100, -40, 0],
          scale: [1, 1.1, 1.3, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute bottom-[-10%] right-[-10%] h-[500px] w-[500px] rounded-full bg-indigo-500/10 blur-[100px]"
      />
      
      {/* Accent Glow */}
      <motion.div
        animate={{
          opacity: [0.3, 0.6, 0.3],
          scale: [1, 1.5, 1],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-[30%] left-[40%] h-[300px] w-[300px] rounded-full bg-fuchsia-500/10 blur-[150px]"
      />
    </div>
  );
}
