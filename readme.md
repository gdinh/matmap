# MoST: MOdular Scheduling Transforms

A representation for higher-level transforms, with tools to generate [SysTL](https://github.com/ChezJrk/SYS_ATL) code.

Source organization:

```
├── docs - not just documentation, but papers, working drafts, etc.
├── schedules - programs to generate schedule description objects (e.g. HBL autotiler, CoSA, etc.)
└── src - MoST object definitions, etc.
    └── schedule_representation.py
```

Design goals can be found under docs/design-goals-and-overview.lyx.

Currently working on:
- abstract MOST description object
- Interface with SysTL (to apply transforms via SysTL, etc.))

Next TODOs:
- [CoSA](https://github.com/ucb-bar/cosa) transform
- HBL autotiling for CNNs (pending on Riley's solver)
- HBL autotiling for projective nested loops (pending on Riley's solver)