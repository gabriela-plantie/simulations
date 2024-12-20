int: min_len;
int: max_len;
int: times;


include "inverse_set.mzn";

set of int: TIME = 1..times;
array[TIME] of int: rider_demand; 

%int: max_shift;


set of int: TIME_PLUS = 1..times+1;
set of int: LENGTH = min(min_len, times)..min(max_len, times);
set of int: LENGTH_0 = {0} union min(min_len, times)..min(max_len, times);
set of int: DEMAND = 1..max(rider_demand);


int: max_shift = ceil(max(t in TIME)(rider_demand[t]) * ceil(times/min_len));
        
set of int: SHIFT = 1..max_shift;
set of int: SHIFT_0 = 0..max_shift;



set of int: SLACK = -max(rider_demand)..max(rider_demand);


array[SHIFT] of var TIME_PLUS: starts_at; 
array[SHIFT] of var LENGTH_0: length; 




array[TIME] of var 0..max(rider_demand): active_riders_at_t;
array[TIME] of var SLACK: slack; 




var 0..max_shift: active_shifts;
var 0..max(rider_demand)*times: slack_sum;




%in each time sum shifts covering 
constraint forall(t in TIME)(
	active_riders_at_t[t] = sum(s in SHIFT)(
				(starts_at[s] <= t) 
				/\ 
				(starts_at[s] + length[s] - 1 >= t)
				)
				);
				
				
				

		
				
constraint forall(t in TIME)(
		rider_demand[t] =  active_riders_at_t[t] + slack[t] 
		);
		

constraint forall(s in SHIFT) (
	if active_shift[s] then
		(starts_at[s] + length[s] - 1 <= times)
		else starts_at[s] = times+1 
		endif );


constraint forall(s in SHIFT) (
	(not active_shift[s]) <-> (starts_at[s] == times + 1)	
	);




% constraint cumulative(starts_at, length, [1| i in 1..max_shift], rider_demand);


% symmetry breaking

% all non used shifts at the end
constraint forall(s in 1..max_shift-1)(
    (not active_shift[s]) -> (
    	(length[s+1] = 0) /\ (starts_at[s+1] = times+1) /\ (starts_at[s] = times+1)
    	
    	)
);


% sorting first by longest 
constraint forall(i in 1..max_shift-1)(
	length[i] >= length[i+1]
	);



% if shifts same len, their length should be ordered by start
constraint forall(i, j in SHIFT where i < j)(
    (if length[i] == length[j] then starts_at[i] <= starts_at[j] endif)
);



constraint active_shifts = sum(s in SHIFT)(active_shift[s]);
constraint slack_sum = sum(t in TIME)(abs(slack[t]));




% dominance
% no puede haber 2 consecutivos de 1, si hay posibles de 2
% no puede haber 3 consecutivos de 1, si hay posibles de 3
% no puede haber 2 consecutivos de 2, si hay posibles de 4

constraint forall(i in 1..max_shift-1)(
	if (min_len <= 2) /\ (2 <= max_len) /\ 
	(starts_at[i] + 1 == starts_at[i+1]) 
	/\ (length[i+1] = 1) then (length[i] > 1)
	endif  
	);




constraint forall(i in 1..max_shift-2)(
	if 
	((min_len <= 2) /\ (2 <= max_len) /\ 
	(starts_at[i] + 1 == starts_at[i+1]) /\
	(starts_at[i] + 2 == starts_at[i+2]) /\
	(length[i+2] == 1) 
	) then ((length[i] >= 2) /\ (length[i+1] >= 2))
	endif  
	);
	
	
% lower area will be filled with longest shifts
constraint 
	if (
		(times / max_len >= 1) /\ 
		(times mod max_len = 0) 
		)
	then forall(s in SHIFT)(if s <= (min(rider_demand) * times/max_len) then length[s] = max_len endif)
	%then forall(s in SHIFT)(if s <= min(rider_demand)  then length[s] = max_len /\ starts_at[s] = 1 endif)
	endif;	
	
%constraint starts_at[1] = 1;
	


solve minimize slack_sum * (max_shift + 1) + active_shifts;

%constraint table([x,y,z], [| 0,0,0 | 1,2,3 | 4,2,0 |])


% predicate inverse_set(array [$$X] of var set of $$Y: f,
%                       array [$$Y] of var set of $$X: invf)



% % set of times for each s

array[SHIFT] of var set of TIME_PLUS: times_for_shifts;  % array of sets


constraint forall (s in SHIFT)(
	times_for_shifts[s] = {t | t in starts_at[s]..starts_at[s] + length[s]-1}
	);


array[TIME] of var set of SHIFT_0: shifts_at_t;
constraint forall(t in TIME)(
	shifts_at_t[t] = {
		if (
			(starts_at[s] <= t) /\ (starts_at[s] + length[s] - 1 >= t)
			)
		then s else 0 endif | s in SHIFT
		} diff {0});


constraint inverse_set(
		times_for_shifts,
		shifts_at_t
		);


constraint forall(t in TIME)(card(shifts_at_t[t]) == active_riders_at_t[t]); 

constraint forall(s in SHIFT where active_shift[s])(max(times_for_shifts[s]) - min(times_for_shifts[s]) + 1 = card(times_for_shifts[s]));



array[SHIFT] of var bool: active_shift; 

constraint forall(s in SHIFT)(active_shift[s] = (length[s] > 0));



%  cumulative(array [int] of var int: s,  # start_at
%                      array [int] of var int: d, # length
%                      array [int] of var int: r, # seria lo q necesita q debe ser siempre menor o igual a b -> aca pongo 1 y en b dejo un poco mas q la demanda
%                      var int: b)
% No sirve, inclusive si tomo solo los activos en t, entonces el length no me sirve para nada porque en t+1 tengo un differente b.


% non overlap? #-> diffn expects arrays of int and not arrays of opt int!!!! -> if i fix the types of shifts I could use it, and transform it to a packing problem.




