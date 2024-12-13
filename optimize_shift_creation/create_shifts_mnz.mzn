int: min_len;
int: max_len;
int: times;

set of int: TIME = 1..times;
array[TIME] of int: rider_demand; 

%int: max_shift;


set of int: TIME_PLUS = 1..times+1;
set of int: LENGTH = {0} union min_len..max_len;



int: max_shift = ceil(max(t in TIME)(rider_demand[t]) * times /min_len);
        
set of int: SHIFT = 1..max_shift;



set of int: SLACK = -max(rider_demand)..max(rider_demand);


array[SHIFT] of var TIME_PLUS: starts_at; 
array[SHIFT] of var LENGTH: length; 

array[TIME] of var int: active_riders_at_t;
array[TIME] of var SLACK: slack; 
var 0..max_shift: active_shifts;
var 0..max(rider_demand)*times: slack_sum;





% in each time sum shifts covering 
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


% prioritize longer shifts



% symmetry breaking

% starts should be ordered
constraint forall(i in 1..max_shift-1)(
	starts_at[i] <= starts_at[i+1]
	);

% all non used shifts at the end
constraint forall(s in 1..max_shift-1)(
    (length[s] = 0 -> length[s+1] = 0)
);


% if shifts start at same time, their length should be ordered
constraint forall(i, j in SHIFT where i < j)(
    (if starts_at[i] == starts_at[j] then length[i] <= length[j] endif)
);


constraint active_shifts = sum(s in SHIFT)(length[s] > 0);
constraint slack_sum = sum(t in TIME)(abs(slack[t]));




solve minimize slack_sum * (max_shift +1) + active_shifts;
