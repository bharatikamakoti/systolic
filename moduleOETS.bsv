//Odd-Even transposition Sort
//Systolic Linear Array Architecture
//Author: K.Bharati, IIITDM KANCEEPURAM
//Date: May 2018

package moduleOETS;

// ================================================================
// Project imports

import Vector         :: *;


typedef 44 NUM_ELEMENTS;

// ================================================================
// Algorithm flow for the Odd-Even transposition sort:

// In every odd step, every (2i-1)th and (2i)th element are compared and swapping takes place
// if the number at the even index is lesser than the number at the odd index.
// In every even step, every (2i)th and (2i+1)th element are compared and swapping takes place
// if the number at the odd index is lesser than the number at the even index.
// This takes place till the array is sorted in an ascending fashion. 
// Each comparison and conditional swapping is performed by a sortEngine

// ================================================================
// Interface for the Odd-Even transposition sort module

interface OETSort_IFC;
   method Action start( Int#(32) j);
   method Action finishload();
   method Action completesort();
   method int getsortvalue();
endinterface

// ================================================================
// Odd-even transposition sort module (defined)

(* synthesize *)
module mkOETsort (OETSort_IFC);

//For the proposed parallel sorting algorithm

//We can use a step counter. For a fact, we know that given N elements, the sort takes
//place in "atmost" in N steps

	

	//This register holds the number of elements to be sorted which
	//is equal to the number of processing elements in the 1D systolic array

	Reg#(Int#(32)) rg_sc <- mkReg (0);
       	
	// NUM_ELEMENTS registers to hold the values to be sorted.
	// One element per PE of the 1D systolic array
        
   	Vector#(NUM_ELEMENTS,Reg#(Int#(32))) arr <- replicateM( mkRegU );
        Reg#(Int#(32)) step <- mkReg(1);

// ================================================================
// Rules

// After step 1, the Odd-even transposition Sort starts
// At every step, the rg_sc is decremented which helps in
// identifying whether the step is an odd step or an even step
// and also the end of all steps.

//Rule 1
rule inc_count ( (step == 2) && (rg_sc < fromInteger(valueof(NUM_ELEMENTS))) );		
	rg_sc <= rg_sc + 1;
endrule

(* descending_urgency = " ro_swap, re_swap, swap_out"*)
//Rule 2.1: Odd step sort
 
rule ro_swap( (rg_sc %2 == 0) && (step == 2) );

	for (Bit#(32) i=1; i< fromInteger (valueof(NUM_ELEMENTS))-1; i=i+2) 
		if(arr[i] > arr[i+1]) begin
                	arr[i] <= arr[i+1]; arr[i+1] <= arr[i]; 
			
		end
       
endrule

//Rule 2.2 Even step sort

rule re_swap ( (rg_sc % 2 == 1) && (step ==2));
	for (Bit#(32) i=0; i<= fromInteger (valueof(NUM_ELEMENTS))-2; i=i+2) 
		if(arr[i] > arr[i+1]) begin
                	arr[i] <= arr[i+1]; arr[i+1] <= arr[i]; 
			
		end
endrule

//Rule 3
rule swap_out (step == 3);
	 for (Int#(32) k = 0; k < fromInteger(valueof(NUM_ELEMENTS))-1; k = k+1)
             arr[k] <= arr[k+1];

endrule

// ================================================================

// Interfaces

//The start method is called NUM_ELEMENTS times by the Tb
//Each time, it accepts an integer and shifts it into the systolic array

   method Action start(Int#(32) j) if (step==1); 
        arr[0] <= j; 
        for (Int#(32) k = 0; k < fromInteger(valueof(NUM_ELEMENTS))-1; k = k+1)
             arr[k+1] <= arr[k];
   endmethod
   
//This method is triggered by the Tb when the last element of inp_arr 
//is loaded into the 1D systolic array

   method Action finishload();
        step <= 2;
        endmethod

   method Action completesort() if(rg_sc==fromInteger(valueof(NUM_ELEMENTS)));
   	step <= 3;
   endmethod

   method int getsortvalue();
   	return arr[0];
   endmethod




endmodule: mkOETsort

// ================================================================

endpackage: moduleOETS








