int: min_len;
int: max_len;
int: times;

set of int: TIME = 1..times;
array[TIME] of int: rider_demand; 

%int: max_shift;



set of int: LENGTH = min(min_len, times)..min(max_len, times);
set of int: DEMAND = 1..max(rider_demand);


int: max_shift = ceil(max(t in TIME)(rider_demand[t]) * ceil(times/min_len));
        
set of int: QSHIFT = 0..max_shift;

set of int: SLACK = -max(rider_demand)..max(rider_demand);


array[TIME, LENGTH] of var QSHIFT: q_shifts; 

array[TIME] of var 0..max(rider_demand): active_riders_at_t;
array[TIME] of var SLACK: slack; 




var 0..max_shift: active_shifts;
var 0..max(rider_demand)*times: slack_sum;


constraint forall(t in TIME)( 
	active_riders_at_t[t] = sum(i in 1..t, l in LENGTH)(if i + l - 1 >= t then q_shifts[i,l] else 0 endif ));
	
		
constraint active_shifts = sum(t in TIME, l in LENGTH)(q_shifts[t,l]);
				
constraint forall(t in TIME)(
		rider_demand[t] =  active_riders_at_t[t] + slack[t] 
		);
		

constraint slack_sum = sum(t in TIME)(abs(slack[t]));



%constraint starts_at[1] = 1;
	


solve minimize slack_sum * (max_shift + 1) + active_shifts;



