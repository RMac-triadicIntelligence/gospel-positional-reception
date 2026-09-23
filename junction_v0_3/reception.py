#!/usr/bin/env python3
"""A declared dynamical hypothesis, NOT an implementation of grace or restoration.
Standard library only. All live evolution is dwelling; frozen clones are assays.
"""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class State:
    x: float = -1.0
    a: float = 0.0
    t: float = 0.0

@dataclass(frozen=True)
class History:
    target: float = .31
    amplitude: float = .015
    phase: float = 0.0
    rate: float = .15
    def evidence(self, t):
        return self.target + self.amplitude * math.sin(.35*t + self.phase)

# V(x,a)=x^4/4-x^2/2-a*x; dx/dt=-dV/dx.
# da/dt is an EXPLICIT HYPOTHESIS for history-driven landscape development.
# a is bounded by the evidence profile, not by success or an outcome label.
def drift(x, a):
    return x-x*x*x+a

def step(s, h, dt, frozen=False):
    def f(x,a,t):
        return drift(x,a), 0.0 if frozen else h.rate*(h.evidence(t)-a)
    k1=f(s.x,s.a,s.t)
    k2=f(s.x+dt*k1[0]/2,s.a+dt*k1[1]/2,s.t+dt/2)
    k3=f(s.x+dt*k2[0]/2,s.a+dt*k2[1]/2,s.t+dt/2)
    k4=f(s.x+dt*k3[0],s.a+dt*k3[1],s.t+dt)
    return State(s.x+dt*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6,
                 s.a+dt*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6,s.t+dt)

def evolve(s, h, duration, dt=.02, frozen=False):
    n=max(1,math.ceil(duration/dt)); d=duration/n
    for _ in range(n): s=step(s,h,d,frozen)
    return s

def bisect_root(a,lo,hi):
    if drift(lo,a)*drift(hi,a)>0: raise ValueError('Root not bracketed')
    for _ in range(70):
        mid=(lo+hi)/2
        if drift(lo,a)*drift(mid,a)<=0: hi=mid
        else: lo=mid
    return (lo+hi)/2

def geometry(a):
    # Outside this range there is no two-basin question. Never label loss of
    # bistability as increased reception.
    critical=2/(3*math.sqrt(3))
    if abs(a)>=critical: raise ValueError('Two-basin regime absent')
    c=1/math.sqrt(3)
    return (bisect_root(a,-2,-c),bisect_root(a,-c,c),bisect_root(a,c,2))

def potential(x,a): return x**4/4-x*x/2-a*x

def capacity(s):
    left,saddle,right=geometry(s.a)
    if s.x>=saddle: raise ValueError('Snapshot is not in the left basin')
    return {'left_attractor':left,'separatrix':saddle,'right_attractor':right,
            'critical_positive_impulse':saddle-s.x,
            'barrier_from_left_attractor':potential(saddle,s.a)-potential(left,s.a)}

def predict(s, impulse, tolerance=1e-8):
    margin=impulse-capacity(s)['critical_positive_impulse']
    return 'unresolved' if abs(margin)<=tolerance else ('right' if margin>0 else 'left')

def observe(s,h,impulse,dt=.02,frozen=True,duration=24):
    # Actual assay integrates a fresh clone. It does NOT assign an outcome from
    # the predictor. Observation uses proximity to an attractor + small drift.
    end=evolve(State(s.x+impulse,s.a,s.t),h,duration,dt,frozen)
    left,_,right=geometry(end.a)
    label='unresolved'
    if abs(drift(end.x,end.a))<.015:
        if abs(end.x-left)<.03: label='left'
        elif abs(end.x-right)<.03: label='right'
    return label,end
