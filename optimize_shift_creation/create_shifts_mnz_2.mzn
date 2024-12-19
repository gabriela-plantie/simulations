int: min_len;
int: max_len;
int: times;

set of int: TIME = 1..times;
array[TIME] of int: rider_demand; 

%int: max_shift;



set of int: LENGTH = min(min_len, times)..min(max_len, times);
set of int: DEMAND = 1..max(rider_demand);


int: max_shift = ceil(max(t in TIME)(rider_demand[t]) * ceil(times/min_len));
        
set of int: QSHIFT = 0..max(rider_demand);

set of int: SLACK = -max(rider_demand)..max(rider_demand);


array[TIME, LENGTH] of var QSHIFT: q_shifts; 

array[TIME] of var 0..max(rider_demand): active_riders_at_t;
array[TIME] of var SLACK: slack; 




var 0..max_shift: active_shifts;
var 0..max(rider_demand)*times: slack_sum;


constraint forall(t in TIME)( 
	active_riders_at_t[t] = sum(i in 1..t, l in LENGTH)(if i + l - 1 >= t then q_shifts[i,l] else 0 endif)
	);

	
constraint forall(t in TIME, l in LENGTH)(q_shifts[t, l] <= rider_demand[t] * 1.2);	 % upper bound

constraint forall(t in TIME)(active_riders_at_t[t] <= rider_demand[t] * 1.2);	 % upper bound
constraint forall(t in TIME)(active_riders_at_t[t] >= rider_demand[t] * 0.8);	% lower bound  % solo no ayuda
				
constraint active_shifts = sum(t in TIME, l in LENGTH)(q_shifts[t,l]);
				
constraint forall(t in TIME)(
		rider_demand[t] =  active_riders_at_t[t] + slack[t] 
		);
		
		
constraint forall(t in TIME, l in LENGTH)(if t + l - 1 > times then q_shifts[t, l] = 0 endif);


constraint slack_sum = sum(t in TIME)(abs(slack[t]));



% dominance

% for 2 in len
constraint if min_len < 2  /\ 2 <= max_len  then
	forall (t in 1..times-2)(sum(i in t..t+2)(q_shifts[t, 1] > 0 ) < 2) % cannot be 2 consecutive 1
					endif;
					
% for 3 in len
constraint if min_len < 3  /\ 3 <= max_len  then
	forall (t in 1..times-3)(sum(i in t..t+3)(q_shifts[t, 1] > 0 ) < 3) % cannot be 3 consecutive 1
	/\
	forall (t in 1..times-3)(sum(i in t..t+2)(bool2int(q_shifts[t, 1] > 0) + bool2int(q_shifts[t+1, 2] > 0) ) < 2) % also cannot be  1,2 
	/\
	forall (t in 1..times-3)(sum(i in t..t+2)(bool2int(q_shifts[t, 2] > 0) + bool2int(q_shifts[t+1, 1] > 0) ) < 2) % also cannot be  2,1 
					endif;

% for 4 in len
constraint if min_len < 4  /\ 4 <= max_len then
	forall (t in 1..times-4)(sum(i in t..t+4)(q_shifts[t, 1] > 0 ) < 4) % cannot be 4 consecutive 1
	/\
	forall (t in 1..times-2)(sum(i in t..t+2)(q_shifts[t, 2] > 0 ) < 4) % cannot be 2 consecutive 2
					endif;
					
constraint if min_len < 5  /\ 5 <= max_len then
	forall (t in 1..times-5)(sum(i in t..t+5)(q_shifts[t, 1] > 0 ) < 5)
					endif;


% sum of length of consecutive shifts > max len (since I am prioritizing longer shifts)
constraint forall(t in 1..times-1)(
		forall (l1, l2 in LENGTH)(
			if q_shifts[t, l1] > 0 /\ q_shifts[t+l1, l2] > 0 
			then l1 + l2 > max_len
			endif)
			);


constraint forall(t in 1.. times-1)(
	forall(l1, l2 in LENGTH)(
		if q_shifts[t, l1] > 0 /\ q_shifts[t+l1, l2] > 0 then l1 >= l2 endif )
		);
		
		
		
% si puede ser lent=6, lent+1=4 o lent=7, lent+1=3 -> 7,3
constraint forall(t in 1.. times-1)(
	forall(l1, l2 in LENGTH)(
		if q_shifts[t, l1] > 0 /\ q_shifts[t+l1, l2] > 0 /\ l1 + l2 == max_len + min_len 
		then l1 = max_len /\ l2 = min_len endif )
		);

% constraint starts_at[1] = 1;
	
% casos de simetria para resolver
% 10 times , always 100 demand, shifts 3..7 -> of len 7 and 3 at 1 and 7 or of len 5 at 1 and 5    
% hacer una variable en que t estan las longitudes -> set lengths_in_t
% longitudes de suvesivos van decreciendo o son iguales





solve minimize slack_sum * (max_shift + 1) + active_shifts;



