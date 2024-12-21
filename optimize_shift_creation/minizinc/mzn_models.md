## Version 1
- calculates an upper bound of shifts
- `starts_at[shift]`, `lenght[shift]`  create 2 arrays of that quantity of elelments representing possible shifts, one is for start time, and the other for the length
- `active_riders_at_t` = num of shifts active at t, create another array that says if a shift is active 
- `slack` variable from active riders at t to rider demand

### Symmetry breaking:
- send all non active shifts at the end of array
- longest shifts should be before (?)
- if same length -> sort starts asc

### Dominance: 
- if len = 4 is possible cannot be 2 consec len=2 and similar


## Version 2
- creat all posible combinations of start time and shift length
- `q_shifts[start_time, length]` variable is an 2d array that reperesnts the number of shifts by start time and length
- `active_riders_at_t` = num of shifts active at t
- `slack` variable from active riders at t to rider demand

### Dominance: 
- if len = 4 is possible cannot be 2 consec len=2 and similar


## Version 3
- improves version 1 creating 2 variables:
- `shifts_at_t[t] = {set of shifts}` = set of shifts tht are active at t -> sum at t is `active_riders_at_t`
- `times_for_shifts = {set of times}` = set of times where a shift is active
- `inverse_set(times_for_shifts, shifts_at_t)` inverse between shifts_at_t and times_for_shifts
- same symmetry breaking and dominance as in version 1


Considerations discarded
- `cumulative`  constraint: the total should be an **int** , and here the total is changing at each t (rider demand).
- `diffn` for **packing**, is suboptimal since it requires keeping the "shapes" (in this cases the shifts).


## Ideas for future: 
- `regular` to enforce seq of events to optimize routing?
https://docs.minizinc.dev/en/stable/predicates.html#ex-nurse
