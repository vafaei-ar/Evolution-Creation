# Model 03: time-varying connectivity

## Question

How does the timing of isolation or renewed contact change the spread of genealogical ancestry?

Model 02 treats connectivity as fixed. Model 03 allows the migration matrix to change from one reproductive transition to the next.

## Time convention

A schedule contains one migration matrix per reproductive transition.

Schedule index 0 produces generation 1 from generation 0.

Therefore:

- barrier_start = 1 means the barrier exists from the first transition.
- barrier_start = 21 means generations 1 through 20 are produced while connected, and the transition producing generation 21 is the first blocked one.
- barrier_start = generations + 1 means the barrier never activates during the simulated period.

The active interval is [barrier_start, barrier_end). If barrier_end is None, the barrier remains active through the final transition.

## Four scenarios

### Permanent isolation from the start

If the founder starts on one side, the disconnected component cannot acquire that ancestry.

### Delayed isolation

The system begins connected and later splits. If founder ancestry crosses before the split, later isolation cannot erase that ancestry.

### Delayed contact

The system begins isolated and later reconnects. Founder ancestry remains confined until contact begins.

### Temporary isolation

A barrier appears for a finite interval and later disappears. This can delay spread without making it impossible.

## Structural conclusion

A statement such as "population X was isolated" is incomplete for genealogy. We need to know when isolation began, whether ancestry crossed before isolation, whether isolation remained complete, and whether later contact occurred.

The figures in the README use illustrative small populations and Monte Carlo simulation. They are not estimates of prehistoric human migration or isolation.
