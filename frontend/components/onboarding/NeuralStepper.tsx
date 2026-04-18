"use client";

import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface Step {
  id: string;
  title: string;
}

interface NeuralStepperProps {
  steps: Step[];
  currentStep: number;
}

export function NeuralStepper({ steps, currentStep }: NeuralStepperProps) {
  return (
    <div className="flex items-center justify-between gap-4 mb-20 relative">
      {/* Background linking line */}
      <div className="absolute top-1/2 left-0 right-0 h-[2px] bg-white/5 -translate-y-1/2" />
      
      {steps.map((step, idx) => {
        const isActive = idx === currentStep;
        const isCompleted = idx < currentStep;

        return (
          <div key={step.id} className="relative flex-1 flex flex-col items-center">
            {/* The Node */}
            <div className="relative z-10">
                {/* Connecting glow line for completed */}
                {isCompleted && (
                    <motion.div 
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: 1 }}
                        className="absolute top-1/2 right-[50%] h-[2px] w-[100%] bg-primary shadow-[0_0_10px_rgba(139,92,246,0.4)] -translate-y-1/2 origin-right"
                    />
                )}
                
                <motion.div
                    animate={{
                        scale: isActive ? 1.2 : 1,
                        backgroundColor: isActive || isCompleted ? "var(--primary)" : "rgba(255,255,255,0.05)",
                    }}
                    className={cn(
                        "h-4 w-4 rounded-full border border-white/10 transition-colors duration-500",
                        (isActive || isCompleted) && "border-primary shadow-[0_0_15px_rgba(139,92,246,0.6)]"
                    )}
                >
                    {isActive && (
                        <motion.div
                            animate={{ scale: [1, 1.8, 1], opacity: [0.3, 0.1, 0.3] }}
                            transition={{ repeat: Infinity, duration: 2 }}
                            className="absolute inset-0 rounded-full bg-primary"
                        />
                    )}
                </motion.div>
            </div>

            {/* Step Title Overlay */}
            <motion.div
                animate={{
                    opacity: isActive ? 1 : 0.3,
                    y: isActive ? 24 : 16
                }}
                className="absolute text-center whitespace-nowrap"
            >
                <p className="text-mono-premium text-[8px] leading-tight">Step 0{idx + 1}</p>
                <p className={cn(
                    "text-[10px] font-black uppercase tracking-widest mt-1",
                    isActive ? "text-white" : "text-slate-500"
                )}>
                    {step.title}
                </p>
            </motion.div>
          </div>
        );
      })}
    </div>
  );
}
