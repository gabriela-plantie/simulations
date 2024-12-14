int: min_len;
int: max_len;
int: times;

set of int: TIME = 1..times;
array[TIME] of int: rider_demand; 

%int: max_shift;


set of int: TIME_PLUS = 1..times+1;
set of int: LENGTH = {0} union min(min_len, times)..min(max_len, times);
set of int: DEMAND = 1..max(rider_demand);


int: max_shift = ceil(max(t in TIME)(rider_demand[t]) * ceil(times/min_len));
        
set of int: SHIFT = 1..max_shift;
set of int: SHIFT_0 = 0..max_shift;



set of int: SLACK = -max(rider_demand)..max(rider_demand);


array[SHIFT] of var TIME_PLUS: starts_at; 
array[SHIFT] of var LENGTH: length; 

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
	if (length[s] > 0) then
		(starts_at[s] + length[s] - 1 <= times)
		else starts_at[s] = times+1 
		endif );


constraint forall(s in SHIFT) (
	((length[s] == 0) <-> (starts_at[s] == times + 1))	
	);




% symmetry breaking

% all non used shifts at the end
constraint forall(s in 1..max_shift-1)(
    (length[s] = 0) -> (
    	(length[s+1] = 0) /\ (starts_at[s+1] = times+1) /\ (starts_at[s] = times+1)
    	
    	)
);


% starts should be ordered
% constraint forall(i in 1..max_shift-1)(
% 	starts_at[i] <= starts_at[i+1]
% 	);

% % if shifts start at same time, their length should be ordered
% constraint forall(i, j in SHIFT where i < j)(
%     (if starts_at[i] == starts_at[j] then length[i] >= length[j] endif)
% );

% sorting first by longest 
constraint forall(i in 1..max_shift-1)(
	length[i] >= length[i+1]
	);



% if shifts same len, their length should be ordered by start
constraint forall(i, j in SHIFT where i < j)(
    (if length[i] == length[j] then starts_at[i] <= starts_at[j] endif)
);



constraint active_shifts = sum(s in SHIFT)(length[s] > 0);
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
	) then ((length[i] == 2) /\ (length[i+1] == 2))
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





% mal , para 3 dim

%array[TIME, DEMAND] of var SHIFT_0: active_s_at_t;
% include "globals.mzn";
% constraint forall(t in TIME)(all_different_except_0([active_s_at_t[t,s] | s in SHIFT])); % no reduce tiempos


% constraint forall(t in TIME)(
% 			forall(d in DEMAND)( 
% 			forall(s in SHIFT)(
% 			active_s_at_t[t, d] = s <-> (
% 				(starts_at[s] <= t) 
% 				/\ 
% 				(starts_at[s] + length[s] - 1 >= t)
% 				)
% 			)
% 		));  % en que d?????
		
		
% constraint forall(t in TIME)(
% 	active_riders_at_t[t] =
% 		sum(	d in DEMAND)(active_s_at_t[t, d] > 0));

% constraint forall(t in TIME)(
% 			forall(d in DEMAND)(
% 				forall (s in SHIFT)(
% 					if (
% 					(length[s] == length[s+1]) /\ 
% 					(starts_at[s] == starts_at[s+1]) /\
% 					%(starts_at[s] == t) /\
% 					length[s] > 0
% 					)
% 					then active_s_at_t[t,d] < active_s_at_t[t,d+1] endif
% 					)
% 				)
% 			); % rompe test

