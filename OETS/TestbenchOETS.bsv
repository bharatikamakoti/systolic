//Odd-Even transposition Sort
//Systolic Linear Array Architecture
//Author: K.Bharati, IIITDM KANCEEPURAM
//Date: May 2018

package TestbenchOETS;

// ================================================================
// Project imports

import Vector         :: *;
import moduleOETS     :: *;
import LFSR           :: *;

typedef 44 NUM_ELEMENTS;

(* synthesize *)

module mkTestbench (Empty); //Empty since it is the top module
	OETSort_IFC m <- mkOETsort ();
	
LFSR #(Bit #(32)) myrand <- mkLFSR_32;
Vector #(NUM_ELEMENTS,Reg#(Int#(32))) inp_arr <- replicateM(mkRegU);
Vector #(NUM_ELEMENTS,Reg#(Int#(32))) out_arr <- replicateM(mkRegU);
Reg#(Bool) mystart <- mkReg(False);
Reg#(Int#(32)) count <- mkReg(0);
Reg#(Bool) myFinish <- mkReg(False);
Reg#(Bool) myPrint <- mkReg(False);

(* descending_urgency = "rl_inp, r1_go, rl_finish, rl_dump, rl_print "*)

//This rule assigns the values for inp_arr and makes mystart <= True.

rule rl_inp( !mystart);
	 inp_arr[0] <= unpack(myrand.value()); 
	 myrand.next();
	 mystart <= True;

endrule

//This rule starts after rl_inp. It pushes the inp_arr values one by one 
//into the 1D systolic array and while pushing the last element, it triggers
//the finishload method indicating to the !D array that it has finished loading.

//Rule 1
rule r1_go ( (mystart) && (count < fromInteger(valueof(NUM_ELEMENTS))));
	
	m.start(inp_arr[count]);
	inp_arr[count+1] <= unpack(myrand.value());
	myrand.next();
	count <= count + 1;
	if (count == fromInteger(valueof(NUM_ELEMENTS))-1) m.finishload();
endrule

//Rule 2
rule rl_finish(!myFinish);
	m.completesort();
	$display("The unsorted sequence is : ");
	for(Integer i=0; i < fromInteger (valueof(NUM_ELEMENTS)); i=i+1)
		$display ("%d ",inp_arr[i]); 
	myFinish <= True;
	count <=0;
	
endrule

//Rule 3
rule rl_dump ( (myFinish) && (count < fromInteger(valueof(NUM_ELEMENTS))));
	
	out_arr[count] <= m.getsortvalue();
	count <= count + 1;
	if (count == fromInteger(valueof(NUM_ELEMENTS))-1) myPrint <= True;
	
endrule

//Rule 4
rule rl_print (myPrint);

	$display("The Sorted sequence is : ");
	for(Integer i=0; i < fromInteger (valueof(NUM_ELEMENTS)); i=i+1)
		$display ("%d ",out_arr[i]); 
	$finish;

endrule

endmodule: mkTestbench

// ================================================================

endpackage: TestbenchOETS
